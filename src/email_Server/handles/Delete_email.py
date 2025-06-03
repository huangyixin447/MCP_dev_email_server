from typing import Dict, Any, Sequence
from mcp.types import TextContent
from mcp import Tool
from email_Server.handles.base_Mcp_Handles import BaseHandler
from email_Server.config.dbconfig import get_config
import pymysql

"""
根据id删除指定邮件，
已测试

"""

class DeleteEmailHandler(BaseHandler):
    name = "delete_email"
    tool_Prompt = "根据 ID 删除本地草稿邮件"

    config: Dict[str, str] = {}

    def get_config(self) -> Dict[str, Any]:
        self.config = get_config()
        return self.config

    def connect_db(self):
        cfg = self.get_config()
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

        # 可选逻辑：只允许删除草稿状态的邮件
        cur.execute("DELETE FROM email_record WHERE id = %s AND status = 'draft'", (email_id,))
        affected_rows = cur.rowcount

        conn.commit()
        conn.close()

        if affected_rows == 0:
            return [TextContent(type="text", text=" 未找到草稿或草稿已发送，无法删除")]
        return [TextContent(type="text", text="🗑️ 草稿已删除")]

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "邮件草稿 ID"}
                },
                "required": ["id"]
            }
        )