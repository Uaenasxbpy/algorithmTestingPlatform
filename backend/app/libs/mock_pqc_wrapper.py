import time
import random
from typing import Dict, List, Optional, Any

class MockPQCWrapper:
    """模拟的PQC库封装，用于开发和测试"""
    
    def __init__(self):
        self.supported_algorithms = {
            "KEM": ["Kyber512", "Kyber768", "Kyber1024"],
            "SIGNATURE": ["Dilithium2", "Dilithium3", "Dilithium5", "Falcon512", "Falcon1024"]
        }
    
    def get_supported_algorithms(self) -> Dict[str, List[str]]:
        """获取支持的算法列表"""
        return self.supported_algorithms
    
    def test_algorithm(self, algorithm_name: str, category: str, source: str) -> bool:
        """测试算法可用性"""
        if category == "KEM":
            return algorithm_name in self.supported_algorithms["KEM"]
        elif category == "SIGNATURE":
            return algorithm_name in self.supported_algorithms["SIGNATURE"]
        return False
    
    def test_kem_algorithm(self, algorithm_name: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """模拟KEM算法测试"""
        if algorithm_name not in self.supported_algorithms["KEM"]:
            raise Exception(f"不支持的KEM算法: {algorithm_name}")
        
        # 模拟测试时间（添加一些随机性）
        base_keygen_time = 0.5
        base_encaps_time = 0.3
        base_decaps_time = 0.3
        
        # 不同算法有不同的基准时间
        if "512" in algorithm_name:
            multiplier = 1.0
        elif "768" in algorithm_name:
            multiplier = 1.5
        elif "1024" in algorithm_name:
            multiplier = 2.0
        else:
            multiplier = 1.0
        
        # 添加随机变化（±20%）
        def add_variance(base_time):
            variance = random.uniform(0.8, 1.2)
            return base_time * multiplier * variance
        
        # 模拟实际测试时间
        time.sleep(0.001)  # 模拟一些计算时间
        
        # 获取密钥大小
        sizes = self._get_kem_sizes(algorithm_name)
        
        return {
            'success': True,  # 模拟测试始终成功
            'keygen_time': add_variance(base_keygen_time),
            'encaps_time': add_variance(base_encaps_time),
            'decaps_time': add_variance(base_decaps_time),
            'public_key_size': sizes['public_key_size'],
            'private_key_size': sizes['secret_key_size'],
            'ciphertext_size': sizes['ciphertext_size']
        }
    
    def test_signature_algorithm(self, algorithm_name: str, library_name: Optional[str] = None) -> Dict[str, Any]:
        """模拟签名算法测试"""
        if algorithm_name not in self.supported_algorithms["SIGNATURE"]:
            raise Exception(f"不支持的签名算法: {algorithm_name}")
        
        # 模拟测试时间
        base_keygen_time = 0.8
        base_sign_time = 0.6
        base_verify_time = 0.2
        
        # 不同算法有不同的性能特征
        if "Dilithium" in algorithm_name:
            if "2" in algorithm_name:
                multiplier = 1.0
            elif "3" in algorithm_name:
                multiplier = 1.4
            elif "5" in algorithm_name:
                multiplier = 2.0
            else:
                multiplier = 1.0
        elif "Falcon" in algorithm_name:
            if "512" in algorithm_name:
                multiplier = 0.8
            elif "1024" in algorithm_name:
                multiplier = 1.2
            else:
                multiplier = 1.0
        else:
            multiplier = 1.0
        
        def add_variance(base_time):
            variance = random.uniform(0.8, 1.2)
            return base_time * multiplier * variance
        
        # 模拟实际测试时间
        time.sleep(0.001)
        
        # 获取密钥大小
        sizes = self._get_sig_sizes(algorithm_name)
        
        return {
            'success': True,
            'keygen_time': add_variance(base_keygen_time),
            'sign_time': add_variance(base_sign_time),
            'verify_time': add_variance(base_verify_time),
            'public_key_size': sizes['public_key_size'],
            'private_key_size': sizes['secret_key_size'],
            'signature_size': sizes['max_signature_size']
        }
    
    def _get_kem_sizes(self, algorithm_name: str) -> Dict[str, int]:
        """获取KEM算法的密钥大小"""
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
        """获取签名算法的密钥大小"""
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
            "Falcon512": {
                'public_key_size': 897,
                'secret_key_size': 1281,
                'max_signature_size': 690
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