from typing import Dict, Any, Sequence
from mcp.types import TextContent
from mcp import Tool
from .base_Mcp_Handles import BaseHandler
import pymysql
import json
from email_Server.config.dbconfig import get_config
"""
根据id获得本地的详细邮件方法
已测试通过！！！！！！！！

"""

class GetLocalDraftEmailDetailHandler(BaseHandler):
    name = "get_local_draft_email_detail"
    tool_Prompt = "根据ID获取本地草稿邮件的详细内容"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "草稿邮件ID"}
                },
                "required": ["id"]
            }
        )

    def connect_db(self):
        cfg = get_config()
        return pymysql.connect(
            host=cfg["DB_HOST"],
            port=int(cfg["DB_PORT"]),
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_DATABASE"],
            charset=cfg["DB_CHARSET"]
        )

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        email_id = arguments["id"]
        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT `to`, subject, body, attachments, status, created_at FROM email_record WHERE id = %s ORDER BY created_at DESC",
            (email_id,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return [TextContent(type="text", text=" 未找到该草稿邮件")]

        to, subject, body, attachments, status, created_at = row
        status_map = {"draft": "草稿", "sent": "已发送", "failed": "发送失败"}
        readable_status = status_map.get(status, status)

        return [TextContent(type="text", text=f"""草稿邮件详情：
- 收件人: {to}
- 创建时间: {created_at}
- 状态: {readable_status}
- 主题: {subject}

正文内容：
{body}
""")]