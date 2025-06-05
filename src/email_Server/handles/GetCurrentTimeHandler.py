from mcp.types import TextContent
from mcp import Tool
from datetime import datetime
from email_Server.handles.base_Mcp_Handles import BaseHandler

# 获取当前时间的工具处理类
class GetCurrentTimeHandler(BaseHandler):
    name = "get_current_time"
    tool_prompt = "获取当前时间"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.tool_prompt,
            inputSchema={"type": "object", "properties": {}}
        )

    async def run_tool(self, arguments: dict) -> list[TextContent]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕒 当前时间为: {now}")
        return [TextContent(type="text", text=f"当前时间是：{now}")]
