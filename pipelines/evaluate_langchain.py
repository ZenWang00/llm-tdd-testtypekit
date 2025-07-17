#!/usr/bin/env python3
"""
LangChain HumanEval Evaluation Pipeline
Integrate HumanEval's test execution logic to validate generated code and calculate pass@1
"""

import os
import sys
import datetime
import json
from collections import defaultdict, Counter
from typing import Dict, List
sys.path.append('.')

from human_eval.data import read_problems, stream_jsonl, write_jsonl
from human_eval.evaluation import evaluate_functional_correctness
from human_eval.execution import check_correctness

def run_evaluation(sample_file: str, 
                   problem_file: str = "benchmarks/humaneval/data/HumanEval.jsonl",
                   timeout: float = 3.0,
                   n_workers: int = 4):
    """
    Run evaluation on generated samples and calculate pass@1
    """
    try:
        print(f"Starting evaluation of: {sample_file}")
        print(f"Using problem file: {problem_file}")
        print("=" * 50)
        
        # Read problems
        problems = read_problems(problem_file)
        print(f"Loaded {len(problems)} problems")
        
        # Read samples
        samples = list(stream_jsonl(sample_file))
        print(f"Loaded {len(samples)} samples")
        
        # Group samples by task_id
        samples_by_task = defaultdict(list)
        for sample in samples:
            samples_by_task[sample["task_id"]].append(sample)
        
        print(f"Found {len(samples_by_task)} unique tasks")
        
        # Run evaluations
        results = []
        error_summary = defaultdict(int)
        
        print("\nRunning test suites...")
        for task_id, task_samples in samples_by_task.items():
            print(f"Evaluating {task_id} ({len(task_samples)} samples)")
            
            for i, sample in enumerate(task_samples):
                try:
                    # Check correctness
                    result = check_correctness(
                        problems[task_id], 
                        sample["completion"], 
                        timeout, 
                        completion_id=i
                    )
                    
                    # Add result to sample
                    sample["passed"] = result["passed"]
                    sample["result"] = result["result"]
                    sample["completion_id"] = result["completion_id"]
                    
                    results.append(sample)
                    
                    # Track error types
                    if not result["passed"]:
                        error_type = result["result"].split(":")[0] if ":" in result["result"] else result["result"]
                        error_summary[error_type] += 1
                    
                except Exception as e:
                    print(f"Error evaluating {task_id} sample {i}: {e}")
                    sample["passed"] = False
                    sample["result"] = f"evaluation_error: {e}"
                    results.append(sample)
                    error_summary["evaluation_error"] += 1
        
        # Calculate statistics
        total_samples = len(results)
        passed_samples = sum(1 for r in results if r["passed"])
        pass_rate = passed_samples / total_samples if total_samples > 0 else 0
        
        # Calculate pass@1 (assuming one sample per task)
        unique_tasks = len(samples_by_task)
        passed_tasks = sum(1 for task_samples in samples_by_task.values() 
                          if any(s["passed"] for s in task_samples))
        pass_at_1 = passed_tasks / unique_tasks if unique_tasks > 0 else 0
        
        # Generate output filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = sample_file.replace(".jsonl", f"_evaluation_{timestamp}.jsonl")
        
        # Save detailed results
        write_jsonl(output_file, results)
        
        # Print summary
        print("\n" + "=" * 50)
        print("EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Total samples: {total_samples}")
        print(f"Passed samples: {passed_samples}")
        print(f"Pass rate: {pass_rate:.2%}")
        print(f"Unique tasks: {unique_tasks}")
        print(f"Passed tasks: {passed_tasks}")
        print(f"Pass@1: {pass_at_1:.2%}")
        
        print(f"\nError Summary:")
        for error_type, count in error_summary.items():
            print(f"  {error_type}: {count}")
        
        print(f"\nDetailed results saved to: {output_file}")
        
        return {
            "total_samples": total_samples,
            "passed_samples": passed_samples,
            "pass_rate": pass_rate,
            "unique_tasks": unique_tasks,
            "passed_tasks": passed_tasks,
            "pass_at_1": pass_at_1,
            "error_summary": dict(error_summary),
            "output_file": output_file
        }
        
    except Exception as e:
        print(f"Evaluation failed: {e}")
        return None

def evaluate_batch_results(batch_file: str):
    """
    Evaluate results from batch processing
    """
    print("Evaluating batch processing results...")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(batch_file):
        print(f"Error: File {batch_file} not found")
        return None
    
    # Run evaluation
    results = run_evaluation(batch_file)
    
    if results:
        print("\nEvaluation completed successfully!")
        return results
    else:
        print("\nEvaluation failed!")
        return None

def main():
    """
    Main function for evaluation
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="LangChain HumanEval Evaluation")
    parser.add_argument("--sample_file", type=str, required=True, 
                       help="Sample file to evaluate")
    parser.add_argument("--problem_file", type=str, 
                       default="benchmarks/humaneval/data/HumanEval.jsonl",
                       help="Problem file path")
    parser.add_argument("--timeout", type=float, default=3.0,
                       help="Timeout for test execution")
    parser.add_argument("--n_workers", type=int, default=4,
                       help="Number of worker processes")
    
    args = parser.parse_args()
    
    print("Starting LangChain HumanEval Evaluation")
    print("=" * 50)
    
    results = run_evaluation(
        sample_file=args.sample_file,
        problem_file=args.problem_file,
        timeout=args.timeout,
        n_workers=args.n_workers
    )
    
    if results:
        print("\nEvaluation completed successfully!")
        print(f"Results saved to: {results['output_file']}")
    else:
        print("\nEvaluation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 