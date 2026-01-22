from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class AlgorithmCategory(str, enum.Enum):
    KEM = "KEM"  # 密钥封装机制
    SIGNATURE = "SIGNATURE"  # 数字签名

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"  # 待运行
    RUNNING = "RUNNING"  # 运行中
    COMPLETED = "COMPLETED"  # 完成
    FAILED = "FAILED"  # 失败

class Algorithm(Base):
    """算法信息表"""
    __tablename__ = "algorithms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(Enum(AlgorithmCategory), nullable=False)
    source = Column(String(50), nullable=False)  # liboqs, pqclean等
    version = Column(String(20))
    description = Column(Text)
    library_name = Column(String(100))  # C库中的函数名前缀
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    test_tasks = relationship("TestTask", back_populates="algorithm")

class TestTask(Base):
    """测试任务表"""
    __tablename__ = "test_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    algorithm_id = Column(Integer, ForeignKey("algorithms.id"), nullable=False)
    task_name = Column(String(200), nullable=False)
    parameters = Column(Text)  # JSON格式存储测试参数
    test_count = Column(Integer, default=100)  # 测试次数
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    algorithm = relationship("Algorithm", back_populates="test_tasks")
    results = relationship("TestResult", back_populates="task", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="task", cascade="all, delete-orphan")

class TestResult(Base):
    """测试结果表"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)  # 指标名称
    value = Column(Float, nullable=False)  # 指标值
    unit = Column(String(20))  # 单位
    test_round = Column(Integer)  # 测试轮次
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    task = relationship("TestTask", back_populates="results")

class Report(Base):
    """报告记录表"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"), nullable=False)
    report_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # PDF, CSV等
    file_size = Column(Integer)  # 文件大小（字节）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    task = relationship("TestTask", back_populates="reports")