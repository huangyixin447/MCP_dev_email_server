## 邮件mcp服务使用方法

下载依赖

` pip install -e .`

然后打开.env文件

```env
# 邮件服务器地址
SMTP_HOST=123
# 服务器接口地址
SMTP_PORT=123
#发件账号
EMAIL_USER=123
#授权码
EMAIL_PASSWORD=123
#数据库
DB_HOST=localhost
DB_PORT=11801
DB_USER=root
DB_PASSWORD=123456
DB_DATABASE=email_db
DB_CHARSET=utf8mb4

#邮箱相关配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
EMAIL_USER=2971434037@qq.com
#填写邮件授权码
EMAIL_PASSWORD=
```

按照你自己的信息填写好

按照如下的sql语句建表

```sql
CREATE TABLE IF NOT EXISTS email_record (
    id VARCHAR(36) PRIMARY KEY,
    `to` TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    status ENUM('draft','sent','failed') DEFAULT 'draft',
    attachments TEXT,
    created_at DATETIME,
    updated_at DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

```

邮件授权码请去你自己的qq邮箱中进行申请

 全部配置完毕，终端输入

```
sse_run
```

则会在9000端口运行mcp服务，服务配置为 localhost:9000/see,

配置到你的mcpclient中即可

使用终端输入

```
stdio_run
```

则会在本地运行stdio的mcp服务，

采用类似如下的json配置即可成功，不过不推荐这种方式



```json
{
  "mcpServers": {
      "email_server": {
        "isActive": true,
        "name": "operateMysql",
        "command": "uv",
        "args": [
          "--directory",
          "G:\\python\\mysql_mcp\\src",  # 这里需要替换为你的项目路径
          "run",
          "server.py",
          "--stdio"
        ]
    }
  }
}    
```