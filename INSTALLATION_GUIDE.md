# 算法测试平台安装指南

本指南提供了算法测试平台的完整安装步骤，包括依赖安装、C库编译和环境配置。

## 系统要求

- **操作系统**：Windows 10/11、Ubuntu 20.04+、macOS 12+
- **Python**：3.9+（后端）
- **Node.js**：16+（前端）
- **数据库**：MySQL 8.0+ 或 SQLite 3
- **C编译器**：GCC (Linux/macOS)、MSVC (Windows) 或 MinGW (Windows)
- **Docker**（可选）：20.10+ 和 Docker Compose 1.29+

## 快速开始（使用Docker）

如果您已安装Docker和Docker Compose，可以使用以下命令快速启动项目：

```bash
# 复制环境变量示例文件
cp .env.example .env
# 根据需要编辑.env文件中的配置
# 启动所有服务
docker-compose up -d --build
```

服务启动后，您可以通过以下地址访问：
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- 数据库：localhost:3306（MySQL）

## 手动安装

### 1. 安装Python依赖

```bash
# 进入后端目录
cd backend
# 安装Python依赖
pip install -r requirements.txt
```

### 2. 安装Node.js依赖

```bash
# 进入前端目录
cd ../frontend
# 安装Node.js依赖
npm install
```

### 3. 编译C库（重要）

本项目使用C语言实现的后量子密码（PQC）算法库。以下是在不同操作系统上编译这些库的步骤：

#### Windows上编译

1. 安装 [MSVC Build Tools](https://visualstudio.microsoft.com/downloads/) 或 [MinGW](https://www.mingw-w64.org/)
2. 安装 [CMake](https://cmake.org/download/)
3. 进入C库目录并编译

```bash
cd ../libs
# 编译liboqs库
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
build.bat shared
cd ..

# 编译PQClean库
git clone https://github.com/PQClean/PQClean.git
cd PQClean
mkdir build
cd build
cmake .. -DBUILD_SHARED_LIBS=ON
cmake --build . --config Release
cd ../..

# 复制编译好的库文件到正确位置
copy liboqs\build\bin\Release\oqs.dll .
copy PQClean\build\Release\*.dll .
```

#### Linux/macOS上编译

```bash
cd ../libs
# 编译liboqs库
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake .. -DBUILD_SHARED_LIBS=ON
make -j4
sudo make install
cd ../..

# 编译PQClean库
git clone https://github.com/PQClean/PQClean.git
cd PQClean
mkdir build && cd build
cmake .. -DBUILD_SHARED_LIBS=ON
make -j4
sudo make install
cd ../..

# 复制编译好的库文件到正确位置
cp /usr/local/lib/liboqs.so .
cp PQClean/build/libpqclean_*.so .
```

### 4. 配置数据库

#### MySQL设置

```bash
# 创建数据库和用户
mysql -u root -p
CREATE DATABASE algorithm_testing;
CREATE USER 'alg_test'@'localhost' IDENTIFIED BY 'alg_test123';
GRANT ALL PRIVILEGES ON algorithm_testing.* TO 'alg_test'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 导入数据库模式
mysql -u alg_test -p algorithm_testing < database/schema.sql
```

#### 使用SQLite（开发模式）

如果您想使用SQLite进行开发，可以在.env文件中设置：

```
USE_MYSQL=false
DATABASE_URL=sqlite:///./test.db
```

### 5. 配置环境变量

复制.env.example文件并根据您的环境进行修改：

```bash
cp .env.example .env
# 根据需要编辑.env文件
```

### 6. 启动服务

#### 启动后端服务

```bash
cd backend
uvicorn main:app --reload
```

#### 启动前端服务

```bash
cd ../frontend
npm run dev
```

## 开发指南

### 目录结构说明

- `backend/`：FastAPI后端代码
- `frontend/`：Vue3前端代码
- `database/`：数据库模式和初始化脚本
- `libs/`：C语言算法库
- `reports/`：生成的测试报告

### 调试模式

默认情况下，后端服务在开发环境中以调试模式运行，提供详细的错误信息和热重载功能。您可以通过修改.env文件中的`DEBUG`参数来控制调试模式。

### 模拟模式

如果C库不可用，系统会自动切换到模拟模式运行。您也可以在代码中显式设置模拟模式：

```python
from app.libs.pqc_wrapper import PQCWrapper

# 强制使用模拟模式
wrapper = PQCWrapper(use_mock=True)
```

## 常见问题解决

### C库加载失败

- 确保已正确编译C库
- 检查库文件是否存在于正确的目录
- 检查库文件的扩展名是否与您的操作系统匹配（Windows：.dll，Linux：.so，macOS：.dylib）
- 确认您的系统可以找到这些库文件（设置正确的环境变量，如PATH或LD_LIBRARY_PATH）

### 数据库连接问题

- 检查.env文件中的数据库配置是否正确
- 确保MySQL服务正在运行
- 验证数据库用户的权限是否正确设置

### API连接错误

- 确保后端服务正在运行
- 检查前端的API基础URL配置是否正确
- 验证CORS设置是否允许前端域名访问后端API

## 安全注意事项

- 不要在生产环境中使用默认密码
- 定期更新.env文件中的密钥和密码
- 确保敏感配置不被提交到版本控制系统
- 在生产环境中禁用DEBUG模式