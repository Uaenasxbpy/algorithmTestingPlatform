from fastapi import APIRouter
from app.api.endpoints import algorithms, tasks, results, reports

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(
    algorithms.router, 
    prefix="/algorithms", 
    tags=["algorithms"]
)

api_router.include_router(
    tasks.router, 
    prefix="/tasks", 
    tags=["tasks"]
)

api_router.include_router(
    results.router, 
    prefix="/results", 
    tags=["results"]
)

api_router.include_router(
    reports.router, 
    prefix="/reports", 
    tags=["reports"]
)