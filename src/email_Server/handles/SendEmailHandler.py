import json
import smtplib
import ssl
from datetime import datetime
from typing import Dict, Any, Sequence
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path

from mcp.types import TextContent
from mcp import Tool
from base_Mcp_Handles import BaseHandler
from   ..config.dbconfig import get_config
import pymysql


class SendEmailHandler(BaseHandler):
    name = "send_email"
    tool_Prompt = "发生草稿中编辑好(存在的邮件)到指定的邮箱"

    config: Dict[str, str] = {}

    def get_config(self) -> Dict[str, Any]:
        # 读取全局配置（数据库、SMTP 等）
        self.config = get_config()
        return self.config


    def connect_db(self):
        # 连接 MySQL 数据库
        cfg = self.get_config()
        return pymysql.connect(
            host=cfg["DB_HOST"],
            port=int(cfg["DB_PORT"]),
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_DATABASE"],
            charset=cfg["DB_CHARSET"]
        )

    def get_smtp(self):
        # 返回 SMTP 配置信息
        cfg = self.get_config()
        return {
            "host": cfg["SMTP_HOST"],
            "port": int(cfg["SMTP_PORT"]),
            "user": cfg["EMAIL_USER"],
            "password": cfg["EMAIL_PASSWORD"]
        }

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:


    def get_tool_description(self) -> Tool:
        # 定义参数结构，供 MCP 系统识别
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "草稿 ID"}
                },
                "required": ["id"]
            }
        )

