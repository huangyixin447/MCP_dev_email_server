from typing import Dict, Any, Sequence
from mcp.types import TextContent
from mcp import Tool
from email_Server.handles.base_Mcp_Handles import BaseHandler
import imaplib
import email
from email.header import decode_header
from email_Server.config.dbconfig import get_config
"""
根据uid查询邮件的全部内容

"""

class QueryQQEmailByUIDHandler(BaseHandler):
    name = "query_qq_email_by_uid"
    tool_prompt = "根据 UID 查询 QQ 邮箱邮件内容"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "description": "邮件 UID"}
                },
                "required": ["uid"]
            }
        )

    def get_imap_connection(self):
        cfg = get_config()
        mail = imaplib.IMAP4_SSL(cfg["IMAP_HOST"])
        mail.login(cfg["EMAIL_USER"], cfg["EMAIL_PASSWORD"])
        return mail

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        from email.utils import parsedate_to_datetime
        from html2text import html2text
        from datetime import datetime

        uid = arguments["uid"]
        mail = self.get_imap_connection()
        mail.select("INBOX")
        print("📬 成功连接 QQ 邮箱 INBOX")
        typ, msg_data = mail.fetch(uid.encode(), "(RFC822)")

        if typ != "OK":
            mail.logout()
            return [TextContent(type="text", text=" 无法检索邮件")]

        raw_email = msg_data[0][1]
        message = email.message_from_bytes(raw_email)

        def decode_mime(s):
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

        subject_raw = message.get("Subject", "")
        subject = decode_mime(subject_raw)
        sender = decode_mime(message.get("From", ""))
        to = decode_mime(message.get("To", ""))
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

        full_text = html2text(body)

        result = f"""UID: {uid}
主题: {subject}
发件人: {sender}
收件人: {to}
时间: {local_time}
正文内容:
{full_text}
"""

        mail.logout()
        return [TextContent(type="text", text=result)]