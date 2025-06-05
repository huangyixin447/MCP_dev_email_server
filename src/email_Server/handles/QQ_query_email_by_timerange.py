from email_Server.handles.base_Mcp_Handles import BaseHandler
from mcp.types import  TextContent
from mcp import  Tool
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
from email_Server.config import get_config


class QueryQQEmailByTimeRangeHandler(BaseHandler):
    name = "query_qq_email_by_time_range"
    tool_prompt = "根据时间范围查询 QQ 邮箱中的邮件记录，可以查询近期的邮件信息"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "起始日期（格式 YYYY-MM-DD）"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期（格式 YYYY-MM-DD）"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        )

    async def run_tool(self, arguments: dict) -> list[TextContent]:
        print(f"🔍 开始根据时间范围查询邮件：{arguments['start_date']} 至 {arguments['end_date']}")
        cfg = get_config()
        EMAIL_USER = cfg["EMAIL_USER"]
        EMAIL_PASSWORD = cfg["EMAIL_PASSWORD"]
        IMAP_HOST = cfg.get("IMAP_HOST", "imap.qq.com")

        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("INBOX")
        print("✅ 已连接到 QQ 邮箱并选择 INBOX")

        # 格式转换
        start = datetime.strptime(arguments["start_date"], "%Y-%m-%d").replace(tzinfo=None)
        end = (datetime.strptime(arguments["end_date"], "%Y-%m-%d") + timedelta(days=1)).replace(tzinfo=None)

        typ, data = mail.search(None, "ALL")
        print(f"🔍 搜索结果状态: {typ}, 邮件数量: {len(data[0].split())}")
        if typ != "OK":
            return [TextContent(type="text", text=" 无法检索邮件")]
        email_ids = data[0].split()
        results = []

        for uid in reversed(email_ids):
            res, data = mail.fetch(uid, "(RFC822)")
            if res != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])
            date_str = msg.get("Date", "")

            if not date_str:
                # 如果 Date 字段为空，尝试使用 Received 字段提取时间
                received = msg.get_all("Received", [])
                if received:
                    import re
                    match = re.search(r'; (.*)', received[-1])
                    if match:
                        date_str = match.group(1).strip()

            try:
                dt = parsedate_to_datetime(date_str)
                if dt is not None and dt.tzinfo is not None:
                    dt = dt.astimezone(tz=None).replace(tzinfo=None)
            except Exception as e:
                print(f"⚠️ 日期解析失败: {e}, 原始字段: {date_str}")
                dt = None

            if dt is None:
                continue

            if not (start <= dt <= end):
                continue
            if dt < start:
                print(f"🛑 遇到早于起始时间的邮件，停止处理 UID: {uid.decode()}")
                break

            subject, enc = decode_header(msg.get("Subject", ""))[0]
            if isinstance(subject, bytes):
                if not enc or enc.lower() == "unknown-8bit":
                    enc = "utf-8"
                subject = subject.decode(enc, errors="ignore")

            sender = msg.get("From", "")
            local_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            print(f"📧 正在处理 UID: {uid.decode()}，时间: {date_str}")
            print(f"主题: {subject}, 发件人: {sender}, 时间: {local_time}")
            print(f"✅ 匹配成功: UID {uid.decode()}")
            results.append(f"UID: {uid.decode()} | 主题: {subject} | 发件人: {sender} | 时间: {local_time}")

        mail.logout()

        if not results:
            return [TextContent(type="text", text="📭 在指定时间范围内没有找到邮件")]

        print("✅ 查询完成，准备返回结果")
        return [TextContent(type="text", text="\n".join(results))]