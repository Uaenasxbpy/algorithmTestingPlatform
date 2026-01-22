# 算法测试平台 - 快速启动指南

## 系统要求

- **Python**: 3.8+
- **Node.js**: 16+
- **MySQL**: 8.0+
- **操作系统**: Windows 10/11, Linux, macOS

## 快速启动

### 方式一：Docker 启动（推荐）

1. **安装 Docker 和 Docker Compose**

2. **克隆项目并启动**
```bash
# 克隆项目（如果需要）
git clone <项目地址>
cd algorithmTestingPlatform

# 启动所有服务
docker-compose up -d
```

3. **访问应用**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 方式二：手动启动

#### 1. 启动 MySQL 数据库

```bash
# 使用 Docker 启动 MySQL
docker run -d \
  --name algorithm_testing_mysql \
  -e MYSQL_ROOT_PASSWORD=root123456 \
  -e MYSQL_DATABASE=algorithm_testing \
  -p 3306:3306 \
  mysql:8.0

# 导入数据库结构
mysql -h localhost -u root -p algorithm_testing < database/schema.sql
```

#### 2. 启动后端服务

```bash
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 启动 FastAPI 服务
python main.py
```

后端服务将在 http://localhost:8000 启动

#### 3. 启动前端服务

```bash
cd frontend

# 安装 Node.js 依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:3000 启动

## 功能模块说明

### 1. 算法管理 (`/algorithms`)
- 添加、编辑、删除后量子密码算法
- 支持 KEM 和数字签名算法
- 算法可用性测试

### 2. 性能测试 (`/testing`)
- 创建算法性能测试任务
- 实时监控测试进度
- 支持自定义测试参数

### 3. 结果分析 (`/results`)
- 查看测试结果和性能指标
- 算法性能对比分析
- 数据可视化展示

### 4. 报告中心 (`/reports`)
- 生成 PDF 和 CSV 格式报告
- 报告下载和管理
- 批量操作支持

## 默认数据

系统会自动创建以下默认算法：

**KEM 算法:**
- Kyber512
- Kyber768
- Kyber1024

**签名算法:**
- Dilithium2
- Dilithium3
- Dilithium5
- Falcon512
- Falcon1024

## 配置说明

### 后端配置 (`backend/app/core/config.py`)

```python
# 数据库配置
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/algorithm_testing"

# C库路径配置
LIBOQS_PATH = "../libs/liboqs"
PQCLEAN_PATH = "../libs/pqclean"

# 报告存储路径
REPORTS_DIR = "../reports"
```

### 前端配置 (`frontend/vite.config.ts`)

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 开发模式

### 后端开发

```bash
cd backend

# 启动开发服务器（自动重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 运行测试
pytest

# 代码格式化
black .
isort .
```

### 前端开发

```bash
cd frontend

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 构建生产版本
npm run build
```

## 性能测试示例

1. **访问测试页面**: http://localhost:3000/testing

2. **选择算法**: 选择一个 KEM 或签名算法

3. **配置测试参数**:
   - 测试名称: `Kyber512_性能测试_2024-01-01`
   - 测试次数: `100`

4. **开始测试**: 点击"开始测试"按钮

5. **查看结果**: 测试完成后在结果分析页面查看

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 MySQL 服务是否启动
   - 验证数据库连接参数
   - 确认数据库和表已创建

2. **前端无法连接后端**
   - 检查后端服务是否在 8000 端口启动
   - 验证代理配置是否正确

3. **C库调用失败**
   - 当前使用模拟模式，无需真实C库
   - 如需真实库，请参考 `libs/README.md`

4. **报告生成失败**
   - 检查 `reports` 目录权限
   - 确认 Python 依赖完整安装

### 日志查看

```bash
# Docker 方式查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 手动启动方式
# 后端日志直接在终端显示
# 前端日志在浏览器开发者工具中查看
```

## 生产部署

### 使用 Docker

```bash
# 构建并启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps
```

### 手动部署

1. **后端部署**
```bash
# 安装生产依赖
pip install -r requirements.txt

# 使用 gunicorn 启动
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **前端部署**
```bash
# 构建生产版本
npm run build

# 使用 nginx 托管静态文件
cp -r dist/* /var/www/html/
```

## 支持与反馈

如有问题或建议，请通过以下方式联系：

- 问题报告: 项目 Issues
- 功能建议: 项目 Discussions
- 技术支持: 项目维护者

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基础算法管理功能
- 实现性能测试框架
- 提供结果分析和报告生成