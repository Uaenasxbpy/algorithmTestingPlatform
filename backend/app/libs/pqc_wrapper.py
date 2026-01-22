import ctypes
import os
import platform
import time
from typing import Dict, List, Optional, Any
from app.core.config import settings
from app.libs.mock_pqc_wrapper import MockPQCWrapper

class PQCWrapper:
    """后量子密码算法C库封装类"""
    
    def __init__(self, use_mock: bool = False):
        """初始化PQC封装器，默认不使用模拟模式"""
        self.liboqs = None
        self.pqclean = None
        self.use_mock = use_mock
        
        # 检测当前操作系统
        self.system = platform.system().lower()
        self.lib_extension = '.dll' if self.system == 'windows' else '.so' if self.system == 'linux' else '.dylib' if self.system == 'darwin' else '.so'
        
        if use_mock:
            # 使用模拟器进行开发和测试
            print("[INFO] 使用模拟模式进行开发和测试")
            self.mock_wrapper = MockPQCWrapper()
        else:
            # 尝试加载真实的C库
            self._load_libraries()
            if not self.liboqs and not self.pqclean:
                print("[警告] 无法加载真实C库，切换到模拟模式")
                self.use_mock = True
                self.mock_wrapper = MockPQCWrapper()
    
    def _load_libraries(self):
        """根据操作系统加载对应格式的C库"""
        # 获取绝对路径以解决相对路径问题
        liboqs_dir = os.path.abspath(settings.LIBOQS_PATH)
        pqclean_dir = os.path.abspath(settings.PQCLEAN_PATH)
        
        # 尝试不同的库文件名格式
        liboqs_names = [f"liboqs{self.lib_extension}", f"oqs{self.lib_extension}"]
        pqclean_names = [f"pqclean{self.lib_extension}"]
        
        try:
            # 尝试加载 liboqs
            for lib_name in liboqs_names:
                liboqs_path = os.path.join(liboqs_dir, lib_name)
                if os.path.exists(liboqs_path):
                    print(f"[INFO] 尝试从 {liboqs_path} 加载liboqs库")
                    try:
                        self.liboqs = ctypes.CDLL(liboqs_path)
                        self._setup_liboqs_functions()
                        print(f"[INFO] 成功加载liboqs库: {lib_name}")
                        break
                    except Exception as e:
                        print(f"[警告] 加载{lib_name}失败: {e}")
            if not self.liboqs:
                print(f"[警告] liboqs库未找到于 {liboqs_dir}")
        except Exception as e:
            print(f"[错误] 加载liboqs库过程中发生异常: {e}")
            
        try:
            # 尝试加载 PQClean（如果需要）
            for lib_name in pqclean_names:
                pqclean_path = os.path.join(pqclean_dir, lib_name)
                if os.path.exists(pqclean_path):
                    print(f"[INFO] 尝试从 {pqclean_path} 加载PQClean库")
                    try:
                        self.pqclean = ctypes.CDLL(pqclean_path)
                        print(f"[INFO] 成功加载PQClean库: {lib_name}")
                        break
                    except Exception as e:
                        print(f"[警告] 加载{lib_name}失败: {e}")
        except Exception as e:
            print(f"[错误] 加载PQClean库过程中发生异常: {e}")
    
    def _setup_liboqs_functions(self):
        """设置liboqs函数签名"""
        if not self.liboqs:
            return
            
        try:
            # KEM函数
            self.liboqs.OQS_KEM_new.argtypes = [ctypes.c_char_p]
            self.liboqs.OQS_KEM_new.restype = ctypes.c_void_p
            
            self.liboqs.OQS_KEM_keypair.argtypes = [
                ctypes.c_void_p,  # kem
                ctypes.POINTER(ctypes.c_uint8),  # public_key
                ctypes.POINTER(ctypes.c_uint8)   # secret_key
            ]
            self.liboqs.OQS_KEM_keypair.restype = ctypes.c_int
            
            self.liboqs.OQS_KEM_encaps.argtypes = [
                ctypes.c_void_p,  # kem
                ctypes.POINTER(ctypes.c_uint8),  # ciphertext
                ctypes.POINTER(ctypes.c_uint8),  # shared_secret
                ctypes.POINTER(ctypes.c_uint8)   # public_key
            ]
            self.liboqs.OQS_KEM_encaps.restype = ctypes.c_int
            
            self.liboqs.OQS_KEM_decaps.argtypes = [
                ctypes.c_void_p,  # kem
                ctypes.POINTER(ctypes.c_uint8),  # shared_secret
                ctypes.POINTER(ctypes.c_uint8),  # ciphertext
                ctypes.POINTER(ctypes.c_uint8)   # secret_key
            ]
            self.liboqs.OQS_KEM_decaps.restype = ctypes.c_int
            
            self.liboqs.OQS_KEM_free.argtypes = [ctypes.c_void_p]
            self.liboqs.OQS_KEM_free.restype = None
            
            # 签名函数
            self.liboqs.OQS_SIG_new.argtypes = [ctypes.c_char_p]
            self.liboqs.OQS_SIG_new.restype = ctypes.c_void_p
            
            self.liboqs.OQS_SIG_keypair.argtypes = [
                ctypes.c_void_p,  # sig
                ctypes.POINTER(ctypes.c_uint8),  # public_key
                ctypes.POINTER(ctypes.c_uint8)   # secret_key
            ]
            self.liboqs.OQS_SIG_keypair.restype = ctypes.c_int
            
            self.liboqs.OQS_SIG_sign.argtypes = [
                ctypes.c_void_p,  # sig
                ctypes.POINTER(ctypes.c_uint8),  # signature
                ctypes.POINTER(ctypes.c_size_t), # signature_len
                ctypes.POINTER(ctypes.c_uint8),  # message
                ctypes.c_size_t,  # message_len
                ctypes.POINTER(ctypes.c_uint8)   # secret_key
            ]
            self.liboqs.OQS_SIG_sign.restype = ctypes.c_int
            
            self.liboqs.OQS_SIG_verify.argtypes = [
                ctypes.c_void_p,  # sig
                ctypes.POINTER(ctypes.c_uint8),  # message
                ctypes.c_size_t,  # message_len
                ctypes.POINTER(ctypes.c_uint8),  # signature
                ctypes.c_size_t,  # signature_len
                ctypes.POINTER(ctypes.c_uint8)   # public_key
            ]
            self.liboqs.OQS_SIG_verify.restype = ctypes.c_int
            
            self.liboqs.OQS_SIG_free.argtypes = [ctypes.c_void_p]
            self.liboqs.OQS_SIG_free.restype = None
            
        except Exception as e:
            print(f"设置liboqs函数签名失败: {e}")
    
    def get_supported_algorithms(self) -> Dict[str, List[str]]:
        """获取支持的算法列表"""
        if self.use_mock:
            return self.mock_wrapper.get_supported_algorithms()
        
        algorithms = {
            "KEM": [],
            "SIGNATURE": []
        }
        
        # 常见的liboqs KEM算法
        kem_algorithms = [
            "Kyber512", "Kyber768", "Kyber1024",
            "NTRU-HPS-2048-509", "NTRU-HPS-2048-677", 
            "NTRU-HRSS-701", "LightSaber-KEM", "Saber-KEM", "FireSaber-KEM"
        ]
        
        # 常见的liboqs签名算法
        sig_algorithms = [
            "Dilithium2", "Dilithium3", "Dilithium5",
            "Falcon-512", "Falcon-1024", "SPHINCS+-Haraka-128f-robust",
            "SPHINCS+-Haraka-128s-robust", "SPHINCS+-SHA256-128f-robust"
        ]
        
        # 测试算法可用性
        for alg in kem_algorithms:
            if self._test_algorithm_available(alg, "KEM"):
                algorithms["KEM"].append(alg)
        
        for alg in sig_algorithms:
            if self._test_algorithm_available(alg, "SIGNATURE"):
                algorithms["SIGNATURE"].append(alg)
        
        return algorithms
    
    def _test_algorithm_available(self, algorithm_name: str, category: str) -> bool:
        """测试算法是否可用"""
        if not self.liboqs:
            return False
            
        try:
            if category == "KEM":
                kem_name = self._get_kem_name(algorithm_name)
                kem = self.liboqs.OQS_KEM_new(kem_name.encode('utf-8'))
                if kem:
                    self.liboqs.OQS_KEM_free(kem)
                    return True
            elif category == "SIGNATURE":
                sig_name = self._get_sig_name(algorithm_name)
                sig = self.liboqs.OQS_SIG_new(sig_name.encode('utf-8'))
                if sig:
                    self.liboqs.OQS_SIG_free(sig)
                    return True
        except Exception:
            pass
        
        return False
    
    def _get_kem_name(self, algorithm_name: str) -> str:
        """获取KEM算法在liboqs中的名称"""
        name_mapping = {
            "Kyber512": "Kyber512",
            "Kyber768": "Kyber768", 
            "Kyber1024": "Kyber1024",
            "NTRU-HPS-2048-509": "NTRU-HPS-2048-509",
            "NTRU-HPS-2048-677": "NTRU-HPS-2048-677",
            "NTRU-HRSS-701": "NTRU-HRSS-701",
            "LightSaber-KEM": "LightSaber-KEM",
            "Saber-KEM": "Saber-KEM",
            "FireSaber-KEM": "FireSaber-KEM"
        }
        return name_mapping.get(algorithm_name, algorithm_name)
    
    def _get_sig_name(self, algorithm_name: str) -> str:
        """获取签名算法在liboqs中的名称"""
        name_mapping = {
            "Dilithium2": "Dilithium2",
            "Dilithium3": "Dilithium3",
            "Dilithium5": "Dilithium5",
            "Falcon-512": "Falcon-512",
            "Falcon-1024": "Falcon-1024",
            "Falcon512": "Falcon-512",
            "Falcon1024": "Falcon-1024",
            "SPHINCS+-Haraka-128f-robust": "SPHINCS+-Haraka-128f-robust"
        }
        return name_mapping.get(algorithm_name, algorithm_name)
    
    def test_algorithm(self, algorithm_name: str, category: str, source: str) -> bool:
        """测试算法可用性"""
        if self.use_mock:
            return self.mock_wrapper.test_algorithm(algorithm_name, category, source)
        return self._test_algorithm_available(algorithm_name, category)
    
    def test_kem_algorithm(self, algorithm_name: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """测试KEM算法性能"""
        if self.use_mock:
            return self.mock_wrapper.test_kem_algorithm(algorithm_name, library_name)
        
        if not self.liboqs:
            raise Exception("liboqs库未加载")
        
        kem_name = self._get_kem_name(algorithm_name)
        kem = self.liboqs.OQS_KEM_new(kem_name.encode('utf-8'))
        
        if not kem:
            raise Exception(f"无法创建KEM实例: {algorithm_name}")
        
        try:
            # 获取密钥大小信息
            # 注意：这里需要根据实际的liboqs结构体定义来获取大小信息
            # 这是一个简化的示例实现
            
            # 模拟获取密钥大小（实际应该从C结构体中读取）
            key_sizes = self._get_kem_sizes(algorithm_name)
            
            public_key = (ctypes.c_uint8 * key_sizes['public_key_size'])()
            secret_key = (ctypes.c_uint8 * key_sizes['secret_key_size'])()
            ciphertext = (ctypes.c_uint8 * key_sizes['ciphertext_size'])()
            shared_secret_enc = (ctypes.c_uint8 * key_sizes['shared_secret_size'])()
            shared_secret_dec = (ctypes.c_uint8 * key_sizes['shared_secret_size'])()
            
            # 密钥生成测试
            start_time = time.perf_counter()
            result = self.liboqs.OQS_KEM_keypair(kem, public_key, secret_key)
            keygen_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
            
            if result != 0:
                raise Exception("密钥生成失败")
            
            # 封装测试
            start_time = time.perf_counter()
            result = self.liboqs.OQS_KEM_encaps(kem, ciphertext, shared_secret_enc, public_key)
            encaps_time = (time.perf_counter() - start_time) * 1000
            
            if result != 0:
                raise Exception("封装失败")
            
            # 解封装测试
            start_time = time.perf_counter()
            result = self.liboqs.OQS_KEM_decaps(kem, shared_secret_dec, ciphertext, secret_key)
            decaps_time = (time.perf_counter() - start_time) * 1000
            
            if result != 0:
                raise Exception("解封装失败")
            
            # 验证共享密钥是否相同
            shared_secret_match = all(
                shared_secret_enc[i] == shared_secret_dec[i] 
                for i in range(key_sizes['shared_secret_size'])
            )
            
            return {
                'success': shared_secret_match,
                'keygen_time': keygen_time,
                'encaps_time': encaps_time,
                'decaps_time': decaps_time,
                'public_key_size': key_sizes['public_key_size'],
                'private_key_size': key_sizes['secret_key_size'],
                'ciphertext_size': key_sizes['ciphertext_size']
            }
            
        finally:
            self.liboqs.OQS_KEM_free(kem)
    
    def test_signature_algorithm(self, algorithm_name: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """测试签名算法性能"""
        if self.use_mock:
            return self.mock_wrapper.test_signature_algorithm(algorithm_name, library_name)
        
        if not self.liboqs:
            raise Exception("liboqs库未加载")
        
        sig_name = self._get_sig_name(algorithm_name)
        sig = self.liboqs.OQS_SIG_new(sig_name.encode('utf-8'))
        
        if not sig:
            raise Exception(f"无法创建签名实例: {algorithm_name}")
        
        try:
            # 获取密钥大小信息
            key_sizes = self._get_sig_sizes(algorithm_name)
            
            public_key = (ctypes.c_uint8 * key_sizes['public_key_size'])()
            secret_key = (ctypes.c_uint8 * key_sizes['secret_key_size'])()
            
            # 密钥生成测试
            start_time = time.perf_counter()
            result = self.liboqs.OQS_SIG_keypair(sig, public_key, secret_key)
            keygen_time = (time.perf_counter() - start_time) * 1000
            
            if result != 0:
                raise Exception("密钥生成失败")
            
            # 准备要签名的消息
            message = b"Hello, Post-Quantum Cryptography!"
            message_array = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
            
            # 签名测试
            signature = (ctypes.c_uint8 * key_sizes['max_signature_size'])()
            signature_len = ctypes.c_size_t(key_sizes['max_signature_size'])
            
            start_time = time.perf_counter()
            result = self.liboqs.OQS_SIG_sign(
                sig, signature, ctypes.byref(signature_len),
                message_array, len(message), secret_key
            )
            sign_time = (time.perf_counter() - start_time) * 1000
            
            if result != 0:
                raise Exception("签名失败")
            
            # 验证测试
            start_time = time.perf_counter()
            result = self.liboqs.OQS_SIG_verify(
                sig, message_array, len(message),
                signature, signature_len.value, public_key
            )
            verify_time = (time.perf_counter() - start_time) * 1000
            
            success = (result == 0)
            
            return {
                'success': success,
                'keygen_time': keygen_time,
                'sign_time': sign_time,
                'verify_time': verify_time,
                'public_key_size': key_sizes['public_key_size'],
                'private_key_size': key_sizes['secret_key_size'],
                'signature_size': signature_len.value
            }
            
        finally:
            self.liboqs.OQS_SIG_free(sig)
    
    def _get_kem_sizes(self, algorithm_name: str) -> Dict[str, int]:
        """获取KEM算法的密钥大小（硬编码，实际应该从C库读取）"""
        sizes = {
            "Kyber512": {
                'public_key_size': 800,
                'secret_key_size': 1632,
                'ciphertext_size': 768,
                'shared_secret_size': 32
            },
            "Kyber768": {
                'public_key_size': 1184,
                'secret_key_size': 2400,
                'ciphertext_size': 1088,
                'shared_secret_size': 32
            },
            "Kyber1024": {
                'public_key_size': 1568,
                'secret_key_size': 3168,
                'ciphertext_size': 1568,
                'shared_secret_size': 32
            }
        }
        
        return sizes.get(algorithm_name, {
            'public_key_size': 1000,
            'secret_key_size': 2000,
            'ciphertext_size': 1000,
            'shared_secret_size': 32
        })
    
    def _get_sig_sizes(self, algorithm_name: str) -> Dict[str, int]:
        """获取签名算法的密钥大小（硬编码，实际应该从C库读取）"""
        sizes = {
            "Dilithium2": {
                'public_key_size': 1312,
                'secret_key_size': 2528,
                'max_signature_size': 2420
            },
            "Dilithium3": {
                'public_key_size': 1952,
                'secret_key_size': 4000,
                'max_signature_size': 3293
            },
            "Dilithium5": {
                'public_key_size': 2592,
                'secret_key_size': 4864,
                'max_signature_size': 4595
            },
            "Falcon-512": {
                'public_key_size': 897,
                'secret_key_size': 1281,
                'max_signature_size': 690
            },
            "Falcon512": {
                'public_key_size': 897,
                'secret_key_size': 1281,
                'max_signature_size': 690
            },
            "Falcon-1024": {
                'public_key_size': 1793,
                'secret_key_size': 2305,
                'max_signature_size': 1330
            },
            "Falcon1024": {
                'public_key_size': 1793,
                'secret_key_size': 2305,
                'max_signature_size': 1330
            }
        }
        
        return sizes.get(algorithm_name, {
            'public_key_size': 1000,
            'secret_key_size': 2000,
            'max_signature_size': 2000
        })