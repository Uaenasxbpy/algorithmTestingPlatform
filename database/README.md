# 数据库配置和使用说明

## MySQL 配置

### 1. 安装 MySQL
确保已安装 MySQL 8.0 或更高版本。

### 2. 创建数据库和用户
```sql
-- 创建数据库
CREATE DATABASE algorithm_testing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'alg_test'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON algorithm_testing.* TO 'alg_test'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 执行建表脚本
```bash
mysql -u root -p algorithm_testing < schema.sql
```

## 表结构说明

### algorithms 表
存储后量子密码算法的基本信息：
- `id`: 主键，自增
- `name`: 算法名称（如 Kyber512）
- `category`: 算法类别（KEM 或 SIGNATURE）
- `source`: 算法来源库（如 liboqs）
- `version`: 版本号
- `description`: 算法描述
- `library_name`: C库中的函数名前缀
- `is_active`: 是否激活

### test_tasks 表
存储测试任务信息：
- `id`: 主键，自增
- `algorithm_id`: 关联的算法ID
- `task_name`: 任务名称
- `parameters`: 测试参数（JSON格式）
- `test_count`: 测试次数
- `status`: 任务状态（PENDING, RUNNING, COMPLETED, FAILED）
- `error_message`: 错误信息
- `started_at`: 开始时间
- `finished_at`: 完成时间

### test_results 表
存储测试结果数据：
- `id`: 主键，自增
- `task_id`: 关联的任务ID
- `metric_name`: 指标名称（如 keygen_time, encaps_time等）
- `value`: 指标值
- `unit`: 单位
- `test_round`: 测试轮次

### reports 表
存储生成的报告信息：
- `id`: 主键，自增
- `task_id`: 关联的任务ID
- `report_name`: 报告名称
- `file_path`: 文件路径
- `file_type`: 文件类型（PDF, CSV等）
- `file_size`: 文件大小

## 性能指标说明

### KEM 算法指标
- `keygen_time`: 密钥生成时间（毫秒）
- `encaps_time`: 封装时间（毫秒）
- `decaps_time`: 解封装时间（毫秒）
- `public_key_size`: 公钥大小（字节）
- `private_key_size`: 私钥大小（字节）
- `ciphertext_size`: 密文大小（字节）
- `success_rate`: 成功率（百分比）

### 签名算法指标
- `keygen_time`: 密钥生成时间（毫秒）
- `sign_time`: 签名时间（毫秒）
- `verify_time`: 验证时间（毫秒）
- `public_key_size`: 公钥大小（字节）
- `private_key_size`: 私钥大小（字节）
- `signature_size`: 签名大小（字节）
- `success_rate`: 成功率（百分比）

## 视图说明

### algorithm_test_stats
算法测试统计视图，提供每个算法的测试次数、成功/失败次数等统计信息。

### performance_summary  
性能指标摘要视图，提供每个任务的各项性能指标平均值。

## 索引优化

数据库已针对常用查询创建了索引：
- 算法表：name, category, source, is_active
- 任务表：algorithm_id, status, created_at
- 结果表：task_id, metric_name, created_at
- 报告表：task_id, file_type, created_at

## 备份和维护

建议定期备份数据库：
```bash
mysqldump -u root -p algorithm_testing > backup_$(date +%Y%m%d).sql
```