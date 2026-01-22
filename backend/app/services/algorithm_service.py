from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from app.models.models import Algorithm
from app.models import schemas
from app.libs.pqc_wrapper import PQCWrapper
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class ConflictError(Exception):
    """冲突错误，用于表示资源已存在"""
    pass

class AlgorithmService:
    def __init__(self, db: Session):
        self.db = db
        try:
            # 使用配置中的设置初始化PQC包装器
            self.pqc_wrapper = PQCWrapper(
                use_mock=settings.USE_MOCK_MODE
            )
            logger.info(f"PQC包装器初始化成功，模式: {'模拟' if settings.USE_MOCK_MODE else '真实'}")
        except Exception as e:
            logger.error(f"PQC包装器初始化失败: {str(e)}")
            # 即使初始化失败，也要创建一个模拟模式的包装器以确保服务可用
            self.pqc_wrapper = PQCWrapper(use_mock=True)

    def get_algorithms(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        category: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[Algorithm]:
        """获取算法列表"""
        try:
            # 验证参数
            if skip < 0:
                raise ValueError("skip参数不能为负数")
            if limit < 1 or limit > 1000:
                raise ValueError("limit参数必须在1到1000之间")
            
            query = self.db.query(Algorithm)
            
            if category:
                if category not in ['KEM', 'SIGNATURE']:
                    logger.warning(f"无效的算法类别: {category}")
                    return []
                query = query.filter(Algorithm.category == category)
            
            if is_active is not None:
                query = query.filter(Algorithm.is_active == is_active)
                
            result = query.offset(skip).limit(limit).all()
            logger.info(f"获取算法列表成功，返回{len(result)}个算法")
            return result
        except ValueError as e:
            logger.warning(f"获取算法列表参数错误: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"获取算法列表失败: {str(e)}")
            return []

    def get_algorithm(self, algorithm_id: int) -> Optional[Algorithm]:
        """根据ID获取算法"""
        try:
            if not isinstance(algorithm_id, int) or algorithm_id <= 0:
                raise ValueError("算法ID必须为正整数")
                
            result = self.db.query(Algorithm).filter(Algorithm.id == algorithm_id).first()
            if result:
                logger.info(f"获取算法成功，ID: {algorithm_id}, 名称: {result.name}")
            else:
                logger.warning(f"未找到ID为{algorithm_id}的算法")
            return result
        except ValueError as e:
            logger.warning(f"获取算法参数错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取算法失败: {str(e)}")
            return None

    def get_algorithm_by_name(self, name: str) -> Optional[Algorithm]:
        """根据名称获取算法"""
        try:
            if not name or not isinstance(name, str):
                raise ValueError("算法名称不能为空")
                
            # 安全验证，防止SQL注入
            safe_name = name.strip()
            if not safe_name:
                raise ValueError("算法名称不能为空")
                
            result = self.db.query(Algorithm).filter(Algorithm.name == safe_name).first()
            if result:
                logger.info(f"获取算法成功，名称: {safe_name}")
            return result
        except ValueError as e:
            logger.warning(f"获取算法参数错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取算法失败: {str(e)}")
            return None

    def create_algorithm(self, algorithm: schemas.AlgorithmCreate) -> Algorithm:
        """创建新算法"""
        try:
            # 参数验证
            if not algorithm.name or not isinstance(algorithm.name, str):
                raise ValueError("算法名称不能为空")
            if algorithm.category not in ['KEM', 'SIGNATURE']:
                raise ValueError("算法类别必须是KEM或SIGNATURE")
            if algorithm.source not in ['liboqs', 'pqclean']:
                raise ValueError("算法源必须是liboqs或pqclean")
            
            # 检查算法名称是否已存在
            existing = self.get_algorithm_by_name(algorithm.name)
            if existing:
                # 使用独特的异常类型来区分重复和其他错误
                raise ConflictError(f"算法名称 '{algorithm.name}' 已存在")

            db_algorithm = Algorithm(
                name=algorithm.name.strip(),
                category=algorithm.category,
                source=algorithm.source,
                version=algorithm.version or "1.0",
                description=algorithm.description or "",
                library_name=algorithm.library_name or "",
                is_active=True
            )
            
            self.db.add(db_algorithm)
            self.db.commit()
            self.db.refresh(db_algorithm)
            
            logger.info(f"创建算法成功，ID: {db_algorithm.id}, 名称: {db_algorithm.name}")
            return db_algorithm
        except ConflictError:
            logger.warning(f"创建算法失败 - 算法名称已存在: {algorithm.name}")
            self.db.rollback()
            raise
        except ValueError as e:
            logger.warning(f"创建算法参数错误: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"创建算法失败: {str(e)}")
            self.db.rollback()
            raise

    def update_algorithm(
        self, 
        algorithm_id: int, 
        algorithm: schemas.AlgorithmUpdate
    ) -> Optional[Algorithm]:
        """更新算法信息"""
        try:
            # 参数验证
            if not isinstance(algorithm_id, int) or algorithm_id <= 0:
                raise ValueError("算法ID必须为正整数")
            
            db_algorithm = self.get_algorithm(algorithm_id)
            if not db_algorithm:
                logger.warning(f"未找到ID为{algorithm_id}的算法，无法更新")
                return None

            # 获取更新数据
            update_data = algorithm.dict(exclude_unset=True)
            
            # 验证更新数据
            if 'category' in update_data and update_data['category'] not in ['KEM', 'SIGNATURE']:
                raise ValueError("算法类别必须是KEM或SIGNATURE")
            if 'source' in update_data and update_data['source'] not in ['liboqs', 'pqclean']:
                raise ValueError("算法源必须是liboqs或pqclean")
            if 'name' in update_data:
                # 检查新名称是否已存在
                existing = self.get_algorithm_by_name(update_data['name'])
                if existing and existing.id != algorithm_id:
                    raise ConflictError(f"算法名称 '{update_data['name']}' 已存在")
                update_data['name'] = update_data['name'].strip()
            
            # 应用更新
            for field, value in update_data.items():
                setattr(db_algorithm, field, value)

            self.db.commit()
            self.db.refresh(db_algorithm)
            
            logger.info(f"更新算法成功，ID: {algorithm_id}, 名称: {db_algorithm.name}")
            return db_algorithm
        except ConflictError as e:
            logger.warning(f"更新算法失败 - 算法名称已存在: {str(e)}")
            self.db.rollback()
            return None
        except ValueError as e:
            logger.warning(f"更新算法参数错误: {str(e)}")
            self.db.rollback()
            return None
        except Exception as e:
            logger.error(f"更新算法失败: {str(e)}")
            self.db.rollback()
            return None

    def delete_algorithm(self, algorithm_id: int) -> bool:
        """删除算法（软删除）"""
        try:
            # 参数验证
            if not isinstance(algorithm_id, int) or algorithm_id <= 0:
                raise ValueError("算法ID必须为正整数")
                
            db_algorithm = self.get_algorithm(algorithm_id)
            if not db_algorithm:
                logger.warning(f"未找到ID为{algorithm_id}的算法，无法删除")
                return False

            # 检查是否有相关的测试任务
            # 注意：这里应该添加关联检查，但当前模型中没有直接的关系
            # 如果有外键约束，可能需要先删除相关记录
            
            db_algorithm.is_active = False
            self.db.commit()
            
            logger.info(f"删除算法成功（软删除），ID: {algorithm_id}, 名称: {db_algorithm.name}")
            return True
        except ValueError as e:
            logger.warning(f"删除算法参数错误: {str(e)}")
            self.db.rollback()
            return False
        except Exception as e:
            logger.error(f"删除算法失败: {str(e)}")
            self.db.rollback()
            return False

    def test_algorithm_availability(self, algorithm_id: int) -> bool:
        """测试算法可用性"""
        try:
            if not isinstance(algorithm_id, int) or algorithm_id <= 0:
                raise ValueError("算法ID必须为正整数")
                
            algorithm = self.get_algorithm(algorithm_id)
            if not algorithm:
                logger.warning(f"未找到ID为{algorithm_id}的算法，无法测试可用性")
                return False

            # 调用C库测试算法是否可用
            result = self.pqc_wrapper.test_algorithm(
                algorithm.name,
                algorithm.category,
                algorithm.source
            )
            
            logger.info(f"测试算法可用性 {'成功' if result else '失败'}，ID: {algorithm_id}, 名称: {algorithm.name}")
            return result
        except ValueError as e:
            logger.warning(f"测试算法可用性参数错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"测试算法可用性异常: {str(e)}")
            return False

    def get_supported_algorithms(self) -> dict:
        """获取支持的算法列表"""
        try:
            result = self.pqc_wrapper.get_supported_algorithms()
            logger.info(f"获取支持的算法列表成功")
            return result
        except Exception as e:
            logger.error(f"获取支持的算法列表失败: {str(e)}")
            # 返回空的支持列表，确保服务不会崩溃
            return {"KEM": [], "SIGNATURE": []}
    
    def validate_algorithm_config(self, validation_request: schemas.AlgorithmValidationRequest) -> schemas.AlgorithmValidationResponse:
        """验证算法配置是否正确"""
        try:
            logger.info(f"开始验证算法配置: {validation_request.name}")
            
            errors = []
            warnings = []
            suggestions = []
            
            # 1. 验证算法名称格式
            if not validation_request.name or len(validation_request.name.strip()) < 2:
                errors.append("算法名称太短，至少需要2个字符")
            elif not validation_request.name.replace('-', '').replace('+', '').replace('_', '').isalnum():
                errors.append("算法名称只能包含字母、数字、连字符、加号和下划线")
            
            # 2. 验证库函数名命名规范
            library_name = validation_request.library_name.strip()
            if validation_request.source == 'liboqs':
                if not library_name.startswith('OQS_'):
                    errors.append("liboqs算法的库函数名必须以'OQS_'开头")
                    suggestions.append("示例: OQS_KEM_kyber_512 或 OQS_SIG_dilithium_2")
                elif validation_request.category == 'KEM' and 'KEM' not in library_name:
                    warnings.append("KEM算法的库函数名建议包含'KEM'关键字")
                elif validation_request.category == 'SIGNATURE' and 'SIG' not in library_name:
                    warnings.append("签名算法的库函数名建议包含'SIG'关键字")
            elif validation_request.source == 'pqclean':
                if not library_name.startswith('PQCLEAN_'):
                    errors.append("PQClean算法的库函数名必须以'PQCLEAN_'开头")
                    suggestions.append("示例: PQCLEAN_KYBER512_CLEAN 或 PQCLEAN_DILITHIUM2_CLEAN")
                elif not library_name.endswith('_CLEAN'):
                    warnings.append("PQClean算法的库函数名建议以'_CLEAN'结尾")
            
            # 3. 验证算法名称是否已存在
            existing = self.get_algorithm_by_name(validation_request.name)
            if existing:
                errors.append(f"算法名称'{validation_request.name}'已存在")
            
            # 4. 验证版本号格式
            if validation_request.version:
                import re
                version_pattern = r'^\d+\.\d+(\.\d+)?$'
                if not re.match(version_pattern, validation_request.version):
                    errors.append("版本号格式不正确，应为 x.y 或 x.y.z 格式")
            
            # 5. 验证算法是否在支持列表中
            supported_algorithms = self.get_supported_algorithms()
            category_algorithms = supported_algorithms.get(validation_request.category, [])
            
            # 检查是否为常见的后量子算法
            common_kem_algorithms = ['Kyber512', 'Kyber768', 'Kyber1024', 'NTRU-HPS-2048-509', 'SABER-KEM-128s']
            common_sig_algorithms = ['Dilithium2', 'Dilithium3', 'Dilithium5', 'Falcon-512', 'Falcon-1024', 'SPHINCS+']
            
            if validation_request.category == 'KEM':
                if not any(common in validation_request.name for common in common_kem_algorithms):
                    warnings.append("该算法不在常见KEM算法列表中，请确认是否正确")
            else:  # SIGNATURE
                if not any(common in validation_request.name for common in common_sig_algorithms):
                    warnings.append("该算法不在常见签名算法列表中，请确认是否正确")
            
            # 6. 尝试验证算法可用性（在模拟模式下跳过）
            if not settings.USE_MOCK_MODE:
                try:
                    is_available = self.pqc_wrapper.test_algorithm(
                        validation_request.name,
                        validation_request.category,
                        validation_request.source
                    )
                    if not is_available:
                        errors.append("算法在系统中不可用，请检查配置")
                except Exception as e:
                    warnings.append(f"无法测试算法可用性: {str(e)}")
            
            # 生成验证结果
            if errors:
                message = f"验证失败，发现{len(errors)}个错误"
                if warnings:
                    message += f"和{len(warnings)}个警告"
                return schemas.AlgorithmValidationResponse(
                    valid=False,
                    message=message,
                    suggestions=suggestions if suggestions else None,
                    warnings=warnings if warnings else None
                )
            else:
                message = "验证成功，算法配置正确"
                if warnings:
                    message += f"，但有{len(warnings)}个警告"
                return schemas.AlgorithmValidationResponse(
                    valid=True,
                    message=message,
                    suggestions=suggestions if suggestions else None,
                    warnings=warnings if warnings else None
                )
                
        except Exception as e:
            logger.error(f"验证算法配置异常: {str(e)}")
            return schemas.AlgorithmValidationResponse(
                valid=False,
                message=f"验证过程发生错误: {str(e)}",
                suggestions=None,
                warnings=None
            )

    def initialize_default_algorithms(self) -> List[Algorithm]:
        """初始化默认的算法"""
        try:
            logger.info("开始初始化默认算法")
            
            default_algorithms = [
                # KEM算法
                {
                    "name": "Kyber512",
                    "category": "KEM",
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "CRYSTALS-Kyber 512位安全级别",
                    "library_name": "OQS_KEM_kyber_512"
                },
                {
                    "name": "Kyber768",
                    "category": "KEM",
                    "source": "liboqs", 
                    "version": "1.0",
                    "description": "CRYSTALS-Kyber 768位安全级别",
                    "library_name": "OQS_KEM_kyber_768"
                },
                {
                    "name": "Kyber1024",
                    "category": "KEM",
                    "source": "liboqs",
                    "version": "1.0", 
                    "description": "CRYSTALS-Kyber 1024位安全级别",
                    "library_name": "OQS_KEM_kyber_1024"
                },
                # 签名算法
                {
                    "name": "Dilithium2",
                    "category": "SIGNATURE", 
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "CRYSTALS-Dilithium 安全级别2",
                    "library_name": "OQS_SIG_dilithium_2"
                },
                {
                    "name": "Dilithium3",
                    "category": "SIGNATURE",
                    "source": "liboqs",
                    "version": "1.0", 
                    "description": "CRYSTALS-Dilithium 安全级别3",
                    "library_name": "OQS_SIG_dilithium_3"
                },
                {
                    "name": "Dilithium5",
                    "category": "SIGNATURE",
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "CRYSTALS-Dilithium 安全级别5", 
                    "library_name": "OQS_SIG_dilithium_5"
                },
                {
                    "name": "Falcon512",
                    "category": "SIGNATURE",
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "Falcon 512位签名算法",
                    "library_name": "OQS_SIG_falcon_512"
                },
                {
                    "name": "Falcon1024", 
                    "category": "SIGNATURE",
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "Falcon 1024位签名算法",
                    "library_name": "OQS_SIG_falcon_1024"
                }
            ]
            
            created_algorithms = []
            for alg_data in default_algorithms:
                try:
                    existing = self.get_algorithm_by_name(alg_data["name"])
                    if not existing:
                        alg_schema = schemas.AlgorithmCreate(**alg_data)
                        created_alg = self.create_algorithm(alg_schema)
                        created_algorithms.append(created_alg)
                        logger.info(f"初始化默认算法成功: {alg_data['name']}")
                    else:
                        logger.info(f"默认算法已存在，跳过: {alg_data['name']}")
                except Exception as e:
                    logger.error(f"初始化默认算法失败: {alg_data['name']}, 错误: {str(e)}")
                    # 继续初始化其他算法，不中断整个过程
                    continue
        
            logger.info(f"默认算法初始化完成，共创建{len(created_algorithms)}个新算法")
            return created_algorithms
        except Exception as e:
            logger.error(f"默认算法初始化过程异常: {str(e)}")
            return []