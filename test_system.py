#!/usr/bin/env python3
"""
算法测试平台 - 快速测试脚本
用于验证系统配置和依赖
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 版本过低，需要 3.8+")
        return False
    print("✅ Python 版本符合要求")
    return True

def check_dependencies():
    """检查 Python 依赖"""
    print("\n检查 Python 依赖...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'sqlalchemy',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 缺失")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺失的包: {', '.join(missing_packages)}")
        print("运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        # 添加项目路径到 Python 路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root / "backend"))
        
        from app.core.config import settings
        from app.db.database import engine
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ 数据库连接成功")
            
            if settings.USE_MYSQL:
                print(f"   使用 MySQL: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
            else:
                print("   使用 SQLite: algorithm_testing.db")
                
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("   将使用 SQLite 作为备用数据库")
        return False

def create_test_data():
    """创建测试数据"""
    print("\n创建数据库表...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        
        from app.db.database import engine, Base
        from app.models.models import Algorithm, TestTask, TestResult, Report
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 检查是否已有算法数据
        from app.db.database import SessionLocal
        db = SessionLocal()
        
        algorithm_count = db.query(Algorithm).count()
        if algorithm_count == 0:
            print("   正在创建默认算法数据...")
            
            # 创建默认算法
            default_algorithms = [
                {
                    "name": "Kyber512",
                    "category": "KEM",
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "CRYSTALS-Kyber 512位安全级别",
                    "library_name": "OQS_KEM_kyber_512",
                    "is_active": True
                },
                {
                    "name": "Dilithium2", 
                    "category": "SIGNATURE",
                    "source": "liboqs",
                    "version": "1.0",
                    "description": "CRYSTALS-Dilithium 安全级别2",
                    "library_name": "OQS_SIG_dilithium_2",
                    "is_active": True
                }
            ]
            
            for alg_data in default_algorithms:
                algorithm = Algorithm(**alg_data)
                db.add(algorithm)
            
            db.commit()
            print("✅ 默认算法数据创建成功")
        else:
            print(f"   已存在 {algorithm_count} 个算法")
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建数据失败: {e}")
        return False

def test_api_server():
    """测试 API 服务器"""
    print("\n测试 API 服务器...")
    
    try:
        import subprocess
        import time
        import requests
        
        # 启动服务器（后台运行）
        print("   启动 FastAPI 服务器...")
        
        project_root = Path(__file__).parent
        backend_dir = project_root / "backend"
        
        # 启动服务器进程
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 测试健康检查端点
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API 服务器启动成功")
                print("   健康检查: http://localhost:8000/health")
                print("   API 文档: http://localhost:8000/docs")
                
                # 终止服务器进程
                process.terminate()
                return True
            else:
                print(f"❌ API 服务器响应异常: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到 API 服务器: {e}")
        
        # 终止服务器进程
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ API 服务器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("     算法测试平台 - 系统检查")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_checks_passed = True
    
    # 1. 检查 Python 版本
    if not check_python_version():
        all_checks_passed = False
    
    # 2. 检查依赖
    if not check_dependencies():
        all_checks_passed = False
        print("\n请先安装依赖:")
        print("cd backend && pip install -r requirements.txt")
        return
    
    # 3. 测试数据库连接
    test_database_connection()
    
    # 4. 创建数据库表和测试数据
    if not create_test_data():
        all_checks_passed = False
    
    # 5. 测试 API 服务器
    if not test_api_server():
        print("   注意: API 服务器测试失败，但不影响手动启动")
    
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 系统检查完成！可以启动项目了")
        print("\n启动方式:")
        print("1. 运行启动脚本: start.bat")
        print("2. 手动启动:")
        print("   后端: cd backend && python main.py")
        print("   前端: cd frontend && npm run dev")
    else:
        print("⚠️  部分检查失败，请解决问题后重试")
    
    print("=" * 50)

if __name__ == "__main__":
    main()