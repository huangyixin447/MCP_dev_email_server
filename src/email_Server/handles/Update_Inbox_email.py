import json
from datetime import datetime
from typing import Dict, Any, Sequence
from mcp.types import TextContent
from mcp import Tool
from email_Server.handles.base_Mcp_Handles import BaseHandler
from email_Server.config.dbconfig import get_config
import pymysql


class UpdateEmailHandler(BaseHandler):
    name = "update_email"
    tool_Prompt = "根据指定的id来更新邮件草稿内容"

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

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "草稿 ID"},
                    "to": {"type": "string", "description": "收件人邮箱"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "attachments": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["id"]
            }
        )

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        mail_id = arguments["id"]
        to = arguments.get("to")
        subject = arguments.get("subject")
        body = arguments.get("body")
        attachments = arguments.get("attachments")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.connect_db()
        cur = conn.cursor()

        # 构建 SQL 动态部分
        fields :list[str] = []
        values:list[Any] = []

        if to is not None:
            fields.append("`to` = %s")
            values.append(to)
        if subject is not None:
            fields.append("subject = %s")
            values.append(subject)
        if body is not None:
            fields.append("body = %s")
            values.append(body)
        if attachments is not None:
            fields.append("attachments = %s")
            values.append(json.dumps(attachments))

        if not fields:
            return [TextContent(type="text", text="⚠ 没有需要更新的内容")]

        # 更新字段和时间
        fields.append("updated_at = %s")
        values.append(now)
        values.append(mail_id)

        sql = f"UPDATE email_record SET {', '.join(fields)} WHERE id = %s"

        cur.execute(sql, values)
        conn.commit()
        conn.close()

        return [TextContent(type="text", text=" 草稿内容已更新")]