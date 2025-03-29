# PostgreSQL API

这是一个使用FastAPI和SQLAlchemy构建的PostgreSQL数据库操作API。

## 功能特点

- 完整的CRUD操作
- 使用SQLAlchemy ORM
- 自动API文档
- 环境变量配置
- 类型提示和验证

## 安装步骤

1. 克隆项目到本地
2. 项目运行环境管理，需要安装好pyenv，poetry
3. 创建并配置好虚拟环境：
   ```bash
   poetry install --no-dev

4. 复制`cp .env.example .env`文件并配置数据库连接信息：
   ```
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_SERVER=your_server
   POSTGRES_PORT=5432
   POSTGRES_DB=your_database
   ```

## 运行应用

```bash
uvicorn main:app --reload
```

## API端点

- POST /users/ - 创建新用户
- GET /users/ - 获取用户列表
- GET /users/{user_id} - 获取特定用户
- PUT /users/{user_id} - 更新用户
- DELETE /users/{user_id} - 删除用户

## 部署到Ubuntu服务器

1. 使用systemd服务运行应用：
   ```bash
   sudo nano /etc/systemd/system/postgres-api.service
   ```
   
   添加以下内容：
   ```
   [Unit]
   Description=PostgreSQL API
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/api_lib/api_postgres_sql
   Environment="PATH=/api_lib/api_postgres_sql/.venv/bin"
   ExecStart=/api_lib/api_postgres_sql/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

2. 启动服务：
   ```bash
   sudo systemctl start postgres-api
   sudo systemctl enable postgres-api
   ```

