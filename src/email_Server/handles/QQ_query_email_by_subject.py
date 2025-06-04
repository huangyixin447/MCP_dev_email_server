from typing import Dict, Any, Sequence
from mcp.types import TextContent
from mcp import Tool
from email_Server.handles.base_Mcp_Handles import BaseHandler
import imaplib
import email
from email.header import decode_header
from email_Server.config.dbconfig import get_config


class QueryQQEmailBySubjectHandler(BaseHandler):

    name = "query_qq_email_by_subject"
    tool_Prompt = "根据标题模糊查询QQ邮箱中的邮件"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "邮件标题关键词"}
                },
                "required": ["keyword"]
            }
        )


    def get_imap_connection(self):
        cfg = get_config()
        mail = imaplib.IMAP4_SSL(cfg["IMAP_HOST"])
        mail.login(cfg["EMAIL_USER"], cfg["EMAIL_PASSWORD"])
        return mail

    def decode_mime(self, s):
        parts = decode_header(s)
        decoded = []
        for part, enc in parts:
            if isinstance(part, bytes):
                try:
                    if not enc or (enc and enc.lower() in ["unknown-8bit", "8bit", "x-unknown"]):
                        decoded.append(part.decode("utf-8", errors="replace"))
                    else:
                        decoded.append(part.decode(enc, errors="replace"))
                except Exception:
                    decoded.append(part.decode("utf-8", errors="replace"))
            else:
                decoded.append(part)
        return ''.join(decoded)

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        from email.utils import parsedate_to_datetime
        from html2text import html2text
        from datetime import datetime
        keyword = arguments["keyword"]
        mail = self.get_imap_connection()
        mail.select("INBOX")
        print("📬 成功连接 QQ 邮箱 INBOX")
        typ, data = mail.search(None, "ALL")

        print(f"🔍 搜索结果状态: {typ}, 邮件数量: {len(data[0].split())}")

        if typ != "OK":
            return [TextContent(type="text", text=" 无法检索邮件")]

        email_ids = data[0].split()
        recent_ids = email_ids[:50]  # 只查询前 100 封邮件

        results = []
        for uid in recent_ids:
            print(f"📨 正在检查邮件 UID: {uid.decode()}")
            typ, msg_data = mail.fetch(uid, "(RFC822)")
            if typ != "OK":
                continue
            raw_email = msg_data[0][1]
            message = email.message_from_bytes(raw_email)
            subject_raw = message.get("Subject", "")
            subject = self.decode_mime(subject_raw)
            print(f"🎯 邮件 UID: {uid.decode()}, 标题: {subject}")
            # subject = self.decode_mime(subject_raw)  # 已在上方赋值，避免重复
            if keyword.strip().lower() in subject.strip().lower():
                print(f"✅ 匹配成功，标题: {subject}")
                sender = self.decode_mime(message.get("From", ""))
                to = self.decode_mime(message.get("To", ""))
                date_str = message.get("Date", "")
                try:
                    date_obj = parsedate_to_datetime(date_str)
                    if date_obj:
                        local_time = datetime.fromtimestamp(date_obj.timestamp()).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        local_time = date_str
                except Exception:
                    local_time = date_str

                # 提取正文
                body = ""
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "text/plain" and not part.get_filename():
                            charset = part.get_content_charset() or "utf-8"
                            body = part.get_payload(decode=True).decode(charset, errors="replace")
                            break
                else:
                    charset = message.get_content_charset() or "utf-8"
                    body = message.get_payload(decode=True).decode(charset, errors="replace")

                snippet = html2text(body)[:150]

                results.append(f"""UID: {uid.decode()}
主题: {subject}
发件人: {sender}
收件人: {to}
时间: {local_time}
正文摘要:
{snippet}
""")

        mail.logout()

        if not results:
            print("⚠️ 未找到任何匹配的邮件")
            return [TextContent(type="text", text=" 未找到匹配的邮件")]
        return [TextContent(type="text", text="\n\n".join(results))]