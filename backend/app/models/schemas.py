from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AlgorithmCategory(str, Enum):
    KEM = "KEM"
    SIGNATURE = "SIGNATURE"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# 算法相关模式
class AlgorithmBase(BaseModel):
    name: str = Field(..., description="算法名称")
    category: AlgorithmCategory = Field(..., description="算法类别")
    source: str = Field(..., description="算法来源")
    version: Optional[str] = Field(None, description="版本号")
    description: Optional[str] = Field(None, description="算法描述")
    library_name: Optional[str] = Field(None, description="C库函数名前缀")

class AlgorithmCreate(AlgorithmBase):
    pass

class AlgorithmUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[AlgorithmCategory] = None
    source: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    library_name: Optional[str] = None
    is_active: Optional[bool] = None

class Algorithm(AlgorithmBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# 测试任务相关模式
class TestTaskBase(BaseModel):
    algorithm_id: int = Field(..., description="算法ID")
    task_name: str = Field(..., description="任务名称")
    parameters: Optional[Dict[str, Any]] = Field(None, description="测试参数")
    test_count: int = Field(100, description="测试次数")

class TestTaskCreate(TestTaskBase):
    pass

class TestTaskUpdate(BaseModel):
    task_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    test_count: Optional[int] = None
    status: Optional[TaskStatus] = None
    error_message: Optional[str] = None

class TestTask(TestTaskBase):
    id: int
    status: TaskStatus
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    algorithm: Algorithm
    
    class Config:
        orm_mode = True

# 测试结果相关模式
class TestResultBase(BaseModel):
    task_id: int = Field(..., description="任务ID")
    metric_name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    unit: Optional[str] = Field(None, description="单位")
    test_round: Optional[int] = Field(None, description="测试轮次")

class TestResultCreate(TestResultBase):
    pass

class TestResult(TestResultBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# 报告相关模式
class ReportBase(BaseModel):
    task_id: int = Field(..., description="任务ID")
    report_name: str = Field(..., description="报告名称")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")

class ReportCreate(ReportBase):
    file_size: Optional[int] = None

class Report(ReportBase):
    id: int
    file_size: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# 算法验证相关模式
class AlgorithmValidationRequest(BaseModel):
    name: str = Field(..., description="算法名称")
    category: AlgorithmCategory = Field(..., description="算法类别")
    source: str = Field(..., description="算法来源")
    library_name: str = Field(..., description="C库函数名前缀")
    version: Optional[str] = Field(None, description="版本号")

class AlgorithmValidationResponse(BaseModel):
    valid: bool = Field(..., description="验证是否通过")
    message: str = Field(..., description="验证结果消息")
    suggestions: Optional[List[str]] = Field(None, description="改进建议")
    warnings: Optional[List[str]] = Field(None, description="警告信息")

# 通用响应模式
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ListResponse(BaseModel):
    items: List[Any]
    total: int
    page: int = 1
    size: int = 20

# 测试执行请求模式
class TestExecutionRequest(BaseModel):
    algorithm_id: int = Field(..., description="算法ID")
    test_name: str = Field(..., description="测试名称")
    test_count: int = Field(100, ge=1, le=10000, description="测试次数")
    parameters: Optional[Dict[str, Any]] = Field(None, description="额外参数")

# 算法性能结果模式
class PerformanceMetrics(BaseModel):
    avg_keygen_time: Optional[float] = Field(None, description="平均密钥生成时间(ms)")
    avg_encaps_time: Optional[float] = Field(None, description="平均封装时间(ms)")
    avg_decaps_time: Optional[float] = Field(None, description="平均解封装时间(ms)")
    avg_sign_time: Optional[float] = Field(None, description="平均签名时间(ms)")
    avg_verify_time: Optional[float] = Field(None, description="平均验证时间(ms)")
    success_rate: float = Field(..., description="成功率")
    public_key_size: Optional[int] = Field(None, description="公钥大小(bytes)")
    private_key_size: Optional[int] = Field(None, description="私钥大小(bytes)")
    signature_size: Optional[int] = Field(None, description="签名大小(bytes)")
    ciphertext_size: Optional[int] = Field(None, description="密文大小(bytes)")