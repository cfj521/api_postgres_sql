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
2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   .\venv\Scripts\activate  # Windows
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 创建`.env`文件并配置数据库连接信息：
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

访问 http://localhost:8000/docs 查看API文档

## API端点

- POST /users/ - 创建新用户
- GET /users/ - 获取用户列表
- GET /users/{user_id} - 获取特定用户
- PUT /users/{user_id} - 更新用户
- DELETE /users/{user_id} - 删除用户

## 部署到Ubuntu服务器

1. 在服务器上安装必要的包：
   ```bash
   sudo apt update
   sudo apt install python3-venv postgresql postgresql-contrib
   ```

2. 配置PostgreSQL：
   ```bash
   sudo -u postgres psql
   CREATE DATABASE your_database;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE your_database TO your_username;
   ```

3. 使用systemd服务运行应用：
   ```bash
   sudo nano /etc/systemd/system/postgres-api.service
   ```
   
   添加以下内容：
   ```
   [Unit]
   Description=PostgreSQL API
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/your/project
   Environment="PATH=/path/to/your/project/venv/bin"
   ExecStart=/path/to/your/project/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

4. 启动服务：
   ```bash
   sudo systemctl start postgres-api
   sudo systemctl enable postgres-api
   ```

5. 配置Nginx（可选）：
   ```bash
   sudo apt install nginx
   sudo nano /etc/nginx/sites-available/postgres-api
   ```

   添加以下内容：
   ```
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. 启用站点：
   ```bash
   sudo ln -s /etc/nginx/sites-available/postgres-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ``` 