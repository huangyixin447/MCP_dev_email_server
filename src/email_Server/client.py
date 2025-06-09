from email_Server.server import main

def stdio_run():
    """stdio 模式入口点"""
    main(mode="stdio")

def sse_run():
    """SSE 模式入口点"""
    main(mode="sse")