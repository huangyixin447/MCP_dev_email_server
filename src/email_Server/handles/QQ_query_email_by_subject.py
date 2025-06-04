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
    tool_Prompt = "根据标题模糊查询QQ邮箱邮件"

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
        return ''.join([
            part.decode(enc or 'utf-8') if isinstance(part, bytes) else part
            for part, enc in parts
        ])

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        keyword = arguments["keyword"]
        mail = self.get_imap_connection()
        mail.select("inbox")
        typ, data = mail.search(None, "ALL")
        if typ != "OK":
            return [TextContent(type="text", text="❌ 无法检索邮件")]

        results = []
        for uid in data[0].split():
            typ, msg_data = mail.fetch(uid, "(RFC822)")
            if typ != "OK":
                continue
            raw_email = msg_data[0][1]
            message = email.message_from_bytes(raw_email)
            subject_raw = message.get("Subject", "")
            subject = self.decode_mime(subject_raw)
            if keyword.lower() in subject.lower():
                results.append(f"UID: {uid.decode()}\n主题: {subject}")

        mail.logout()

        if not results:
            return [TextContent(type="text", text="🔍 未找到匹配的邮件")]
        return [TextContent(type="text", text="\n\n".join(results))]