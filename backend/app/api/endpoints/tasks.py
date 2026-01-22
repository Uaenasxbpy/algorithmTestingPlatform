from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import time

from app.db.database import get_db
from app.models import schemas
from app.services.task_service import TaskService
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[schemas.TestTask])
async def get_tasks(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    algorithm_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    start_time = time.time()
    # 验证参数范围
    skip = max(0, skip)  # 确保skip不为负
    limit = min(settings.MAX_QUERY_LIMIT, max(1, limit))  # 限制最大返回量
    
    logger.info("Received request for tasks list with params: skip=%d, limit=%d, algorithm_id=%s, status=%s", 
                skip, limit, algorithm_id, status_filter)
    
    try:
        service = TaskService(db)
        tasks = service.get_tasks(
            skip=skip,
            limit=limit,
            algorithm_id=algorithm_id,
            status=status_filter
        )
        
        logger.debug("Returning %d tasks in %.3f seconds", 
                    len(tasks), time.time() - start_time)
        return tasks
    except Exception as e:
        logger.error("Error fetching tasks: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务列表失败: " + str(e)
        )

@router.get("/{task_id}", response_model=schemas.TestTask)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取任务详情"""
    logger.info("Received request for task details with ID: %d", task_id)
    
    try:
        # 验证ID是否为正整数
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        service = TaskService(db)
        task = service.get_task(task_id)
        if not task:
            logger.warning("Task with ID %d not found", task_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务ID {task_id} 不存在"
            )
        
        logger.debug("Returning details for task ID: %d", task_id)
        return task
    except HTTPException:
        # 重新抛出已格式化的HTTP异常
        raise
    except Exception as e:
        logger.error("Error fetching task ID %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务详情失败: " + str(e)
        )

@router.post("/", response_model=schemas.TestTask, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.TestTaskCreate,
    db: Session = Depends(get_db)
):
    """创建新测试任务"""
    logger.info("Received request to create new task: %s", task.task_name)
    logger.debug("Task creation parameters: algorithm_id=%d, test_count=%d, parameters=%s", 
                task.algorithm_id, task.test_count, task.parameters)
    
    try:
        service = TaskService(db)
        created_task = service.create_task(task)
        logger.info("Task created successfully with ID: %d", created_task.id)
        return created_task
    except ValueError as e:
        logger.warning("Validation error when creating task: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating task: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建任务失败: " + str(e)
        )

@router.post("/execute", response_model=schemas.MessageResponse)
async def execute_test(
    request: schemas.TestExecutionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """执行测试任务"""
    logger.info("Received request to execute test: %s", request.test_name)
    logger.debug("Test execution parameters: algorithm_id=%d, test_count=%d, parameters=%s", 
                request.algorithm_id, request.test_count, request.parameters)
    
    # 参数验证
    if request.test_count <= 0 or request.test_count > settings.MAX_TEST_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"测试次数必须在1到{settings.MAX_TEST_COUNT}之间"
        )
    
    try:
        service = TaskService(db)
        
        # 创建任务
        task_data = schemas.TestTaskCreate(
            algorithm_id=request.algorithm_id,
            task_name=request.test_name,
            test_count=request.test_count,
            parameters=request.parameters
        )
        task = service.create_task(task_data)
        
        # 后台执行测试
        async def run_task():
            logger.info(f"Starting background execution for task ID: {task.id}")
            try:
                await service.execute_task_background(task.id)
                logger.info(f"Background execution completed for task ID: {task.id}")
            except Exception as e:
                logger.error(f"Error in background execution for task ID {task.id}: %s", str(e))
        
        background_tasks.add_task(run_task)
        
        logger.info(f"Task {task.id} created and scheduled for background execution")
        return schemas.MessageResponse(
            message=f"测试任务已创建，任务ID: {task.id}，正在后台执行"
        )
    except ValueError as e:
        logger.warning("Validation error when creating test task: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error executing test: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建任务失败: " + str(e)
        )

@router.put("/{task_id}", response_model=schemas.TestTask)
async def update_task(
    task_id: int,
    task: schemas.TestTaskUpdate,
    db: Session = Depends(get_db)
):
    """更新任务信息"""
    logger.info("Received request to update task ID: %d", task_id)
    logger.debug("Update parameters: %s", task.dict(exclude_unset=True))
    
    try:
        # 验证ID是否为正整数
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        service = TaskService(db)
        updated_task = service.update_task(task_id, task)
        if not updated_task:
            logger.warning("Task with ID %d not found for update", task_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务ID {task_id} 不存在"
            )
        
        logger.info("Task ID %d updated successfully", task_id)
        return updated_task
    except ValueError as e:
        logger.warning("Validation error when updating task %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # 重新抛出已格式化的HTTP异常
        raise
    except Exception as e:
        logger.error("Error updating task ID %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新任务失败: " + str(e)
        )

@router.delete("/{task_id}", response_model=schemas.MessageResponse)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """删除任务"""
    logger.info("Received request to delete task ID: %d", task_id)
    
    try:
        # 验证ID是否为正整数
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        service = TaskService(db)
        success = service.delete_task(task_id)
        if not success:
            logger.warning("Task with ID %d not found or cannot be deleted", task_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务ID {task_id} 不存在或无法删除"
            )
        
        logger.info("Task ID %d deleted successfully", task_id)
        return schemas.MessageResponse(message="任务删除成功")
    except ValueError as e:
        logger.warning("Validation error when deleting task %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # 重新抛出已格式化的HTTP异常
        raise
    except Exception as e:
        logger.error("Error deleting task ID %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除任务失败: " + str(e)
        )

@router.post("/{task_id}/stop", response_model=schemas.MessageResponse)
async def stop_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """停止正在运行的任务"""
    logger.info("Received request to stop task ID: %d", task_id)
    
    try:
        # 验证ID是否为正整数
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        service = TaskService(db)
        success = service.stop_task(task_id)
        if not success:
            logger.warning("Task with ID %d not found or cannot be stopped", task_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务ID {task_id} 不存在或无法停止（可能未在运行中）"
            )
        
        logger.info("Task ID %d stopped successfully", task_id)
        return schemas.MessageResponse(message="任务已停止")
    except HTTPException:
        # 重新抛出已格式化的HTTP异常
        raise
    except Exception as e:
        logger.error("Error stopping task ID %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="停止任务失败: " + str(e)
        )

@router.get("/{task_id}/status", response_model=dict)
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取任务执行状态"""
    logger.info("Received request to get status for task ID: %d", task_id)
    
    try:
        # 验证ID是否为正整数
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        service = TaskService(db)
        status_info = service.get_task_status(task_id)
        if not status_info:
            logger.warning("Task with ID %d not found", task_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务ID {task_id} 不存在"
            )
        
        logger.debug("Returning status for task ID %d: %s", task_id, status_info['status'])
        return status_info
    except HTTPException:
        # 重新抛出已格式化的HTTP异常
        raise
    except Exception as e:
        logger.error("Error getting status for task ID %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务状态失败: " + str(e)
        )

@router.post("/{task_id}/run", response_model=schemas.MessageResponse)
async def run_task_manually(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """手动运行任务（用于测试和调试）"""
    logger.info("Received request to manually run task ID: %d", task_id)
    
    try:
        # 验证ID是否为正整数
        if task_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        service = TaskService(db)
        task = service.get_task(task_id)
        if not task:
            logger.warning("Task with ID %d not found", task_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务ID {task_id} 不存在"
            )
        
        from app.models.models import TaskStatus
        if task.status != TaskStatus.PENDING:
            logger.warning("Task %d is not in pending state, current state: %s", task_id, task.status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务状态不是待运行，当前状态: {task.status}"
            )
        
        # 后台执行任务
        async def run_task():
            logger.info(f"Starting manual background execution for task ID: {task_id}")
            try:
                await service.execute_task_background(task_id)
                logger.info(f"Manual background execution completed for task ID: {task_id}")
            except Exception as e:
                logger.error(f"Error in manual background execution for task ID {task_id}: %s", str(e))
        
        background_tasks.add_task(run_task)
        
        logger.info(f"Task {task_id} scheduled for manual execution")
        return schemas.MessageResponse(
            message=f"任务 {task_id} 已开始执行"
        )
    except HTTPException:
        # 重新抛出已格式化的HTTP异常
        raise
    except Exception as e:
        logger.error("Error manually running task ID %d: %s", task_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="手动运行任务失败: " + str(e)
        )