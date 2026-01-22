from pydantic import BaseSettings, Field
from typing import Optional
import os
import platform

class Settings(BaseSettings):
    # 环境检测
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # 数据库配置 - 优先从环境变量获取
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DATABASE_HOST: str = Field(default="localhost", env="DATABASE_HOST")
    DATABASE_PORT: int = Field(default=3306, env="DATABASE_PORT")
    DATABASE_USER: str = Field(default="alg_test", env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field(default="", env="DATABASE_PASSWORD")
    DATABASE_NAME: str = Field(default="algorithm_testing", env="DATABASE_NAME")
    
    # 数据库类型配置
    USE_MYSQL: bool = Field(default=True, env="USE_MYSQL")  # 默认为使用 MySQL
    
    # JWT配置
    SECRET_KEY: str = Field(default="", env="SECRET_KEY")  # 生产环境必须通过环境变量设置
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # C库路径配置 - 考虑不同操作系统
    LIBOQS_PATH: str = Field(default=os.path.abspath("../libs/liboqs"), env="LIBOQS_PATH")
    PQCLEAN_PATH: str = Field(default=os.path.abspath("../libs/pqclean"), env="PQCLEAN_PATH")
    C_LIBRARY_PATH: str = Field(default=os.path.abspath("../libs"), env="C_LIBRARY_PATH")  # 通用C库路径
    
    # 模拟模式配置
    USE_MOCK_MODE: bool = Field(default=True, env="USE_MOCK_MODE")  # 默认使用模拟模式
    USE_MOCK: bool = Field(default=True, env="USE_MOCK")  # 兼容旧名称
    
    # 报告存储路径
    REPORTS_DIR: str = Field(default=os.path.abspath("../reports"), env="REPORTS_DIR")
    
    # 其他配置
    DEBUG: bool = Field(default=False, env="DEBUG")  # 默认为False，生产环境更安全
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "算法测试平台"
    VERSION: str = "1.0.0"
    
    # 日志配置
    LOGGER_NAME: str = Field(default="algorithm_testing_platform", env="LOGGER_NAME")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")  # 可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # CORS配置
    ALLOWED_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"], 
        env="ALLOWED_ORIGINS"
    )
    
    # 查询和测试限制配置
    MAX_QUERY_LIMIT: int = Field(default=1000, env="MAX_QUERY_LIMIT")  # 最大查询返回数量
    MAX_TEST_COUNT: int = Field(default=10000, env="MAX_TEST_COUNT")  # 最大测试次数
    
    class Config:
        case_sensitive = True
        # 允许从.env文件加载配置
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_database_url(self) -> str:
        """获取数据库连接 URL，优先使用DATABASE_URL环境变量"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        elif self.USE_MYSQL:
            # 使用参数化构建连接字符串，避免SQL注入风险
            return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?charset=utf8mb4"
        else:
            # SQLite配置
            return "sqlite:///./algorithm_testing.db"

# 初始化设置
settings = Settings()

# 开发环境默认配置
if settings.ENVIRONMENT == "development" and not settings.SECRET_KEY:
    settings.SECRET_KEY = "dev-secret-key-change-in-production"
    settings.DEBUG = True
    print("[INFO] 使用开发环境默认配置")

# 尝试连接 MySQL，如果失败则使用 SQLite
def initialize_database_connection():
    """初始化数据库连接，MySQL连接失败则回退到SQLite"""
    if settings.USE_MYSQL and not settings.DATABASE_URL:
        try:
            import pymysql
            connection = pymysql.connect(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                connect_timeout=5
            )
            connection.close()
            print("[INFO] 成功连接到 MySQL 数据库")
        except pymysql.MySQLError as e:
            print(f"[WARNING] 无法连接到 MySQL: {e}")
            print("[INFO] 切换到 SQLite 数据库")
            settings.USE_MYSQL = False
        except ImportError:
            print("[WARNING] pymysql模块未安装")
            print("[INFO] 切换到 SQLite 数据库")
            settings.USE_MYSQL = False
        except Exception as e:
            print(f"[WARNING] 数据库连接异常: {e}")
            print("[INFO] 切换到 SQLite 数据库")
            settings.USE_MYSQL = False

# 初始化数据库连接
initialize_database_connection()