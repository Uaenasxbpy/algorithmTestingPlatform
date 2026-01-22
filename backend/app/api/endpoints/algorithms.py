from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import schemas
from app.services.algorithm_service import AlgorithmService, ConflictError

router = APIRouter()

@router.get("/", response_model=List[schemas.Algorithm])
async def get_algorithms(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """获取算法列表"""
    service = AlgorithmService(db)
    algorithms = service.get_algorithms(
        skip=skip, 
        limit=limit, 
        category=category, 
        is_active=is_active
    )
    return algorithms

@router.get("/{algorithm_id}", response_model=schemas.Algorithm)
async def get_algorithm(
    algorithm_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取算法详情"""
    service = AlgorithmService(db)
    algorithm = service.get_algorithm(algorithm_id)
    if not algorithm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="算法不存在"
        )
    return algorithm

@router.post("/", response_model=schemas.Algorithm)
async def create_algorithm(
    algorithm: schemas.AlgorithmCreate,
    db: Session = Depends(get_db)
):
    """创建新算法"""
    service = AlgorithmService(db)
    try:
        return service.create_algorithm(algorithm)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{algorithm_id}", response_model=schemas.Algorithm)
async def update_algorithm(
    algorithm_id: int,
    algorithm: schemas.AlgorithmUpdate,
    db: Session = Depends(get_db)
):
    """更新算法信息"""
    service = AlgorithmService(db)
    updated_algorithm = service.update_algorithm(algorithm_id, algorithm)
    if not updated_algorithm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="算法不存在"
        )
    return updated_algorithm

@router.delete("/{algorithm_id}", response_model=schemas.MessageResponse)
async def delete_algorithm(
    algorithm_id: int,
    db: Session = Depends(get_db)
):
    """删除算法（软删除）"""
    service = AlgorithmService(db)
    success = service.delete_algorithm(algorithm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="算法不存在"
        )
    return schemas.MessageResponse(message="算法删除成功")

@router.post("/validate", response_model=schemas.AlgorithmValidationResponse)
async def validate_algorithm_config(
    algorithm_data: schemas.AlgorithmValidationRequest,
    db: Session = Depends(get_db)
):
    """验证算法配置是否正确"""
    service = AlgorithmService(db)
    try:
        validation_result = service.validate_algorithm_config(algorithm_data)
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证算法配置时发生错误: {str(e)}"
        )

@router.get("/{algorithm_id}/test", response_model=schemas.MessageResponse)
async def test_algorithm_availability(
    algorithm_id: int,
    db: Session = Depends(get_db)
):
    """测试算法可用性"""
    service = AlgorithmService(db)
    algorithm = service.get_algorithm(algorithm_id)
    if not algorithm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="算法不存在"
        )
    
    # 这里会调用C库测试算法是否可用
    try:
        is_available = service.test_algorithm_availability(algorithm_id)
        if is_available:
            return schemas.MessageResponse(message="算法可用")
        else:
            return schemas.MessageResponse(message="算法不可用", success=False)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试算法时发生错误: {str(e)}"
        )