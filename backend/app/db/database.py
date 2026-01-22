from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# 创建数据库引擎
if settings.USE_MYSQL:
    engine = create_engine(
        settings.get_database_url(),
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG,
        future=True
    )
else:
    # SQLite配置，解决线程安全问题
    engine = create_engine(
        settings.get_database_url(),
        echo=settings.DEBUG,
        future=True,
        # SQLite特定配置
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 使用静态连接池
        pool_pre_ping=True
    )

# 创建SessionLocal类
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # 避免在commit后对象过期
)

# 创建Base类
Base = declarative_base()

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception:
            # 忽略关闭连接时的错误
            pass