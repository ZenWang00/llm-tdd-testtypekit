# LLM-TDD Experiment Report
Generated: 2025-09-01 11:11:56

## 1. Pipeline Execution Summary

| Pipeline Type | Dataset | Tasks | Date | Method | Stage | Parameters | Status |
|----------------|---------|-------|------|--------|-------|------------|--------|
| Test Generation | MBPP | 200 | 2025-08-31 | test_only_mbpp | test_generation_only | T:0.1 | ✅ |
| Test Generation | MBPP | 200 | 2025-08-31 | test_only_mbpp | test_generation_only | T:0.3 | ✅ |
| Test Generation | MBPP | 200 | 2025-08-31 | test_only_mbpp | test_generation_only | T:0.5 | ✅ |
| Test Generation | MBPP | 200 | 2025-08-31 | test_only_mbpp | test_generation_only | T:0.7 | ✅ |
| Test Generation | MBPP | 200 | 2025-08-31 | test_only_mbpp | test_generation_only | T:0.9 | ✅ |

## 2. Test Quality Analysis

### 2.1 Quality Metrics Summary

| Dataset | Tasks | Date | Parameters | Contract Score | Heuristic Score | Status |
|---------|-------|------|------------|----------------|-----------------|--------|
| MBPP | 200 | 2025-08-31 | T:0.0 | 0.960 | 0.539 | ✅ |
| MBPP | 200 | 2025-08-31 | T:0.0 | 0.959 | 0.539 | ✅ |
| MBPP | 200 | 2025-08-31 | T:0.0 | 0.958 | 0.543 | ✅ |
| MBPP | 200 | 2025-08-31 | T:0.0 | 0.958 | 0.533 | ✅ |
| MBPP | 200 | 2025-08-31 | T:0.0 | 0.958 | 0.531 | ✅ |

### 2.2 Detailed Analysis Results

**test_only_mbpp_batch_200_tasks_T0.1_gpt-4o-mini_20250831_171654_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 200
Contract Compliance Rate: 91.5%
Average Contract Score: 0.960
Average Heuristic Score: 0.539
```

**test_only_mbpp_batch_200_tasks_T0.3_gpt-4o-mini_20250831_175437_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 200
Contract Compliance Rate: 91.5%
Average Contract Score: 0.959
Average Heuristic Score: 0.539
```

**test_only_mbpp_batch_200_tasks_T0.5_gpt-4o-mini_20250831_181550_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 200
Contract Compliance Rate: 90.5%
Average Contract Score: 0.958
Average Heuristic Score: 0.543
```

**test_only_mbpp_batch_200_tasks_T0.7_gpt-4o-mini_20250831_183809_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 200
Contract Compliance Rate: 91.0%
Average Contract Score: 0.958
Average Heuristic Score: 0.533
```

**test_only_mbpp_batch_200_tasks_T0.9_gpt-4o-mini_20250831_185751_comprehensive_report.txt**

```
EXECUTIVE SUMMARY
------------------------------
Total Tests Analyzed: 200
Contract Compliance Rate: 92.0%
Average Contract Score: 0.958
Average Heuristic Score: 0.531
```

## 3. Consistency Check Results

### 3.1 Consistency Metrics Summary

| Dataset | Tasks | Runs | Date | Avg Jaccard | Structure Consistency | Status |
|---------|-------|------|------|--------------|----------------------|--------|
| MBPP | 200 | 5 | 2025-08-31 | 0.424 | 0.994 | ⚠️ |

### 3.2 Detailed Consistency Analysis

No consistency analysis files found

## 4. Status Description

- ✅ Success: All metrics meet expectations
- ⚠️ Warning: Some metrics do not meet expectations
- ❌ Failure: Major metrics do not meet expectations

## 5. File Statistics

- Test Generation: 10 files
- Code Generation: 0 files
- Full TDD: 0 files
- Consistency Check: 0 files
- Quality Analysis Reports: 5 files
- Consistency Analysis: 0 files
