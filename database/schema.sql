-- 算法测试平台数据库结构
-- 创建数据库
CREATE DATABASE IF NOT EXISTS algorithm_testing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE algorithm_testing;

-- 算法信息表
CREATE TABLE algorithms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '算法名称',
    category ENUM('KEM', 'SIGNATURE') NOT NULL COMMENT '算法类别',
    source VARCHAR(50) NOT NULL COMMENT '算法来源库',
    version VARCHAR(20) COMMENT '版本号',
    description TEXT COMMENT '算法描述',
    library_name VARCHAR(100) COMMENT 'C库函数名前缀',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_source (source),
    INDEX idx_is_active (is_active)
) COMMENT '算法信息表';

-- 测试任务表
CREATE TABLE test_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    algorithm_id INT NOT NULL COMMENT '算法ID',
    task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
    parameters TEXT COMMENT '测试参数(JSON格式)',
    test_count INT DEFAULT 100 COMMENT '测试次数',
    status ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING' COMMENT '任务状态',
    error_message TEXT COMMENT '错误信息',
    started_at TIMESTAMP NULL COMMENT '开始时间',
    finished_at TIMESTAMP NULL COMMENT '完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (algorithm_id) REFERENCES algorithms(id) ON DELETE CASCADE,
    INDEX idx_algorithm_id (algorithm_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) COMMENT '测试任务表';

-- 测试结果表
CREATE TABLE test_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '任务ID',
    metric_name VARCHAR(100) NOT NULL COMMENT '指标名称',
    value DOUBLE NOT NULL COMMENT '指标值',
    unit VARCHAR(20) COMMENT '单位',
    test_round INT COMMENT '测试轮次',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_metric_name (metric_name),
    INDEX idx_created_at (created_at),
    INDEX idx_task_metric (task_id, metric_name)
) COMMENT '测试结果表';

-- 报告记录表
CREATE TABLE reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '任务ID',
    report_name VARCHAR(200) NOT NULL COMMENT '报告名称',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_type VARCHAR(10) NOT NULL COMMENT '文件类型',
    file_size INT COMMENT '文件大小(字节)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_file_type (file_type),
    INDEX idx_created_at (created_at)
) COMMENT '报告记录表';

-- 插入默认算法数据
INSERT INTO algorithms (name, category, source, version, description, library_name) VALUES
-- KEM算法
('Kyber512', 'KEM', 'liboqs', '1.0', 'CRYSTALS-Kyber 512位安全级别', 'OQS_KEM_kyber_512'),
('Kyber768', 'KEM', 'liboqs', '1.0', 'CRYSTALS-Kyber 768位安全级别', 'OQS_KEM_kyber_768'),
('Kyber1024', 'KEM', 'liboqs', '1.0', 'CRYSTALS-Kyber 1024位安全级别', 'OQS_KEM_kyber_1024'),

-- 签名算法  
('Dilithium2', 'SIGNATURE', 'liboqs', '1.0', 'CRYSTALS-Dilithium 安全级别2', 'OQS_SIG_dilithium_2'),
('Dilithium3', 'SIGNATURE', 'liboqs', '1.0', 'CRYSTALS-Dilithium 安全级别3', 'OQS_SIG_dilithium_3'),
('Dilithium5', 'SIGNATURE', 'liboqs', '1.0', 'CRYSTALS-Dilithium 安全级别5', 'OQS_SIG_dilithium_5'),
('Falcon512', 'SIGNATURE', 'liboqs', '1.0', 'Falcon 512位签名算法', 'OQS_SIG_falcon_512'),
('Falcon1024', 'SIGNATURE', 'liboqs', '1.0', 'Falcon 1024位签名算法', 'OQS_SIG_falcon_1024');

-- 创建视图：算法测试统计
CREATE VIEW algorithm_test_stats AS
SELECT 
    a.id,
    a.name,
    a.category,
    a.source,
    COUNT(DISTINCT t.id) as total_tests,
    COUNT(DISTINCT CASE WHEN t.status = 'COMPLETED' THEN t.id END) as completed_tests,
    COUNT(DISTINCT CASE WHEN t.status = 'FAILED' THEN t.id END) as failed_tests,
    MAX(t.created_at) as last_test_date
FROM algorithms a
LEFT JOIN test_tasks t ON a.id = t.algorithm_id
WHERE a.is_active = TRUE
GROUP BY a.id, a.name, a.category, a.source;

-- 创建视图：性能指标摘要
CREATE VIEW performance_summary AS
SELECT 
    t.id as task_id,
    t.task_name,
    a.name as algorithm_name,
    a.category,
    AVG(CASE WHEN r.metric_name = 'keygen_time' THEN r.value END) as avg_keygen_time,
    AVG(CASE WHEN r.metric_name = 'encaps_time' THEN r.value END) as avg_encaps_time,
    AVG(CASE WHEN r.metric_name = 'decaps_time' THEN r.value END) as avg_decaps_time,
    AVG(CASE WHEN r.metric_name = 'sign_time' THEN r.value END) as avg_sign_time,
    AVG(CASE WHEN r.metric_name = 'verify_time' THEN r.value END) as avg_verify_time,
    MAX(CASE WHEN r.metric_name = 'success_rate' THEN r.value END) as success_rate,
    MAX(CASE WHEN r.metric_name = 'public_key_size' THEN r.value END) as public_key_size,
    MAX(CASE WHEN r.metric_name = 'private_key_size' THEN r.value END) as private_key_size,
    MAX(CASE WHEN r.metric_name = 'signature_size' THEN r.value END) as signature_size,
    MAX(CASE WHEN r.metric_name = 'ciphertext_size' THEN r.value END) as ciphertext_size
FROM test_tasks t
JOIN algorithms a ON t.algorithm_id = a.id
LEFT JOIN test_results r ON t.id = r.task_id
WHERE t.status = 'COMPLETED'
GROUP BY t.id, t.task_name, a.name, a.category;