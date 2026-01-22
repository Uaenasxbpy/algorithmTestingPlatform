# 手动启动指南

## 前提条件检查

请确保您的系统已安装：
- Python 3.8+ 
- Node.js 16+
- MySQL 8.0+

可以通过以下命令检查：
```bash
python --version
node --version
mysql --version
```

## 1. 启动 MySQL 数据库

### 选项 A: 使用本地 MySQL 服务
```bash
# Windows - 启动 MySQL 服务
net start mysql80

# 或通过服务管理器启动 MySQL80 服务
```

### 选项 B: 使用 MySQL Workbench
- 打开 MySQL Workbench
- 连接到本地 MySQL 实例
- 创建数据库：`CREATE DATABASE algorithm_testing;`

### 选项 C: 命令行创建数据库
```bash
# 连接到 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE algorithm_testing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户（可选）
CREATE USER 'alg_test'@'localhost' IDENTIFIED BY 'alg_test123';
GRANT ALL PRIVILEGES ON algorithm_testing.* TO 'alg_test'@'localhost';
FLUSH PRIVILEGES;

# 退出
EXIT;
```

### 导入数据库结构
```bash
# 进入项目目录
cd f:\研1\algorithmTestingPlatform

# 导入数据库结构
mysql -u root -p algorithm_testing < database/schema.sql
```

## 2. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 修改数据库连接配置（如果需要）
# 编辑 app/core/config.py 中的数据库连接信息

# 启动后端服务
python main.py
```

后端将在 http://localhost:8000 启动

## 3. 启动前端服务

```bash
# 打开新的命令窗口，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动前端开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

## 4. 访问应用

- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 故障排除

### 后端启动问题

1. **数据库连接失败**
```bash
# 检查 MySQL 服务状态
sc query mysql80

# 修改配置文件 backend/app/core/config.py
DATABASE_URL = "mysql+pymysql://root:你的密码@localhost:3306/algorithm_testing"
```

2. **端口占用**
```bash
# 检查端口占用
netstat -ano | findstr :8000

# 终止占用进程
taskkill /PID 进程ID /F
```

### 前端启动问题

1. **Node.js 版本过低**
```bash
# 升级 Node.js 到 16+ 版本
# 或使用 nvm 管理多个版本
```

2. **依赖安装失败**
```bash
# 清理缓存重新安装
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 开发建议

1. **使用代码编辑器**
   - 推荐 VS Code 
   - 安装 Python、Vue、TypeScript 扩展

2. **开发工具**
   - 后端调试：可以在 VS Code 中调试 Python
   - 前端调试：使用浏览器开发者工具
   - API测试：访问 http://localhost:8000/docs

3. **代码修改热重载**
   - 后端：uvicorn 自动重载
   - 前端：Vite 热更新