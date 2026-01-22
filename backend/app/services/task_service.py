from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
import os
import logging

from app.models.models import TestTask, Algorithm, TaskStatus
from app.models import schemas
from app.libs.pqc_wrapper import PQCWrapper
from app.services.result_service import ResultService
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        # 使用配置中的模拟模式设置初始化PQCWrapper
        self.pqc_wrapper = PQCWrapper(use_mock=settings.USE_MOCK)
        self.result_service = ResultService(db)
        logger.info("TaskService initialized with mock mode: %s", settings.USE_MOCK)

    def get_tasks(
        self, 
        skip: int = 0,
        limit: int = 100,
        algorithm_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[TestTask]:
        """获取任务列表"""
        try:
            # 验证参数
            skip = max(0, skip)
            limit = min(1000, max(1, limit))  # 限制最大返回量为1000
            
            logger.info("Fetching tasks with skip=%d, limit=%d, algorithm_id=%s, status=%s", 
                        skip, limit, algorithm_id, status)
            
            query = self.db.query(TestTask)
            
            if algorithm_id:
                query = query.filter(TestTask.algorithm_id == algorithm_id)
            if status:
                query = query.filter(TestTask.status == status)
                
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error("Error fetching tasks: %s", str(e))
            return []

    def get_task(self, task_id: int) -> Optional[TestTask]:
        """根据ID获取任务"""
        try:
            task = self.db.query(TestTask).filter(TestTask.id == task_id).first()
            if not task:
                logger.warning("Task with id %d not found", task_id)
            return task
        except Exception as e:
            logger.error("Error retrieving task %d: %s", task_id, str(e))
            return None

    def create_task(self, task: schemas.TestTaskCreate) -> TestTask:
        """创建新任务"""
        try:
            # 验证参数
            if not task.task_name or len(task.task_name.strip()) == 0:
                raise ValueError("任务名称不能为空")
            if task.test_count <= 0:
                raise ValueError("测试次数必须为正数")
            if task.test_count > 1000:
                raise ValueError("测试次数不能超过1000")

            # 验证算法是否存在
            logger.info("Creating task for algorithm_id: %d", task.algorithm_id)
            algorithm = self.db.query(Algorithm).filter(
                Algorithm.id == task.algorithm_id,
                Algorithm.is_active == True
            ).first()
            
            if not algorithm:
                logger.error("Algorithm with id %d not found or inactive", task.algorithm_id)
                raise ValueError("算法不存在或已禁用")

            # 转换参数为JSON字符串
            parameters_json = json.dumps(task.parameters) if task.parameters else None

            db_task = TestTask(
                algorithm_id=task.algorithm_id,
                task_name=task.task_name,
                parameters=parameters_json,
                test_count=task.test_count,
                status=TaskStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
            logger.info("Task created successfully with id: %d", db_task.id)
            return db_task
        except ValueError as e:
            logger.warning("Validation error when creating task: %s", str(e))
            raise
        except Exception as e:
            logger.error("Error creating task: %s", str(e))
            self.db.rollback()
            raise

    def update_task(
        self, 
        task_id: int, 
        task: schemas.TestTaskUpdate
    ) -> Optional[TestTask]:
        """更新任务信息"""
        try:
            logger.info("Updating task with id: %d", task_id)
            db_task = self.get_task(task_id)
            if not db_task:
                return None

            # 如果任务正在运行或已完成，则不允许修改
            if db_task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]:
                logger.warning("Cannot update task %d: it's running or completed", task_id)
                raise ValueError("不能修改正在运行或已完成的任务")

            update_data = task.dict(exclude_unset=True)
            
            # 处理参数字段
            if 'parameters' in update_data and update_data['parameters'] is not None:
                update_data['parameters'] = json.dumps(update_data['parameters'])
            
            # 验证任务名称
            if 'task_name' in update_data and update_data['task_name'] and len(update_data['task_name'].strip()) == 0:
                raise ValueError("任务名称不能为空")

            for field, value in update_data.items():
                setattr(db_task, field, value)

            self.db.commit()
            self.db.refresh(db_task)
            logger.info("Task %d updated successfully", task_id)
            return db_task
        except ValueError as e:
            logger.warning("Validation error when updating task %d: %s", task_id, str(e))
            raise
        except Exception as e:
            logger.error("Error updating task %d: %s", task_id, str(e))
            self.db.rollback()
            raise

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        try:
            logger.info("Deleting task with id: %d", task_id)
            db_task = self.get_task(task_id)
            if not db_task:
                return False

            # 如果任务正在运行，则不允许删除
            if db_task.status == TaskStatus.RUNNING:
                logger.warning("Cannot delete task %d: it's running", task_id)
                raise ValueError("不能删除正在运行的任务")

            # 先删除相关的报告文件
            from app.models.models import Report
            reports = self.db.query(Report).filter(Report.task_id == task_id).all()
            for report in reports:
                # 删除物理文件
                if os.path.exists(report.file_path):
                    try:
                        os.remove(report.file_path)
                        logger.debug("Deleted report file: %s", report.file_path)
                    except Exception as file_error:
                        logger.warning("Failed to delete report file %s: %s", report.file_path, str(file_error))
                # 删除数据库记录
                self.db.delete(report)
            
            # 删除任务（由于设置了CASCADE，相关的test_results会自动删除）
            self.db.delete(db_task)
            self.db.commit()
            logger.info("Task %d deleted successfully", task_id)
            return True
        except ValueError as e:
            logger.warning("Validation error when deleting task %d: %s", task_id, str(e))
            raise
        except Exception as e:
            logger.error("Error deleting task %d: %s", task_id, str(e))
            self.db.rollback()
            return False

    async def execute_task_background(self, task_id: int):
        """后台执行任务"""
        task = self.get_task(task_id)
        if not task:
            logger.warning("Cannot execute task: task %d not found", task_id)
            return

        try:
            # 检查任务状态
            if task.status != TaskStatus.PENDING:
                logger.warning("Task %d is not in pending state, current state: %s", 
                              task_id, task.status)
                return

            # 更新任务状态为运行中
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self.db.commit()
            logger.info("Task %d started execution", task_id)

            # 获取算法信息
            algorithm = task.algorithm
            if not algorithm:
                raise ValueError(f"Algorithm not found for task {task_id}")

            # 解析参数
            try:
                parameters = json.loads(task.parameters) if task.parameters else {}
                logger.debug("Task %d parameters: %s", task_id, parameters)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid parameters format: {str(e)}")

            # 执行测试
            if algorithm.category == "KEM":
                self._execute_kem_test(task, algorithm, parameters)
            elif algorithm.category == "SIGNATURE":
                self._execute_signature_test(task, algorithm, parameters)
            else:
                raise ValueError(f"Unsupported algorithm type: {algorithm.category}")

            # 更新任务状态为完成
            task.status = TaskStatus.COMPLETED
            task.finished_at = datetime.utcnow()
            logger.info("Task %d completed successfully", task_id)

        except Exception as e:
            # 更新任务状态为失败
            error_msg = str(e)
            task.status = TaskStatus.FAILED
            task.error_message = error_msg
            task.finished_at = datetime.utcnow()
            logger.error("Task %d failed: %s", task_id, error_msg)

        finally:
            self.db.commit()
            self.db.refresh(task)  # 确保获取最新状态

    def _execute_kem_test(self, task: TestTask, algorithm: Algorithm, parameters: Dict):
        """执行KEM算法测试"""
        results = []
        
        for round_num in range(task.test_count):
            try:
                logger.debug("Executing KEM test round %d for task %d, algorithm: %s", 
                            round_num + 1, task.id, algorithm.name)
                
                # 调用C库执行KEM测试
                test_result = self.pqc_wrapper.test_kem_algorithm(
                    algorithm.name,
                    algorithm.library_name
                )
                
                # 记录各项指标
                if test_result:
                    # 密钥生成时间
                    if 'keygen_time' in test_result:
                        self.result_service.create_result(schemas.TestResultCreate(
                            task_id=task.id,
                            metric_name='keygen_time',
                            value=test_result['keygen_time'],
                            unit='ms',
                            test_round=round_num + 1
                        ))
                    
                    # 封装时间
                    if 'encaps_time' in test_result:
                        self.result_service.create_result(schemas.TestResultCreate(
                            task_id=task.id,
                            metric_name='encaps_time',
                            value=test_result['encaps_time'],
                            unit='ms',
                            test_round=round_num + 1
                        ))
                    
                    # 解封装时间
                    if 'decaps_time' in test_result:
                        self.result_service.create_result(schemas.TestResultCreate(
                            task_id=task.id,
                            metric_name='decaps_time',
                            value=test_result['decaps_time'],
                            unit='ms',
                            test_round=round_num + 1
                        ))
                    
                    # 密钥和密文大小（只记录一次）
                    if round_num == 0:
                        if 'public_key_size' in test_result:
                            self.result_service.create_result(schemas.TestResultCreate(
                                task_id=task.id,
                                metric_name='public_key_size',
                                value=test_result['public_key_size'],
                                unit='bytes'
                            ))
                        
                        if 'private_key_size' in test_result:
                            self.result_service.create_result(schemas.TestResultCreate(
                                task_id=task.id,
                                metric_name='private_key_size',
                                value=test_result['private_key_size'],
                                unit='bytes'
                            ))
                        
                        if 'ciphertext_size' in test_result:
                            self.result_service.create_result(schemas.TestResultCreate(
                                task_id=task.id,
                                metric_name='ciphertext_size',
                                value=test_result['ciphertext_size'],
                                unit='bytes'
                            ))
                    
                    # 成功/失败标记
                    success = test_result.get('success', False)
                    results.append(1 if success else 0)
                    
                    if success:
                        logger.debug("KEM test round %d for task %d completed successfully", 
                                    round_num + 1, task.id)
                    else:
                        logger.warning("KEM test round %d for task %d completed with failure", 
                                      round_num + 1, task.id)
            except Exception as e:
                logger.error("Error in KEM test round %d for task %d: %s", 
                           round_num + 1, task.id, str(e))
                results.append(0)
                
        # 计算成功率
        success_rate = (sum(results) / len(results)) * 100 if results else 0
        self.result_service.create_result(schemas.TestResultCreate(
            task_id=task.id,
            metric_name='success_rate',
            value=success_rate,
            unit='%'
        ))

    def _execute_signature_test(self, task: TestTask, algorithm: Algorithm, parameters: Dict):
        """执行签名算法测试"""
        results = []
        
        for round_num in range(task.test_count):
            try:
                logger.debug("Executing signature test round %d for task %d, algorithm: %s", 
                            round_num + 1, task.id, algorithm.name)
                
                # 调用C库执行签名测试
                test_result = self.pqc_wrapper.test_signature_algorithm(
                    algorithm.name,
                    algorithm.library_name
                )
                
                # 记录各项指标
                if test_result:
                    # 密钥生成时间
                    if 'keygen_time' in test_result:
                        self.result_service.create_result(schemas.TestResultCreate(
                            task_id=task.id,
                            metric_name='keygen_time',
                            value=test_result['keygen_time'],
                            unit='ms',
                            test_round=round_num + 1
                        ))
                    
                    # 签名时间
                    if 'sign_time' in test_result:
                        self.result_service.create_result(schemas.TestResultCreate(
                            task_id=task.id,
                            metric_name='sign_time',
                            value=test_result['sign_time'],
                            unit='ms',
                            test_round=round_num + 1
                        ))
                    
                    # 验证时间
                    if 'verify_time' in test_result:
                        self.result_service.create_result(schemas.TestResultCreate(
                            task_id=task.id,
                            metric_name='verify_time',
                            value=test_result['verify_time'],
                            unit='ms',
                            test_round=round_num + 1
                        ))
                    
                    # 密钥和签名大小（只记录一次）
                    if round_num == 0:
                        if 'public_key_size' in test_result:
                            self.result_service.create_result(schemas.TestResultCreate(
                                task_id=task.id,
                                metric_name='public_key_size',
                                value=test_result['public_key_size'],
                                unit='bytes'
                            ))
                        
                        if 'private_key_size' in test_result:
                            self.result_service.create_result(schemas.TestResultCreate(
                                task_id=task.id,
                                metric_name='private_key_size',
                                value=test_result['private_key_size'],
                                unit='bytes'
                            ))
                        
                        if 'signature_size' in test_result:
                            self.result_service.create_result(schemas.TestResultCreate(
                                task_id=task.id,
                                metric_name='signature_size',
                                value=test_result['signature_size'],
                                unit='bytes'
                            ))
                    
                    # 成功/失败标记
                    success = test_result.get('success', False)
                    results.append(1 if success else 0)
                    
                    if success:
                        logger.debug("Signature test round %d for task %d completed successfully", 
                                    round_num + 1, task.id)
                    else:
                        logger.warning("Signature test round %d for task %d completed with failure", 
                                      round_num + 1, task.id)
            except Exception as e:
                logger.error("Error in signature test round %d for task %d: %s", 
                           round_num + 1, task.id, str(e))
                results.append(0)
                
        # 计算成功率
        success_rate = (sum(results) / len(results)) * 100 if results else 0
        self.result_service.create_result(schemas.TestResultCreate(
            task_id=task.id,
            metric_name='success_rate',
            value=success_rate,
            unit='%'
        ))

    def stop_task(self, task_id: int) -> bool:
        """停止正在运行的任务"""
        try:
            logger.info("Stopping task with id: %d", task_id)
            task = self.get_task(task_id)
            if not task or task.status != TaskStatus.RUNNING:
                logger.warning("Cannot stop task %d: not found or not running", task_id)
                return False
            
            # 将状态设置为失败
            task.status = TaskStatus.FAILED
            task.error_message = "任务被用户停止"
            task.finished_at = datetime.utcnow()
            self.db.commit()
            logger.info("Task %d stopped successfully", task_id)
            return True
        except Exception as e:
            logger.error("Error stopping task %d: %s", task_id, str(e))
            self.db.rollback()
            return False

    def get_task_status(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务执行状态"""
        try:
            logger.debug("Getting status for task %d", task_id)
            task = self.get_task(task_id)
            if not task:
                return None
            
            status_info = {
                'task_id': task.id,
                'status': task.status,
                'progress': 0,
                'started_at': task.started_at,
                'finished_at': task.finished_at,
                'error_message': task.error_message,
                'algorithm_id': task.algorithm_id,
                'test_count': task.test_count,
                'task_name': task.task_name
            }
            
            # 如果任务完成，计算进度为100%
            if task.status == TaskStatus.COMPLETED:
                status_info['progress'] = 100
            elif task.status == TaskStatus.RUNNING:
                # 通过结果数量估算进度，优化进度计算逻辑
                result_count = self.result_service.get_task_result_count(task_id)
                
                # 根据算法类型动态调整估算的总结果数
                algorithm = self.db.query(Algorithm).filter(Algorithm.id == task.algorithm_id).first()
                if algorithm:
                    if algorithm.category == "KEM":
                        # KEM算法每轮产生3个时间结果，加上3个大小结果（仅第一轮）
                        estimated_total = min(task.test_count * 3 + 3, result_count + (task.test_count * 3))
                    else:  # SIGNATURE
                        # 签名算法每轮产生3个时间结果，加上3个大小结果（仅第一轮）
                        estimated_total = min(task.test_count * 3 + 3, result_count + (task.test_count * 3))
                else:
                    # 默认估算
                    estimated_total = max(1, task.test_count * 3)
                    
                if estimated_total > 0:
                    progress = (result_count / estimated_total) * 100
                    # 限制进度最高为95%，保留5%用于最终处理
                    status_info['progress'] = min(95, progress)
                    logger.debug("Task %d progress: %d%% (results: %d/%d)", 
                                task_id, status_info['progress'], result_count, estimated_total)
        except Exception as e:
            logger.error("Error getting status for task %d: %s", task_id, str(e))
            # 返回基本状态信息，避免完全失败
            task = self.get_task(task_id)
            if task:
                return {
                    'task_id': task.id,
                    'status': task.status,
                    'progress': 0 if task.status != TaskStatus.COMPLETED else 100,
                    'error_message': f"获取详细状态出错: {str(e)}"
                }
            return None
        
        return status_info