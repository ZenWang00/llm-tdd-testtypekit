# MBPP迭代修复实验脚本使用指南

## 📋 概述

本套脚本用于运行MBPP数据集的迭代修复实验，支持不同温度参数的大规模测试。

## 🚀 脚本说明

### 1. `run_mbpp_iterative_experiment.py` - 完整实验脚本

**功能**: 运行大规模MBPP迭代修复实验，支持多温度并行测试

**特点**:
- 支持100+任务的完整实验
- 多温度并行执行
- 自动结果分析和报告生成
- MBPP格式转换和评估

**使用方法**:
```bash
# 基本用法 - 100个任务，5个温度，3轮迭代
python run_mbpp_iterative_experiment.py \
  --problem_file benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl \
  --num_tasks 100 \
  --max_rounds 3 \
  --temperatures 0.1 0.3 0.5 0.7 0.9

# 标准执行
python run_mbpp_iterative_experiment.py \
  --problem_file benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl \
  --num_tasks 100 \
  --max_rounds 3 \
  --temperatures 0.1 0.3 0.5 0.7 0.9

# 自定义参数
python run_mbpp_iterative_experiment.py \
  --problem_file benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl \
  --num_tasks 50 \
  --start_task 100 \
  --max_rounds 4 \
  --temperatures 0.2 0.4 0.6 0.8 \
  --model gpt-4o-mini
```

### 2. `run_mbpp_quick_test.py` - 快速测试脚本

**功能**: 快速验证脚本功能，适合小规模测试

**使用方法**:
```bash
# 快速测试 - 5个任务，2个温度
python run_mbpp_quick_test.py \
  --problem_file benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl \
  --num_tasks 5 \
  --temperatures 0.1 0.7
```

## 📊 参数说明

### 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--problem_file` | str | 必需 | MBPP问题文件路径 |
| `--num_tasks` | int | 100 | 处理的任务数量 |
| `--start_task` | int | 0 | 起始任务索引 |
| `--max_rounds` | int | 3 | 最大迭代轮数 |
| `--temperatures` | list | [0.1,0.3,0.5,0.7,0.9] | 温度参数列表 |
| `--model` | str | gpt-4o-mini | 使用的模型 |


### 高级参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--skip_conversion` | flag | False | 跳过MBPP格式转换 |

## 📁 输出结构

实验完成后会生成以下目录结构：

```
mbpp_iterative_experiment_100tasks_3rounds_20250901_123456/
├── experiment_results.json          # 原始实验结果
├── experiment_report.md             # 实验报告
├── T0.1/                           # 温度0.1的结果
│   ├── results/                    # 迭代修复结果
│   │   ├── round_1_code.jsonl      # 第1轮代码
│   │   ├── round_1_results.jsonl   # 第1轮测试结果
│   │   ├── round_2_code.jsonl      # 第2轮代码（如果有）
│   │   ├── round_2_results.jsonl   # 第2轮测试结果（如果有）
│   │   ├── task_*_final_status.json # 各任务最终状态
│   │   ├── mbpp_format_results.jsonl # MBPP格式转换结果
│   │   └── mbpp_evaluation.txt     # MBPP评估结果
├── T0.3/                           # 温度0.3的结果
├── T0.5/                           # 温度0.5的结果
├── T0.7/                           # 温度0.7的结果
└── T0.9/                           # 温度0.9的结果
```

## 📈 结果分析

### 1. 实验报告 (`experiment_report.md`)

包含：
- 实验配置信息
- 各温度的成功率统计
- 执行时间分析
- 错误信息汇总

### 2. 原始结果 (`experiment_results.json`)

包含：
- 每个温度的实验状态
- 执行时间
- 错误信息
- 输出目录路径

### 3. MBPP评估结果

每个温度目录下包含：
- `mbpp_format_results.jsonl`: 转换为MBPP格式的结果
- `mbpp_evaluation.txt`: 使用官方MBPP评估的结果

## ⚡ 性能建议

### 1. 执行策略

```bash
# 标准配置
--num_tasks 100 --max_rounds 3
```

**注意**: 
- 脚本会串行执行不同温度的实验
- 避免同时运行多个实验实例

### 2. 任务数量

```bash
# 小规模测试
--num_tasks 10

# 中等规模
--num_tasks 50

# 大规模实验
--num_tasks 100
```

### 3. 温度选择

```bash
# 快速测试
--temperatures 0.1 0.7

# 完整测试
--temperatures 0.1 0.3 0.5 0.7 0.9

# 自定义范围
--temperatures 0.2 0.4 0.6 0.8
```

## 🔧 故障排除

### 1. 常见错误

**API限制错误**:
```
Rate limit reached for project
```
**解决方案**: 减少任务数量或增加任务间隔

**超时错误**:
```
Process timed out
```
**解决方案**: 减少`num_tasks`或增加超时时间

**文件不存在**:
```
Problem file not found
```
**解决方案**: 检查文件路径是否正确

### 2. 调试模式

使用快速测试脚本进行调试：
```bash
python run_mbpp_quick_test.py \
  --problem_file your_file.jsonl \
  --num_tasks 3 \
  --temperatures 0.1
```

## 📝 使用示例

### 示例1: 完整实验

```bash
# 运行100个任务的完整实验
python run_mbpp_iterative_experiment.py \
  --num_tasks 100 \
  --max_rounds 3 \
  --temperatures 0.1 0.3 0.5 0.7 0.9
```

### 示例2: 快速验证

```bash
# 快速验证脚本功能
python run_mbpp_quick_test.py \
  --num_tasks 5 \
  --temperatures 0.1 0.7
```

### 示例3: 自定义实验

```bash
# 自定义参数实验
python run_mbpp_iterative_experiment.py \
  --num_tasks 50 \
  --start_task 200 \
  --max_rounds 4 \
  --temperatures 0.2 0.4 0.6 0.8 \
  --model gpt-4o-mini
```

## 🎯 最佳实践

1. **先运行快速测试**验证脚本功能
2. **合理设置温度范围**平衡效果和成本
3. **监控API使用量**避免超出限制
4. **定期保存结果**防止数据丢失
5. **避免同时运行多个实验**防止资源冲突

## 📞 支持

如有问题，请检查：
1. 文件路径是否正确
2. API密钥是否有效
3. 网络连接是否正常
4. 系统资源是否充足
