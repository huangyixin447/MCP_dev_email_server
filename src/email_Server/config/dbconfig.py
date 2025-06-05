import  os
from  dotenv import  *


# 从环境变量获取数据库配置的信息
def get_db_config():
    load_dotenv()
    config={}
    # 指定.env配置文件的路径
    from  pathlib import Path
    # 填写你env的路径
    default_env_path=Path("'/Users/wzf-perfomancemac/Desktop/mcp/mcp_server_development/MCP_dev_ Test01/.env'")
    # 加载env的默认路径
    load_dotenv(dotenv_path=default_env_path)
    # 加调试输出确认是否加载成功
    print(f"邮件服务器:{os.getenv('SMTP_HOST')}")
    print(f"smtp_port{os.getenv('SMTP_PORT')}")
    print(f"发件账号:{os.getenv('EMAIL_USER')}")
    print(f"授权码:{'yes' if os.getenv('EMAIL_PASSWORD') else 'no'}")

    config["SMTP_HOST"] = os.getenv("SMTP_HOST")
    config["SMTP_PORT"] = os.getenv("SMTP_PORT")
    config["EMAIL_USER"] = os.getenv("EMAIL_USER")
    config["EMAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")
    config["DB_HOST"] = os.getenv("DB_HOST")
    config["DB_PORT"] = os.getenv("DB_PORT")
    config["DB_USER"] = os.getenv("DB_USER")
    config["DB_PASSWORD"] = os.getenv("DB_PASSWORD")
    config["DB_DATABASE"] = os.getenv("DB_DATABASE")
    config["DB_CHARSET"] = os.getenv("DB_CHARSET")
    config["IMAP_HOST"] = os.getenv("IMAP_HOST")
    config["EMAIL_MAX"]=os.getenv("EMAIL_MAX")


    required_keys = ["SMTP_HOST", "SMTP_PORT", "EMAIL_USER", "EMAIL_PASSWORD", "DB_HOST","DB_USER","DB_PASSWORD","DB_DATABASE","DB_CHARSET","DB_PORT"]
    for key in required_keys:
        if not config.get(key):
            raise ValueError(f"❌ 缺少必要的配置项: {key}")
    return  config

# 返回配置文件
def  get_config()->type[dict[str:str]]:
    config=get_db_config()

    return  config




if __name__ == '__main__':
    print(get_config())



