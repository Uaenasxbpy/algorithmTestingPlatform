# 算法测试平台 (Algorithm Testing Platform)

## 项目简介

本平台用于本地环境下测试和验证 NIST 标准化的后量子密码（PQC）算法，实现快速调用、结果展示和可视化报告输出。

## 项目架构

```
[前端 Vue3] <—— HTTP/REST ——> [后端 Python FastAPI]
                                        |
                                        v
                           [C PQC 算法库(liboqs/PQClean)]
                                        |
                                   [MySQL 数据库]
```

## 技术栈

- **前端**: Vue3 + Vite + ECharts + Element Plus
- **后端**: Python FastAPI + SQLAlchemy + ctypes
- **数据库**: MySQL
- **算法库**: liboqs / PQClean (C语言实现)

## 项目结构

```
algorithmTestingPlatform/
├── backend/                 # 后端Python FastAPI
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库相关
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── libs/           # C库封装
│   ├── requirements.txt
│   └── main.py
├── frontend/               # 前端Vue3
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── api/            # API调用
│   │   ├── utils/          # 工具函数
│   │   └── stores/         # 状态管理
│   ├── package.json
│   └── vite.config.js
├── libs/                   # C算法库
│   ├── liboqs/            # liboqs库文件
│   └── bindings/          # Python绑定
├── database/              # 数据库脚本
│   └── schema.sql
├── docs/                  # 文档
├── reports/               # 生成的报告存储
├── docker-compose.yml     # Docker配置
└── README.md
```

## 功能特性

1. **算法管理**: 支持多种PQC算法（Kyber、Dilithium、Falcon、SPHINCS+）
2. **测试执行**: 功能测试和性能测试
3. **结果可视化**: 图表展示和数据对比
4. **报告生成**: PDF和CSV导出
5. **任务管理**: 测试任务的创建、执行和监控

## 开发里程碑

- [x] 阶段A: 项目结构搭建
- [ ] 阶段B: 后端API和C库集成
- [ ] 阶段C: 前端界面开发
- [ ] 阶段D: 数据库集成
- [ ] 阶段E: 可视化和报告功能

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- GCC编译器（用于编译C库）

### 安装步骤

1. 克隆项目
2. 安装后端依赖: `cd backend && pip install -r requirements.txt`
3. 安装前端依赖: `cd frontend && npm install`
4. 配置数据库连接
5. 编译C算法库
6. 启动服务

详细安装说明请参考 `docs/installation.md`

## 使用说明

1. 打开前端界面选择算法
2. 配置测试参数
3. 提交测试任务
4. 查看结果和生成报告

## 许可证

MIT Licensex
 


 