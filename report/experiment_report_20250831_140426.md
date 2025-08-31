# LLM-TDD Experiment Report
Generated: 2025-08-31 14:04:26

## 1. Pipeline Execution Summary

| Pipeline Type | Dataset | Tasks | Date | Method | Stage | Parameters | Status |
|----------------|---------|-------|------|--------|-------|------------|--------|
| Full TDD | HumanEval | 10 | 2025-08-30 | tdd_humaneval | N/A | N/A | ✅ |
| Full TDD | HumanEval | 164 | 2025-08-30 | tdd_humaneval | N/A | N/A | ✅ |
| Code Generation | MBPP | 2 | 2025-08-31 | code_only_mbpp | code_generation_only | N/A | ✅ |
| Consistency Check | MBPP | 2 | 2025-08-31 | consistency_check_mbpp | consistency_check | T:0.1,0.3,0.5, S:42,123,456 | ❌ |
| Consistency Check | MBPP | 2 | 2025-08-31 | consistency_check_mbpp | consistency_check | T:0.1,0.3,0.5, S:42,123,456 | ✅ |
| Full TDD | MBPP | 100 | 2025-08-31 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-29 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 1 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 500 | 2025-08-29 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 500 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Full TDD | MBPP | 974 | 2025-08-30 | tdd_mbpp | N/A | N/A | ✅ |
| Test Generation | MBPP | 2 | 2025-08-31 | test_only_mbpp | test_generation_only | N/A | ✅ |

## 2. Test Quality Analysis

### 2.1 Quality Metrics Summary

| Dataset | Tasks | Date | Contract Score | Heuristic Score | Status |
|---------|-------|------|----------------|-----------------|--------|
| MBPP | 100 | 2025-08-31 | 0.968 | 0.544 | ✅ |
| MBPP | 1 | 2025-08-30 | 0.000 | 0.000 | ❌ |
| MBPP | 2 | 2025-08-31 | 0.800 | 0.516 | ✅ |

### 2.2 Detailed Analysis Results

**tdd_mbpp_batch_100_tasks_gpt-4o-mini_20250831_120953_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 100
Contract Compliance Rate: 93.0%
Average Contract Score: 0.968
Average Heuristic Score: 0.544
```

**tdd_mbpp_batch_1_tasks_gpt-4o-mini_20250830_102517_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 1
Contract Compliance Rate: 0.0%
Average Contract Score: 0.000
Average Heuristic Score: 0.000
```

**test_only_mbpp_batch_2_tasks_gpt-4o-mini_20250831_132129_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 2
Contract Compliance Rate: 50.0%
Average Contract Score: 0.800
Average Heuristic Score: 0.516
```

## 3. Consistency Check Results

### 3.1 Consistency Metrics Summary

| Dataset | Tasks | Runs | Date | Avg Jaccard | Structure Consistency | Status |
|---------|-------|------|------|--------------|----------------------|--------|
| MBPP | 2 | 3 | 2025-08-31 | 0.737 | 0.680 | ✅ |

### 3.2 Detailed Consistency Analysis

**consistency_check_mbpp_2_tasks_3_runs_gpt-4o-mini_20250831_132938_analysis.json**

- Total Tasks: 2
- Analyzed Tasks: 2
- Average Jaccard Similarity: 0.737
- Average Structure Consistency: 0.680

**Task-Level Consistency:**

  - Task 1:
    - Number of Runs: 3
    - Valid Runs: 3
    - Average Jaccard: 0.715
    - Structure Consistency: 0.680

  - Task 2:
    - Number of Runs: 3
    - Valid Runs: 3
    - Average Jaccard: 0.759
    - Structure Consistency: 0.680

## 4. Status Description

- ✅ Success: All metrics meet expectations
- ⚠️ Warning: Some metrics do not meet expectations
- ❌ Failure: Major metrics do not meet expectations

## 5. File Statistics

- Test Generation: 2 files
- Code Generation: 1 files
- Full TDD: 17 files
- Consistency Check: 3 files
- Quality Analysis Reports: 3 files
- Consistency Analysis: 1 files
