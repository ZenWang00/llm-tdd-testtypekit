# Experiment Report Usage Guide

## Overview

The `report` folder contains comprehensive reports for LLM-TDD experiments, integrating the following three core analysis modules:

1. **Output Contract** - Contract validation results
2. **Heuristic Checks** - Heuristic check results  
3. **Consistency Check** - Consistency check results

## Report Structure

### 1. Pipeline Execution Summary
- Shows the execution status of all pipelines
- Includes test generation, code generation, full TDD, etc.
- Status indicators: ✅ Success, ⚠️ Warning, ❌ Failure

### 2. Test Quality Analysis
- **Quality Metrics Summary**: Table format showing contract scores and heuristic scores
- **Detailed Analysis Results**: Contains detailed content from each analysis file

### 3. Consistency Check Results
- **Consistency Metrics Summary**: Jaccard similarity and structure consistency
- **Detailed Consistency Analysis**: Task-level detailed analysis

### 4. Status Description
- Standards for success, warning, and failure

### 5. File Statistics
- Statistics for various types of files

## Usage

### Generate Reports
```bash
# Generate complete report
python generate_experiment_report.py

# Specify data directory
python generate_experiment_report.py --data_dir benchmarks

# Specify output file
python generate_experiment_report.py --output report/my_report.md
```

### View Reports
```bash
# View latest report
ls -la report/
cat report/experiment_report_YYYYMMDD_HHMMSS.md
```

## Report File Naming

- `experiment_report_YYYYMMDD_HHMMSS.md` - Complete experiment report
- Timestamp format: YYYYMMDD_HHMMSS

## Data Sources

Reports automatically scan the following directories and files:
- `benchmarks/mbpp/data/` - MBPP data
- `benchmarks/humaneval/data/` - HumanEval data
- `*_comprehensive_report.txt` - Quality analysis reports
- `*_analysis.json` - Consistency analysis results

## Notes

1. Ensure data files exist and are readable
2. Report generation requires Python environment and dependencies
3. Large datasets may take longer to process
4. Recommend generating reports regularly to track experiment progress
