# LLM-TDD 实验报告
生成时间: 2025-08-31 13:47:54

## 1. Pipeline运行摘要

| Pipeline Type | Dataset | Tasks | Date | Method | Stage | Status |
|----------------|---------|-------|------|--------|-------|--------|
| Full TDD | HumanEval | 10 | 2025-08-30 | tdd_humaneval | N/A | ✅ |
| Full TDD | HumanEval | 164 | 2025-08-30 | tdd_humaneval | N/A | ✅ |
| Code Generation | MBPP | 2 | 2025-08-31 | code_only_mbpp | code_generation_only | ✅ |
| Consistency Check | MBPP | 2 | 2025-08-31 | consistency_check_mbpp | consistency_check | ❌ |
| Consistency Check | MBPP | 2 | 2025-08-31 | consistency_check_mbpp | consistency_check | ✅ |
| Full TDD | MBPP | 100 | 2025-08-31 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-29 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 500 | 2025-08-29 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 500 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Full TDD | MBPP | 974 | 2025-08-30 | tdd_mbpp | N/A | ✅ |
| Test Generation | MBPP | 2 | 2025-08-31 | test_only_mbpp | test_generation_only | ✅ |

## 2. 测试质量分析

### 2.1 质量指标汇总

| Dataset | Tasks | Date | Contract Score | Heuristic Score | Status |
|---------|-------|------|----------------|-----------------|--------|
| MBPP | 100 | 2025-08-31 | N/A | N/A | ✅ |
| MBPP | 1 | 2025-08-30 | N/A | N/A | ✅ |
| MBPP | 2 | 2025-08-31 | N/A | N/A | ✅ |

### 2.2 详细分析结果

**tdd_mbpp_batch_100_tasks_gpt-4o-mini_20250831_120953_comprehensive_report.txt**

```
详细分析内容请查看原文件
```

**tdd_mbpp_batch_1_tasks_gpt-4o-mini_20250830_102517_comprehensive_report.txt**

```
详细分析内容请查看原文件
```

**test_only_mbpp_batch_2_tasks_gpt-4o-mini_20250831_132129_comprehensive_report.txt**

```
详细分析内容请查看原文件
```

## 3. 一致性检查结果

### 3.1 一致性指标汇总

| Dataset | Tasks | Runs | Date | Avg Jaccard | Structure Consistency | Status |
|---------|-------|------|------|--------------|----------------------|--------|
| MBPP | 2 | 3 | 2025-08-31 | 0.737 | 0.680 | ✅ |

### 3.2 详细一致性分析

**consistency_check_mbpp_2_tasks_3_runs_gpt-4o-mini_20250831_132938_analysis.json**

- 总任务数: 2
- 分析任务数: 2
- 平均Jaccard相似性: 0.737
- 平均结构一致性: 0.680

**任务级别一致性:**

  - 任务 1:
    - 运行次数: 3
    - 有效运行: 3
    - 平均Jaccard: 0.715
    - 结构一致性: 0.680

  - 任务 2:
    - 运行次数: 3
    - 有效运行: 3
    - 平均Jaccard: 0.759
    - 结构一致性: 0.680

## 4. 状态说明

- ✅ 成功: 所有指标都达到预期
- ⚠️ 警告: 部分指标未达到预期
- ❌ 失败: 主要指标未达到预期

## 5. 文件统计

- 测试生成: 2 个文件
- 代码生成: 1 个文件
- 完整TDD: 17 个文件
- 一致性检查: 3 个文件
- 质量分析报告: 3 个文件
- 一致性分析: 1 个文件
