# Batch Pipeline Usage

This directory contains refactored batch processing pipelines for different benchmarks.

## Files

- `batch_base.py` - Base class with common functionality
- `batch_humaneval.py` - HumanEval benchmark pipeline
- `batch_mbpp.py` - MBPP benchmark pipeline

## Usage

### HumanEval Pipeline

```bash
# Process 10 HumanEval tasks starting from task 0
python pipelines/batch_humaneval.py --num_tasks 10 --start_task 0

# Process 50 tasks with custom model
python pipelines/batch_humaneval.py --num_tasks 50 --model gpt-4o --start_task 10

# Use custom problem file
python pipelines/batch_humaneval.py --problem_file path/to/custom/humaneval.jsonl
```

### MBPP Pipeline

```bash
# Process 10 MBPP tasks starting from task 0 (filtered to official test split 1-500)
python pipelines/batch_mbpp.py --num_tasks 10 --start_task 0

# Process 500 tasks with custom model
python pipelines/batch_mbpp.py --num_tasks 500 --model gpt-4o --start_task 0

# Use custom problem file
python pipelines/batch_mbpp.py --problem_file path/to/custom/mbpp.jsonl
```

## Key Differences

### HumanEval
- Uses `problem['prompt']` (already includes function signature)
- Outputs to `benchmarks/humaneval/data/`
- Sample fields: `entry_point`, `canonical_solution`, `test`
- Evaluation: `evaluate_functional_correctness`

### MBPP
- Uses `problem['text']` + `test_list` (formatted with MBPP_PROMPT_TEMPLATE)
- Outputs to `benchmarks/mbpp/data/`
- Sample fields: `test_list`, `challenge_test_list`, `reference_code`
- Evaluation: `analyze_mbpp_results_fixed.py`
- Filters to official test split (task_id 1-500)

## Architecture

The refactored code uses inheritance to avoid duplication:

```
BaseBatchPipeline (abstract base class)
├── HumanEvalBatchPipeline
└── MBPPBatchPipeline
```

Each pipeline implements:
- `read_problems()` - Read benchmark-specific data format
- `get_prompt()` - Format prompt for the benchmark
- `create_sample()` - Create output sample with benchmark-specific fields
- `save_results()` - Save results in benchmark-specific format 