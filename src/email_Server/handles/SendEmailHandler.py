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
from email_Server.handles.base_Mcp_Handles import BaseHandler
from   email_Server.config.dbconfig import get_config
import pymysql
"""
测试成功
"""

class SendEmailHandler(BaseHandler):
    name = "send_email"
    tool_Prompt = "将本地草稿中编辑好(存在的邮件)到指定的邮箱"

    config: Dict[str, str] = {}

    def get_config(self) -> Dict[str, Any]:
        # 读取全局配置（数据库、SMTP 等）
        self.config = get_config()
        return self.config


    def connect_db(self)->pymysql.connect:
        if not self.config:
            self.get_config()  # 确保先加载配置
        # 连接 MySQL 数据库
        cfg = self.config
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
        # 获取草稿 ID 和目标邮箱
        mail_id = arguments["id"]
        target_email = arguments.get("target_email")

        # 数据库连接
        conn = self.connect_db()
        cur = conn.cursor()

        # 查询草稿数据
        cur.execute(
            "SELECT `to`, subject, body, attachments FROM email_record WHERE id = %s AND status = 'draft'",
            (mail_id,)
        )
        # 检查是否查找到草稿
        row = cur.fetchone()

        if not row:
            conn.close()
            return [TextContent(type="text", text=" 未找到草稿或状态不正确")]

        # 解析字段
        to, subject, body, attachments_json = row
        if target_email:
            to = target_email  # 替换收件人
        attachments = json.loads(attachments_json or "[]")

        from email.utils import formataddr
        smtp_cfg = self.get_smtp()
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = formataddr(('timelock_MCP_server', smtp_cfg['user']))
        msg['To'] = formataddr(('收件人', to))
        msg['Subject'] = subject

        try:
            server = smtplib.SMTP_SSL(smtp_cfg['host'], smtp_cfg['port'])
            server.login(smtp_cfg['user'], smtp_cfg['password'])
            server.sendmail(smtp_cfg['user'], [to], msg.as_string())
            server.quit()
        except Exception as e:
            return [TextContent(type="text", text=f"❌ 邮件发送失败: {str(e)}")]

        # 更新状态为已发送
        cur.execute(
            "UPDATE email_record SET status='sent', updated_at=%s WHERE id=%s",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mail_id)
        )
        conn.commit()
        conn.close()

        return [TextContent(type="text", text="yes 邮件发送成功")]

    def get_tool_description(self) -> Tool:
        # 定义参数结构，供 MCP 系统识别
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "草稿 ID"},
                    "target_email": {"type": "string", "description": "用于替代草稿中的收件人"}
                },
                "required": ["id"]
            }
        )

