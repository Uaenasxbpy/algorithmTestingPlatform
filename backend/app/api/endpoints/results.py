from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import schemas
from app.services.result_service import ResultService
import logging
from app.core.config import settings

# 配置日志记录器
logger = logging.getLogger(settings.LOGGER_NAME)
logger.setLevel(settings.LOG_LEVEL)

router = APIRouter()

@router.get("/task/{task_id}", response_model=List[schemas.TestResult])
async def get_task_results(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取指定任务的测试结果
    
    Args:
        task_id: 任务ID
        db: 数据库会话对象
    
    Returns:
        List[schemas.TestResult]: 测试结果列表
    
    Raises:
        HTTPException: 当任务ID无效或查询失败时
    """
    try:
        if task_id <= 0:
            logger.error(f"Invalid task_id: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        logger.debug(f"Request to get results for task_id: {task_id}")
        service = ResultService(db)
        results = service.get_task_results(task_id)
        logger.info(f"Successfully retrieved {len(results)} results for task_id: {task_id}")
        return results
    except ValueError as e:
        logger.error(f"Value error in get_task_results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get task results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务结果失败"
        )

@router.get("/task/{task_id}/summary", response_model=dict)
async def get_task_results_summary(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取任务结果摘要统计
    
    Args:
        task_id: 任务ID
        db: 数据库会话对象
    
    Returns:
        dict: 结果摘要统计
    
    Raises:
        HTTPException: 当任务ID无效、无结果或查询失败时
    """
    try:
        if task_id <= 0:
            logger.error(f"Invalid task_id: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        logger.debug(f"Request to get results summary for task_id: {task_id}")
        service = ResultService(db)
        summary = service.get_task_results_summary(task_id)
        if not summary:
            logger.warning(f"No results summary found for task_id: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到任务结果"
            )
        logger.info(f"Successfully retrieved results summary for task_id: {task_id}")
        return summary
    except ValueError as e:
        logger.error(f"Value error in get_task_results_summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        # 重新抛出已经处理过的HTTP异常
        raise
    except Exception as e:
        logger.error(f"Failed to get results summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务结果摘要失败"
        )

@router.get("/task/{task_id}/metrics", response_model=schemas.PerformanceMetrics)
async def get_task_performance_metrics(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取任务性能指标
    
    Args:
        task_id: 任务ID
        db: 数据库会话对象
    
    Returns:
        schemas.PerformanceMetrics: 性能指标对象
    
    Raises:
        HTTPException: 当任务ID无效、无指标或查询失败时
    """
    try:
        if task_id <= 0:
            logger.error(f"Invalid task_id: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务ID必须为正整数"
            )
            
        logger.debug(f"Request to get performance metrics for task_id: {task_id}")
        service = ResultService(db)
        metrics = service.get_performance_metrics(task_id)
        if not metrics:
            logger.warning(f"No performance metrics found for task_id: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到性能指标"
            )
        logger.info(f"Successfully retrieved performance metrics for task_id: {task_id}")
        return metrics
    except ValueError as e:
        logger.error(f"Value error in get_task_performance_metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        # 重新抛出已经处理过的HTTP异常
        raise
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务性能指标失败"
        )

@router.get("/compare", response_model=dict)
async def compare_algorithms(
    algorithm_ids: str = Query(..., description="逗号分隔的算法ID列表"),
    metric_name: Optional[str] = Query(None, description="可选的比较指标名称"),
    db: Session = Depends(get_db)
):
    """比较多个算法的性能
    
    Args:
        algorithm_ids: 逗号分隔的算法ID列表
        metric_name: 可选的比较指标名称
        db: 数据库会话对象
    
    Returns:
        dict: 包含算法比较结果的数据
    
    Raises:
        HTTPException: 当参数无效或比较失败时
    """
    try:
        logger.debug(f"Request to compare algorithms: {algorithm_ids}, metric: {metric_name}")
        
        # 验证算法ID格式
        try:
            algorithm_id_list = [int(id.strip()) for id in algorithm_ids.split(',')]
        except ValueError:
            logger.error(f"Invalid algorithm_ids format: {algorithm_ids}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="算法ID格式错误，应为逗号分隔的正整数列表"
            )
            
        # 验证算法ID值
        for alg_id in algorithm_id_list:
            if alg_id <= 0:
                logger.error(f"Invalid algorithm_id in list: {alg_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="算法ID必须为正整数"
                )
                
        # 限制算法数量，防止性能问题
        if len(algorithm_id_list) > 10:
            logger.warning(f"Too many algorithm IDs requested: {len(algorithm_id_list)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多可比较10个算法"
            )
            
        service = ResultService(db)
        comparison = service.compare_algorithms(algorithm_id_list, metric_name)
        logger.info(f"Successfully compared {len(comparison.get('algorithms', {}))} algorithms")
        return comparison
    except ValueError as e:
        logger.error(f"Value error in compare_algorithms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        # 重新抛出已经处理过的HTTP异常
        raise
    except Exception as e:
        logger.error(f"Failed to compare algorithms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比较算法性能失败"
        )

@router.get("/algorithm/{algorithm_id}/latest", response_model=List[schemas.TestResult])
async def get_algorithm_latest_results(
    algorithm_id: int,
    limit: int = Query(10, ge=1, le=100, description="返回结果的最大数量，范围1-100"),
    db: Session = Depends(get_db)
):
    """获取算法的最新测试结果
    
    Args:
        algorithm_id: 算法ID
        limit: 返回结果的最大数量
        db: 数据库会话对象
    
    Returns:
        List[schemas.TestResult]: 最新的测试结果列表
    
    Raises:
        HTTPException: 当参数无效或查询失败时
    """
    try:
        if algorithm_id <= 0:
            logger.error(f"Invalid algorithm_id: {algorithm_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="算法ID必须为正整数"
            )
            
        logger.debug(f"Request to get latest results for algorithm_id: {algorithm_id}, limit: {limit}")
        service = ResultService(db)
        results = service.get_algorithm_latest_results(algorithm_id, limit)
        logger.info(f"Successfully retrieved {len(results)} latest results for algorithm_id: {algorithm_id}")
        return results
    except ValueError as e:
        logger.error(f"Value error in get_algorithm_latest_results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get latest results for algorithm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取算法最新测试结果失败"
        )

@router.get("/algorithm/{algorithm_id}/history", response_model=dict)
async def get_algorithm_performance_history(
    algorithm_id: int,
    metric_name: str,
    days: int = Query(30, ge=1, le=365, description="查询的天数范围，1-365天"),
    db: Session = Depends(get_db)
):
    """获取算法性能历史趋势
    
    Args:
        algorithm_id: 算法ID
        metric_name: 指标名称
        days: 查询的天数范围
        db: 数据库会话对象
    
    Returns:
        dict: 包含历史性能数据的字典
    
    Raises:
        HTTPException: 当参数无效或查询失败时
    """
    try:
        if algorithm_id <= 0:
            logger.error(f"Invalid algorithm_id: {algorithm_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="算法ID必须为正整数"
            )
            
        if not metric_name:
            logger.error("Empty metric_name provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指标名称不能为空"
            )
            
        logger.debug(f"Request to get performance history for algorithm_id: {algorithm_id}, metric: {metric_name}, days: {days}")
        service = ResultService(db)
        history = service.get_algorithm_performance_history(
            algorithm_id, metric_name, days
        )
        logger.info(f"Successfully retrieved performance history with {len(history.get('data', []))} data points for algorithm_id: {algorithm_id}")
        return history
    except ValueError as e:
        logger.error(f"Value error in get_algorithm_performance_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get performance history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取算法性能历史趋势失败"
        )

@router.post("/", response_model=schemas.TestResult, tags=["系统内部调用"])
async def create_result(
    result: schemas.TestResultCreate,
    db: Session = Depends(get_db)
):
    """创建测试结果（通常由系统内部调用）
    
    Args:
        result: 测试结果创建对象
        db: 数据库会话对象
    
    Returns:
        schemas.TestResult: 创建的测试结果
    
    Raises:
        HTTPException: 当输入数据无效或创建失败时
    """
    try:
        logger.debug(f"Request to create result for task_id: {result.task_id if hasattr(result, 'task_id') else 'unknown'}")
        service = ResultService(db)
        created_result = service.create_result(result)
        logger.info(f"Successfully created result with id: {created_result.id}")
        return created_result
    except ValueError as e:
        logger.error(f"Value error in create_result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建测试结果失败"
        )

@router.delete("/{result_id}", response_model=schemas.MessageResponse)
async def delete_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """删除测试结果
    
    Args:
        result_id: 结果ID
        db: 数据库会话对象
    
    Returns:
        schemas.MessageResponse: 操作结果消息
    
    Raises:
        HTTPException: 当结果ID无效、结果不存在或删除失败时
    """
    try:
        if result_id <= 0:
            logger.error(f"Invalid result_id: {result_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结果ID必须为正整数"
            )
            
        logger.debug(f"Request to delete result with id: {result_id}")
        service = ResultService(db)
        success = service.delete_result(result_id)
        if not success:
            logger.warning(f"Result with id {result_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="结果不存在"
            )
        logger.info(f"Successfully deleted result with id: {result_id}")
        return schemas.MessageResponse(message="结果删除成功")
    except ValueError as e:
        logger.error(f"Value error in delete_result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        # 重新抛出已经处理过的HTTP异常
        raise
    except Exception as e:
        logger.error(f"Failed to delete result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除测试结果失败"
        )