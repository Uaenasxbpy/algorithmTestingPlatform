# Docker 启动故障排除指南

## 🚨 常见问题解决方案

### 问题1: `docker-compose up -d` 命令卡住

#### 可能原因：
1. **Docker Desktop 还在初始化**
2. **网络问题导致镜像下载缓慢**
3. **系统资源不足**
4. **防火墙阻止**

#### 解决步骤：

##### 步骤1: 确认 Docker 状态
```bash
# 运行 Docker 状态检查
check_docker.bat
```

##### 步骤2: 手动检查 Docker
```bash
# 检查 Docker 是否正常运行
docker info

# 测试 Docker 基本功能
docker run --rm hello-world
```

##### 步骤3: 清理并重新启动
```bash
# 停止所有相关容器
docker-compose down --remove-orphans

# 清理未使用的镜像和容器
docker system prune -f

# 使用新的启动脚本
docker-start.bat
```

##### 步骤4: 分步启动（如果仍然卡住）
```bash
# 只启动数据库
docker-compose up -d mysql

# 等待30秒后启动后端
docker-compose up -d backend

# 再等待15秒后启动前端
docker-compose up -d frontend
```

### 问题2: 镜像构建失败

#### 解决方案：
```bash
# 清理构建缓存
docker builder prune -f

# 重新构建（无缓存）
docker-compose build --no-cache

# 如果网络问题，可以手动下载基础镜像
docker pull python:3.9-slim
docker pull node:18-alpine
docker pull mysql:8.0
```

### 问题3: 端口冲突

#### 检查端口占用：
```bash
# Windows 检查端口
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# 如果端口被占用，终止进程或修改端口
```

#### 修改端口（编辑 docker-compose.yml）：
```yaml
ports:
  - "3001:80"  # 前端改为3001
  - "8001:8000" # 后端改为8001
  - "3307:3306" # MySQL改为3307
```

### 问题4: 资源不足

#### 增加 Docker 资源：
1. 打开 Docker Desktop
2. 进入 Settings → Resources
3. 增加：
   - Memory: 至少 4GB
   - CPU: 至少 2 cores
   - Disk: 至少 2GB

### 问题5: 网络问题

#### 解决方案：
```bash
# 使用国内镜像源（编辑 Dockerfile）
# 在 Python Dockerfile 中添加：
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 在 Node.js Dockerfile 中添加：
RUN npm config set registry https://registry.npm.taobao.org
```

## 🔧 立即可用的替代方案

如果 Docker 问题持续存在，请使用以下方案：

### 方案A: 手动启动（推荐）
```bash
# 运行启动脚本
start.bat

# 选择 "3. 启动完整服务"
```

### 方案B: 系统检查
```bash
# 运行完整系统检查
python test_system.py
```

### 方案C: 分别启动
```bash
# 后端
cd backend
pip install -r requirements.txt
python main.py

# 前端（新窗口）
cd frontend
npm install  
npm run dev
```

## 📝 调试技巧

### 查看详细日志：
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

### 检查容器状态：
```bash
# 查看运行中的容器
docker-compose ps

# 查看系统资源使用
docker stats
```

### 进入容器调试：
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec mysql mysql -u root -p
```

## 🎯 快速恢复

如果遇到任何问题，最快的解决方案：

1. **停止 Docker 服务**：
   ```bash
   docker-compose down --remove-orphans
   ```

2. **使用手动启动**：
   ```bash
   start.bat
   ```

3. **访问应用**：
   - http://localhost:3000 (前端)
   - http://localhost:8000 (后端)

这样可以绕过 Docker 的复杂性，直接使用项目！