import uvicorn
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.router import api_router
from app.db.database import engine, Base

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建数据库表
try:
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建成功")
except Exception as e:
    logger.error(f"创建数据库表时出错: {e}")

# 确保reports目录存在
try:
    reports_dir = settings.REPORTS_DIR
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        logger.info(f"创建reports目录: {reports_dir}")
except Exception as e:
    logger.error(f"创建reports目录时出错: {e}")

# 应用初始化
app = FastAPI(
    title="算法测试平台 API",
    description="用于测试和验证 NIST 标准化的后量子密码（PQC）算法的 API 接口",
    version="1.0.0",
    debug=settings.DEBUG
)

# 设置CORS
logger.info(f"当前CORS配置 - 允许的源: {settings.ALLOWED_ORIGINS}")
# 为了确保开发环境中的兼容性，使用更宽松的CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 直接指定允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 挂载静态文件目录（用于报告文件）
try:
    app.mount("/static/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")
    logger.info("静态文件目录挂载成功")
except Exception as e:
    logger.error(f"挂载静态文件目录时出错: {e}")

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info(f"API路由注册成功，前缀: {settings.API_V1_STR}")

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误，请联系管理员"}
    )

@app.get("/")
async def root():
    logger.info("访问根端点")
    return {"message": "算法测试平台 API", "version": settings.VERSION}

@app.get("/health", tags=["system"])
async def health_check():
    """详细的健康检查端点"""
    # 检查数据库连接
    db_status = "healthy"
    try:
        from app.db.database import get_db
        db = next(get_db())
        # 执行简单查询验证连接
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        logger.error(f"数据库连接检查失败: {e}")
        db_status = "unhealthy"
    
    # 检查C库加载状态
    c_lib_status = "unhealthy"
    try:
        from app.libs.pqc_wrapper import PQCWrapper
        pqc = PQCWrapper(use_mock=False)
        if pqc.liboqs or pqc.pqclean:
            c_lib_status = "healthy"
        elif pqc.use_mock:
            c_lib_status = "mock_mode"
    except Exception as e:
        logger.error(f"C库检查失败: {e}")
    
    # 检查报告目录
    reports_dir_status = "healthy" if os.path.exists(settings.REPORTS_DIR) else "unhealthy"
    
    status = "healthy" if db_status == "healthy" else "degraded"
    
    logger.info(f"健康检查 - 状态: {status}, 数据库: {db_status}, C库: {c_lib_status}, 报告目录: {reports_dir_status}")
    
    return {
        "status": status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "c_library": c_lib_status,
        "reports_directory": reports_dir_status,
        "timestamp": str(os.path.getmtime(__file__))
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )