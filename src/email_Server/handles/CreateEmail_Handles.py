import json
import uuid
from datetime import datetime
from typing import Dict, Any, Sequence

import pymysql
from  mcp.types import  TextContent
from  mcp import  Tool
from  email_Server.handles.base_Mcp_Handles import BaseHandler
from   email_Server.config.dbconfig import get_config

"""邮箱草稿"""

class CreateEmailHandles(BaseHandler):
    #工具名称
    name = "create_email"
    # 提示词
    tool_Prompt = "创建邮件草稿,并且存储到mysql5的数据库中"

    config: Dict[str, str]={}

    def get_config(self) -> Dict[str, Any]:
        self.config=get_config()
        return  self.config
# 获取数据库连接
    def connect_db(self):
        if not self.config:
            self.get_config()  # 确保先加载配置
        host=self.config["DB_HOST"]
        port=int(self.config["DB_PORT"])
        user=self.config["DB_USER"]
        password=self.config["DB_PASSWORD"]
        database=self.config["DB_DATABASE"]
        charset=self.config["DB_CHARSET"]

        DB_CONFIG={
            "host": host,
            "port":port ,
            "user": user,
            "password": password,
            "database": database,
            "charset": charset
        }
        return  pymysql.connect(**DB_CONFIG)







    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        conn = self.connect_db()
        cur = conn.cursor()
        mail_id = str(uuid.uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
                    INSERT INTO email_record (id, `to`, subject, body, status, attachments, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, 'draft', %s, %s, %s)
                """, (
            mail_id, arguments['to'], arguments.get('subject', ''), arguments.get('body', ''),
            json.dumps(arguments.get('attachments', [])), now, now
        ))
        conn.commit()
        conn.close()
        return [TextContent(type="text", text=f" 创建成功 ID: {mail_id}")]
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "attachments": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["to"]
            }
        )
