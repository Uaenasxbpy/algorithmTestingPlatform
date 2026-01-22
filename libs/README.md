# liboqs 库安装和配置指南

## 概述

liboqs 是一个开源的后量子密码算法库，支持多种NIST标准化的PQC算法。本项目使用 liboqs 来实现实际的算法测试。

## 安装方式

### 方式一：从源码编译（推荐）

1. **安装依赖**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential cmake git

# Windows (使用 MSYS2)
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake git
```

2. **克隆和编译 liboqs**
```bash
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=../../libs/liboqs ..
make -j4
make install
```

3. **复制库文件到项目**
```bash
# Linux
cp lib/liboqs.so ../../../libs/liboqs/

# Windows
cp bin/oqs.dll ../../../libs/liboqs/liboqs.dll
```

### 方式二：使用预编译版本

从 [liboqs Releases](https://github.com/open-quantum-safe/liboqs/releases) 下载预编译版本。

### 方式三：Docker 方式

```bash
# 使用官方Docker镜像
docker pull openquantumsafe/liboqs
docker run -it openquantumsafe/liboqs /bin/bash

# 在容器中复制库文件
docker cp container_id:/usr/local/lib/liboqs.so ./libs/liboqs/
```

## 支持的算法

### KEM 算法
- **Kyber**: Kyber512, Kyber768, Kyber1024
- **NTRU**: NTRU-HPS-2048-509, NTRU-HPS-2048-677, NTRU-HRSS-701
- **Saber**: LightSaber-KEM, Saber-KEM, FireSaber-KEM
- **FrodoKEM**: FrodoKEM-640-AES, FrodoKEM-976-AES, FrodoKEM-1344-AES
- **BIKE**: BIKE-L1, BIKE-L3
- **HQC**: HQC-128, HQC-192, HQC-256

### 签名算法
- **Dilithium**: Dilithium2, Dilithium3, Dilithium5
- **Falcon**: Falcon-512, Falcon-1024
- **SPHINCS+**: 多个变体
- **Rainbow**: Rainbow-I-Classic, Rainbow-III-Classic, Rainbow-V-Classic
- **Picnic**: 多个变体

## 配置说明

### 环境变量配置

在 `backend/app/core/config.py` 中配置库路径：

```python
# C库路径配置
LIBOQS_PATH: str = "../libs/liboqs"
PQCLEAN_PATH: str = "../libs/pqclean"
```

### 库文件结构

```
libs/
├── liboqs/
│   ├── liboqs.so          # Linux 共享库
│   ├── liboqs.dll         # Windows 动态库
│   ├── include/           # 头文件（可选）
│   └── README.md          # 库说明
└── bindings/
    └── python/            # Python 绑定（可选）
```

## 测试安装

创建测试脚本验证安装：

```python
# test_liboqs.py
import ctypes
import os

def test_liboqs():
    try:
        # 加载库
        lib_path = "libs/liboqs/liboqs.so"  # Linux
        # lib_path = "libs/liboqs/liboqs.dll"  # Windows
        
        if not os.path.exists(lib_path):
            print(f"库文件不存在: {lib_path}")
            return False
        
        lib = ctypes.CDLL(lib_path)
        
        # 测试 KEM
        lib.OQS_KEM_new.argtypes = [ctypes.c_char_p]
        lib.OQS_KEM_new.restype = ctypes.c_void_p
        
        kem = lib.OQS_KEM_new(b"Kyber512")
        if kem:
            print("✓ KEM 测试成功")
            lib.OQS_KEM_free(kem)
        else:
            print("✗ KEM 测试失败")
            return False
        
        # 测试签名
        lib.OQS_SIG_new.argtypes = [ctypes.c_char_p]
        lib.OQS_SIG_new.restype = ctypes.c_void_p
        
        sig = lib.OQS_SIG_new(b"Dilithium2")
        if sig:
            print("✓ 签名测试成功")
            lib.OQS_SIG_free(sig)
        else:
            print("✗ 签名测试失败")
            return False
        
        print("🎉 liboqs 安装验证成功!")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    test_liboqs()
```

## 故障排除

### 常见问题

1. **库文件未找到**
   - 检查路径配置是否正确
   - 确认库文件存在且有执行权限

2. **符号未找到**
   - 确认使用的 liboqs 版本
   - 检查函数名是否正确

3. **权限问题**
   ```bash
   chmod +x libs/liboqs/liboqs.so
   ```

4. **Windows DLL 问题**
   - 确保所有依赖的DLL都在系统路径中
   - 可能需要安装 Visual C++ Redistributable

### 调试模式

启用详细日志：

```python
# 在 config.py 中
DEBUG: bool = True
LIBOQS_DEBUG: bool = True
```

### 回退到模拟模式

如果无法安装真实的 liboqs 库，系统会自动回退到模拟模式：

```python
# 在 PQCWrapper 初始化时
wrapper = PQCWrapper(use_mock=True)  # 强制使用模拟模式
```

## 性能优化

### 编译优化

```bash
cmake -DCMAKE_BUILD_TYPE=Release \
      -DOQS_USE_OPENSSL=ON \
      -DOQS_BUILD_ONLY_LIB=ON \
      ..
```

### 运行时优化

1. **并行测试**: 可以并行运行多个算法测试
2. **内存池**: 重用内存分配以提高性能
3. **缓存**: 缓存密钥生成结果

## 更多资源

- [liboqs 官方文档](https://github.com/open-quantum-safe/liboqs)
- [Open Quantum Safe 项目](https://openquantumsafe.org/)
- [NIST PQC 标准化](https://csrc.nist.gov/projects/post-quantum-cryptography)