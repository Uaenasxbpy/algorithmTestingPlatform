from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.models import TestResult, TestTask, Algorithm
from app.models import schemas
import statistics
import logging
from app.core.config import settings

# 配置日志记录器
logger = logging.getLogger(settings.LOGGER_NAME)
logger.setLevel(settings.LOG_LEVEL)

class ResultService:
    def __init__(self, db: Session):
        """初始化ResultService
        
        Args:
            db: 数据库会话对象
        
        Raises:
            ValueError: 当数据库会话为空时
        """
        if not db:
            logger.error("ResultService initialization failed: database session is None")
            raise ValueError("Database session cannot be None")
        self.db = db
        logger.debug("ResultService initialized successfully")

    def get_task_results(self, task_id: int) -> List[TestResult]:
        """获取指定任务的所有测试结果
        
        Args:
            task_id: 任务ID
        
        Returns:
            List[TestResult]: 测试结果列表
        
        Raises:
            ValueError: 当任务ID无效时
            Exception: 当数据库查询失败时
        """
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                logger.error(f"Invalid task_id: {task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            logger.debug(f"Fetching results for task_id: {task_id}")
            results = self.db.query(TestResult).filter(
                TestResult.task_id == task_id
            ).order_by(TestResult.created_at).all()
            logger.info(f"Successfully fetched {len(results)} results for task_id: {task_id}")
            return results
        except ValueError as e:
            logger.error(f"Value error in get_task_results: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch results for task_id {task_id}: {str(e)}")
            raise

    def get_task_result_count(self, task_id: int) -> int:
        """获取任务结果数量
        
        Args:
            task_id: 任务ID
        
        Returns:
            int: 结果数量
        
        Raises:
            ValueError: 当任务ID无效时
            Exception: 当数据库查询失败时
        """
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                logger.error(f"Invalid task_id: {task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            logger.debug(f"Counting results for task_id: {task_id}")
            count = self.db.query(TestResult).filter(
                TestResult.task_id == task_id
            ).count()
            logger.info(f"Successfully fetched result count: {count} for task_id: {task_id}")
            return count
        except ValueError as e:
            logger.error(f"Value error in get_task_result_count: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to count results for task_id {task_id}: {str(e)}")
            raise

    def create_result(self, result: schemas.TestResultCreate) -> TestResult:
        """创建测试结果
        
        Args:
            result: 测试结果创建对象
        
        Returns:
            TestResult: 创建的测试结果
        
        Raises:
            ValueError: 当输入数据无效时
            Exception: 当创建结果失败时
        """
        try:
            if not result:
                logger.error("Invalid result data: None")
                raise ValueError("Result data cannot be None")
            
            # 验证必要字段
            if not hasattr(result, 'task_id') or result.task_id is None:
                logger.error("Missing task_id in result data")
                raise ValueError("task_id is required")
            
            if not hasattr(result, 'metric_name') or not result.metric_name:
                logger.error("Missing metric_name in result data")
                raise ValueError("metric_name is required")
            
            if not hasattr(result, 'value') or result.value is None:
                logger.error("Missing value in result data")
                raise ValueError("value is required")
            
            # 验证数据类型
            if not isinstance(result.task_id, int) or result.task_id <= 0:
                logger.error(f"Invalid task_id: {result.task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            if not isinstance(result.value, (int, float)):
                logger.error(f"Invalid value type: {type(result.value).__name__}")
                raise ValueError("Value must be a number")
            
            # 检查任务是否存在
            task_exists = self.db.query(TestTask).filter(TestTask.id == result.task_id).first()
            if not task_exists:
                logger.error(f"Task with id {result.task_id} does not exist")
                raise ValueError(f"Task with id {result.task_id} does not exist")
            
            logger.debug(f"Creating result for task_id: {result.task_id}, metric: {result.metric_name}")
            
            db_result = TestResult(
                task_id=result.task_id,
                metric_name=result.metric_name,
                value=result.value,
                unit=result.unit if hasattr(result, 'unit') else None,
                test_round=result.test_round if hasattr(result, 'test_round') else 1
            )
            
            self.db.add(db_result)
            self.db.commit()
            self.db.refresh(db_result)
            
            logger.info(f"Successfully created result with id: {db_result.id} for task_id: {result.task_id}")
            return db_result
        except ValueError as e:
            logger.error(f"Value error in create_result: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Failed to create result: {str(e)}")
            self.db.rollback()
            raise

    def delete_result(self, result_id: int) -> bool:
        """删除测试结果
        
        Args:
            result_id: 结果ID
        
        Returns:
            bool: 是否成功删除
        
        Raises:
            ValueError: 当结果ID无效时
            Exception: 当删除操作失败时
        """
        try:
            if not isinstance(result_id, int) or result_id <= 0:
                logger.error(f"Invalid result_id: {result_id}")
                raise ValueError("Result ID must be a positive integer")
            
            logger.debug(f"Deleting result with id: {result_id}")
            db_result = self.db.query(TestResult).filter(
                TestResult.id == result_id
            ).first()
            
            if not db_result:
                logger.warning(f"Result with id {result_id} not found")
                return False
            
            self.db.delete(db_result)
            self.db.commit()
            logger.info(f"Successfully deleted result with id: {result_id}")
            return True
        except ValueError as e:
            logger.error(f"Value error in delete_result: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to delete result with id {result_id}: {str(e)}")
            self.db.rollback()
            raise

    def get_task_results_summary(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务结果摘要统计
        
        Args:
            task_id: 任务ID
        
        Returns:
            Optional[Dict[str, Any]]: 结果摘要统计，如果没有结果则返回None
        
        Raises:
            ValueError: 当任务ID无效时
            Exception: 当计算摘要失败时
        """
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                logger.error(f"Invalid task_id: {task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            logger.debug(f"Generating results summary for task_id: {task_id}")
            results = self.get_task_results(task_id)
            if not results:
                logger.warning(f"No results found for task_id: {task_id}")
                return None

            # 按指标分组
            metrics_data = {}
            for result in results:
                metric_name = result.metric_name
                if metric_name not in metrics_data:
                    metrics_data[metric_name] = []
                metrics_data[metric_name].append(result.value)

            # 计算统计信息
            summary = {}
            for metric_name, values in metrics_data.items():
                if values:
                    try:
                        metric_stats = {
                            'count': len(values),
                            'avg': statistics.mean(values),
                            'min': min(values),
                            'max': max(values),
                            'median': statistics.median(values),
                            'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                        }
                        summary[metric_name] = metric_stats
                    except statistics.StatisticsError as e:
                        logger.warning(f"Failed to calculate statistics for metric {metric_name}: {str(e)}")
                        summary[metric_name] = {'error': str(e)}

            # 获取任务信息
            task = self.db.query(TestTask).filter(TestTask.id == task_id).first()
            if task:
                summary['task_info'] = {
                    'task_id': task.id,
                    'task_name': task.task_name,
                    'test_count': task.test_count,
                    'algorithm_name': task.algorithm.name,
                    'category': task.algorithm.category
                }

            logger.info(f"Successfully generated results summary for task_id: {task_id}")
            return summary
        except ValueError as e:
            logger.error(f"Value error in get_task_results_summary: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate results summary for task_id {task_id}: {str(e)}")
            raise

    def get_performance_metrics(self, task_id: int) -> Optional[schemas.PerformanceMetrics]:
        """获取任务性能指标
        
        Args:
            task_id: 任务ID
        
        Returns:
            Optional[schemas.PerformanceMetrics]: 性能指标对象，如果没有结果则返回None
        
        Raises:
            ValueError: 当任务ID无效时
            Exception: 当计算性能指标失败时
        """
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                logger.error(f"Invalid task_id: {task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            logger.debug(f"Calculating performance metrics for task_id: {task_id}")
            results = self.get_task_results(task_id)
            if not results:
                logger.warning(f"No results found for task_id: {task_id}")
                return None

            # 提取各项指标的平均值
            metrics = {}
            for result in results:
                metric_name = result.metric_name
                if metric_name not in metrics:
                    metrics[metric_name] = []
                metrics[metric_name].append(result.value)

            # 计算平均值并构造性能指标对象
            performance_data = {}
            
            # 时间指标（需要计算平均值）
            time_metrics = ['keygen_time', 'encaps_time', 'decaps_time', 'sign_time', 'verify_time']
            for metric in time_metrics:
                if metric in metrics:
                    try:
                        performance_data[f'avg_{metric}'] = statistics.mean(metrics[metric])
                    except statistics.StatisticsError as e:
                        logger.warning(f"Failed to calculate mean for metric {metric}: {str(e)}")
                        performance_data[f'avg_{metric}'] = 0.0

            # 大小指标（取最大值或唯一值）
            size_metrics = ['public_key_size', 'private_key_size', 'signature_size', 'ciphertext_size']
            for metric in size_metrics:
                if metric in metrics:
                    try:
                        performance_data[metric] = max(metrics[metric])
                    except ValueError as e:
                        logger.warning(f"Failed to calculate max for metric {metric}: {str(e)}")
                        performance_data[metric] = 0

            # 成功率（取最后一个值）
            if 'success_rate' in metrics:
                performance_data['success_rate'] = metrics['success_rate'][-1]
            else:
                performance_data['success_rate'] = 0.0

            logger.info(f"Successfully calculated performance metrics for task_id: {task_id}")
            return schemas.PerformanceMetrics(**performance_data)
        except ValueError as e:
            logger.error(f"Value error in get_performance_metrics: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics for task_id {task_id}: {str(e)}")
            raise

    def compare_algorithms(
        self,
        algorithm_ids: List[int],
        metric_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """比较多个算法的性能
        
        Args:
            algorithm_ids: 算法ID列表
            metric_name: 可选的特定指标名称
        
        Returns:
            Dict[str, Any]: 包含算法比较结果的数据
        
        Raises:
            ValueError: 当输入参数无效时
            Exception: 当比较过程失败时
        """
        try:
            if not algorithm_ids or not isinstance(algorithm_ids, list):
                logger.error(f"Invalid algorithm_ids: {algorithm_ids}")
                raise ValueError("algorithm_ids must be a non-empty list of integers")
            
            # 验证算法ID
            for alg_id in algorithm_ids:
                if not isinstance(alg_id, int) or alg_id <= 0:
                    logger.error(f"Invalid algorithm_id in list: {alg_id}")
                    raise ValueError(f"Algorithm ID {alg_id} must be a positive integer")
            
            logger.debug(f"Comparing algorithms with ids: {algorithm_ids}, metric: {metric_name}")
            comparison_data = {}

            for algorithm_id in algorithm_ids:
                # 获取该算法的最新任务
                latest_task = self.db.query(TestTask).filter(
                    TestTask.algorithm_id == algorithm_id,
                    TestTask.status == 'COMPLETED'
                ).order_by(desc(TestTask.finished_at)).first()

                if latest_task:
                    algorithm_data = {
                        'algorithm_id': algorithm_id,
                        'algorithm_name': latest_task.algorithm.name,
                        'category': latest_task.algorithm.category,
                        'latest_task_id': latest_task.id,
                        'test_date': latest_task.finished_at
                    }

                    if metric_name:
                        # 获取特定指标的数据
                        metric_results = self.db.query(TestResult).filter(
                            TestResult.task_id == latest_task.id,
                            TestResult.metric_name == metric_name
                        ).all()
                        
                        if metric_results:
                            values = [r.value for r in metric_results]
                            try:
                                algorithm_data['metric_data'] = {
                                    'metric_name': metric_name,
                                    'avg': statistics.mean(values),
                                    'min': min(values),
                                    'max': max(values),
                                    'count': len(values)
                                }
                            except statistics.StatisticsError as e:
                                logger.warning(f"Failed to calculate statistics for metric {metric_name} in algorithm {algorithm_id}: {str(e)}")
                                algorithm_data['metric_data'] = {'error': str(e)}
                    else:
                        # 获取性能指标摘要
                        try:
                            metrics = self.get_performance_metrics(latest_task.id)
                            if metrics:
                                algorithm_data['performance_metrics'] = metrics.dict()
                        except Exception as e:
                            logger.warning(f"Failed to get performance metrics for task {latest_task.id}: {str(e)}")
                            algorithm_data['performance_metrics_error'] = str(e)

                    comparison_data[latest_task.algorithm.name] = algorithm_data
                else:
                    logger.warning(f"No completed tasks found for algorithm_id: {algorithm_id}")

            logger.info(f"Successfully compared {len(comparison_data)} algorithms")
            return {
                'algorithms': comparison_data,
                'comparison_metric': metric_name,
                'total_algorithms': len(comparison_data)
            }
        except ValueError as e:
            logger.error(f"Value error in compare_algorithms: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to compare algorithms: {str(e)}")
            raise

    def get_algorithm_latest_results(
        self,
        algorithm_id: int,
        limit: int = 10
    ) -> List[TestResult]:
        """获取算法的最新测试结果
        
        Args:
            algorithm_id: 算法ID
            limit: 返回结果的最大数量
        
        Returns:
            List[TestResult]: 最新的测试结果列表
        
        Raises:
            ValueError: 当输入参数无效时
            Exception: 当查询过程失败时
        """
        try:
            if not isinstance(algorithm_id, int) or algorithm_id <= 0:
                logger.error(f"Invalid algorithm_id: {algorithm_id}")
                raise ValueError("Algorithm ID must be a positive integer")
            
            if not isinstance(limit, int) or limit < 1:
                logger.error(f"Invalid limit: {limit}")
                raise ValueError("Limit must be a positive integer")
            
            # 限制最大返回数量，防止性能问题
            actual_limit = min(limit, 100)
            if actual_limit < limit:
                logger.warning(f"Limit {limit} exceeded maximum allowed (100), using {actual_limit}")
            
            logger.debug(f"Fetching latest results for algorithm_id: {algorithm_id}, limit: {actual_limit}")
            
            # 获取该算法的最新任务
            latest_tasks = self.db.query(TestTask).filter(
                TestTask.algorithm_id == algorithm_id,
                TestTask.status == 'COMPLETED'
            ).order_by(desc(TestTask.finished_at)).limit(5).all()

            if not latest_tasks:
                logger.warning(f"No completed tasks found for algorithm_id: {algorithm_id}")
                return []

            task_ids = [task.id for task in latest_tasks]
            
            results = self.db.query(TestResult).filter(
                TestResult.task_id.in_(task_ids)
            ).order_by(desc(TestResult.created_at)).limit(actual_limit).all()
            
            logger.info(f"Successfully fetched {len(results)} latest results for algorithm_id: {algorithm_id}")
            return results
        except ValueError as e:
            logger.error(f"Value error in get_algorithm_latest_results: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch latest results for algorithm_id {algorithm_id}: {str(e)}")
            raise

    def get_algorithm_performance_history(
        self,
        algorithm_id: int,
        metric_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取算法性能历史趋势
        
        Args:
            algorithm_id: 算法ID
            metric_name: 指标名称
            days: 查询的天数范围
        
        Returns:
            Dict[str, Any]: 包含历史性能数据的字典
        
        Raises:
            ValueError: 当输入参数无效时
            Exception: 当查询过程失败时
        """
        try:
            if not isinstance(algorithm_id, int) or algorithm_id <= 0:
                logger.error(f"Invalid algorithm_id: {algorithm_id}")
                raise ValueError("Algorithm ID must be a positive integer")
            
            if not metric_name or not isinstance(metric_name, str):
                logger.error(f"Invalid metric_name: {metric_name}")
                raise ValueError("Metric name must be a non-empty string")
            
            if not isinstance(days, int) or days < 1 or days > 365:
                logger.error(f"Invalid days: {days}")
                raise ValueError("Days must be between 1 and 365")
            
            logger.debug(f"Fetching performance history for algorithm_id: {algorithm_id}, metric: {metric_name}, days: {days}")
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # 获取时间范围内的任务
            tasks = self.db.query(TestTask).filter(
                TestTask.algorithm_id == algorithm_id,
                TestTask.status == 'COMPLETED',
                TestTask.finished_at >= start_date,
                TestTask.finished_at <= end_date
            ).order_by(TestTask.finished_at).all()

            if not tasks:
                logger.warning(f"No completed tasks found for algorithm_id: {algorithm_id} in the last {days} days")
                return {'data': [], 'algorithm_id': algorithm_id, 'metric_name': metric_name}

            history_data = []
            for task in tasks:
                # 获取该任务的指定指标数据
                metric_results = self.db.query(TestResult).filter(
                    TestResult.task_id == task.id,
                    TestResult.metric_name == metric_name
                ).all()

                if metric_results:
                    values = [r.value for r in metric_results]
                    try:
                        avg_value = statistics.mean(values)
                        
                        history_data.append({
                            'date': task.finished_at.isoformat(),
                            'task_id': task.id,
                            'task_name': task.task_name,
                            'value': avg_value,
                            'sample_count': len(values)
                        })
                    except statistics.StatisticsError as e:
                        logger.warning(f"Failed to calculate mean for metric {metric_name} in task {task.id}: {str(e)}")

            logger.info(f"Successfully fetched performance history with {len(history_data)} points for algorithm_id: {algorithm_id}")
            return {
                'data': history_data,
                'algorithm_id': algorithm_id,
                'metric_name': metric_name,
                'period_days': days,
                'total_points': len(history_data)
            }
        except ValueError as e:
            logger.error(f"Value error in get_algorithm_performance_history: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch performance history for algorithm_id {algorithm_id}: {str(e)}")
            raise

    def get_metric_distribution(self, task_id: int, metric_name: str) -> Dict[str, Any]:
        """获取指标值分布
        
        Args:
            task_id: 任务ID
            metric_name: 指标名称
        
        Returns:
            Dict[str, Any]: 包含指标分布数据的字典
        
        Raises:
            ValueError: 当输入参数无效时
            Exception: 当计算分布失败时
        """
        try:
            if not isinstance(task_id, int) or task_id <= 0:
                logger.error(f"Invalid task_id: {task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            if not metric_name or not isinstance(metric_name, str):
                logger.error(f"Invalid metric_name: {metric_name}")
                raise ValueError("Metric name must be a non-empty string")
            
            logger.debug(f"Calculating metric distribution for task_id: {task_id}, metric: {metric_name}")
            
            results = self.db.query(TestResult).filter(
                TestResult.task_id == task_id,
                TestResult.metric_name == metric_name
            ).all()

            if not results:
                logger.warning(f"No results found for task_id: {task_id} and metric: {metric_name}")
                return {
                    'values': [],
                    'histogram': {},
                    'statistics': {},
                    'message': 'No data available'
                }

            values = [r.value for r in results]
            
            # 创建直方图数据
            bins = 20
            try:
                min_val, max_val = min(values), max(values)
            except ValueError as e:
                logger.error(f"Failed to calculate min/max values: {str(e)}")
                return {
                    'values': values,
                    'histogram': {},
                    'statistics': {},
                    'error': str(e)
                }
                
            if min_val == max_val:
                logger.info(f"All values are the same ({min_val}) for task_id: {task_id}, metric: {metric_name}")
                return {
                    'values': values,
                    'histogram': {'bins': [min_val], 'counts': [len(values)]},
                    'statistics': {
                        'count': len(values),
                        'mean': min_val,
                        'std': 0,
                        'min': min_val,
                        'max': max_val
                    }
                }

            bin_width = (max_val - min_val) / bins
            bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
            counts = [0] * bins

            for value in values:
                bin_index = min(int((value - min_val) / bin_width), bins - 1)
                counts[bin_index] += 1

            # 计算统计信息
            try:
                statistics_data = {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'std': statistics.stdev(values) if len(values) > 1 else 0,
                    'min': min_val,
                    'max': max_val,
                    'median': statistics.median(values)
                }
            except statistics.StatisticsError as e:
                logger.warning(f"Failed to calculate some statistics: {str(e)}")
                statistics_data = {
                    'count': len(values),
                    'min': min_val,
                    'max': max_val,
                    'error': str(e)
                }

            logger.info(f"Successfully calculated metric distribution for task_id: {task_id}, metric: {metric_name}")
            return {
                'values': values,
                'histogram': {
                    'bin_edges': bin_edges,
                    'counts': counts
                },
                'statistics': statistics_data
            }
        except ValueError as e:
            logger.error(f"Value error in get_metric_distribution: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to calculate metric distribution for task_id {task_id}, metric {metric_name}: {str(e)}")
            raise