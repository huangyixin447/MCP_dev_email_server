from typing import Dict, Any, Sequence
from mcp.types import TextContent
from mcp import Tool
from email_Server.handles.base_Mcp_Handles import BaseHandler
from email_Server.config.dbconfig import get_config
import pymysql
"""
根据草稿状态以及关键字查找本地的邮件记录列表
已测试成功
"""

class ListEmailHandler(BaseHandler):
    name = "list_email"
    tool_Prompt = "查询本地草稿邮件记录列表（支持状态筛选和模糊搜索）"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_Prompt,
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "草稿状态，如 draft/sent/failed"},
                    "keyword": {"type": "string", "description": "可用于模糊匹配收件人或主题"}
                }
            }
        )
    @classmethod
    def connect_db(cls):
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
        status = arguments.get("status")
        keyword = arguments.get("keyword", "")

        conn = self.connect_db()
        cur = conn.cursor()

        # 构建 SQL 语句和参数
        sql = "SELECT id, `to`, subject, status, updated_at FROM email_record WHERE 1=1"
        params = []

        if status:
            sql += " AND status = %s"
            params.append(status)
        if keyword:
            sql += " AND (`to` LIKE %s OR subject LIKE %s)"
            kw = f"%{keyword}%"
            params.extend([kw, kw])

        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return [TextContent(type="text", text=" 没有符合条件的邮件记录")]

        # 格式化输出
        result = "\n\n".join(
            [f"📩 ID: {r[0]}\n收件人: {r[1]}\n主题: {r[2]}\n状态: {r[3]}\n更新时间: {r[4]}" for r in rows]
        )
        return [TextContent(type="text", text=result)]