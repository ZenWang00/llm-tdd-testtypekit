# 新Pipeline架构说明

## 概述

新的Pipeline架构将原来的两阶段TDD流程拆分为独立的测试生成和代码生成阶段，提高了调试效率和数据管理能力。

## 架构设计

### 1. 现有Pipeline（保持不变）
- `batch_mbpp_tdd.py` - MBPP完整TDD流程
- `batch_humaneval_tdd.py` - HumanEval完整TDD流程

### 2. 新Pipeline（新增）
- `batch_mbpp_test_only.py` - MBPP测试专用Pipeline
- `batch_humaneval_test_only.py` - HumanEval测试专用Pipeline
- `batch_mbpp_code_only.py` - MBPP代码专用Pipeline
- `batch_humaneval_code_only.py` - HumanEval代码专用Pipeline

## 工作流程

### 阶段1：测试生成
```bash
# MBPP测试生成
python pipelines/batch_mbpp_test_only.py --num_tasks 100

# HumanEval测试生成
python pipelines/batch_humaneval_test_only.py --num_tasks 164
```

**输出文件格式**：
```
test_only_mbpp_batch_100_tasks_gpt-4o-mini_20250831_143022.jsonl
test_only_humaneval_batch_164_tasks_gpt-4o-mini_20250831_143022.jsonl
```

**数据字段**：
```json
{
    "task_id": "1",
    "prompt": "问题描述",
    "reference_code": "参考代码",
    "generated_tests": "生成的测试代码",
    "method": "test_only_mbpp",
    "model": "gpt-4o-mini",
    "timestamp": "2025-08-31T...",
    "stage": "test_generation_only"
}
```

### 阶段2：代码生成
```bash
# MBPP代码生成
python pipelines/batch_mbpp_code_only.py --test_file test_only_mbpp_batch_100_tasks_gpt-4o-mini_20250831_143022.jsonl

# HumanEval代码生成
python pipelines/batch_humaneval_code_only.py --test_file test_only_humaneval_batch_164_tasks_gpt-4o-mini_20250831_143022.jsonl
```

**输出文件格式**：
```
code_only_mbpp_batch_100_tasks_gpt-4o-mini_20250831_143156.jsonl
code_only_humaneval_batch_100_tasks_gpt-4o-mini_20250831_143156.jsonl
```

**数据字段**：
```json
{
    "task_id": "1",
    "prompt": "问题描述",
    "completion": "生成的代码实现",
    "method": "code_only_mbpp",
    "model": "gpt-4o-mini",
    "timestamp": "2025-08-31T...",
    "test_list": "原始测试列表",
    "challenge_test_list": "挑战测试列表",
    "reference_code": "参考代码",
    "generated_tests": "生成的测试代码",
    "stage": "code_generation_only"
}
```

## 关键特性

### 1. 数据复用
- 测试生成结果可以重复使用
- 支持部分任务重新生成代码
- 便于调试和一致性检验

### 2. 文件命名规范
- **MBPP系列**：`test_only_mbpp_batch_*.jsonl`, `code_only_mbpp_batch_*.jsonl`
- **HumanEval系列**：`test_only_humaneval_batch_*.jsonl`, `code_only_humaneval_batch_*.jsonl`

### 3. 数据完整性
- 保留所有原始字段
- 新增`stage`字段标识处理阶段
- 新增`method`字段标识Pipeline类型

## 使用场景

### 1. 调试测试生成
```bash
# 生成少量测试进行调试
python pipelines/batch_mbpp_test_only.py --num_tasks 5

# 分析测试质量
python analyze_tdd_comprehensive.py test_only_mbpp_batch_5_tasks_gpt-4o-mini_*.jsonl
```

### 2. 一致性检验
```bash
# 生成多组测试
python pipelines/batch_mbpp_test_only.py --num_tasks 10
python pipelines/batch_mbpp_test_only.py --num_tasks 10

# 比较测试一致性
# （需要实现一致性检验脚本）
```

### 3. 代码生成优化
```bash
# 使用高质量测试生成代码
python pipelines/batch_mbpp_code_only.py --test_file high_quality_tests.jsonl

# 评估代码质量
python analyze_mbpp_results_fixed.py code_only_mbpp_batch_*.jsonl
```

## 优势

1. **调试效率**：测试生成失败时，不需要重新生成代码
2. **数据管理**：测试和代码分离存储，便于管理
3. **一致性检验**：可以多次生成测试进行质量对比
4. **资源节约**：避免重复的API调用
5. **灵活性**：支持不同的测试和代码生成策略

## 注意事项

1. 确保测试文件路径正确
2. 代码生成Pipeline依赖测试文件的完整性
3. 文件名包含时间戳，避免覆盖
4. 建议先小规模测试，再大规模运行

## 下一步计划

1. 实现一致性检验脚本（Jaccard相似性）
2. 添加测试质量评估指标
3. 实现测试和代码生成的关联分析
4. 优化错误处理和日志记录
