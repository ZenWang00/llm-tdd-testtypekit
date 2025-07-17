#!/usr/bin/env python3
"""
Batch LangChain HumanEval Pipeline
Process multiple HumanEval tasks in batch
"""

import os
import sys
import datetime
import json
from tqdm import tqdm
sys.path.append('.')

from pipelines.lc_chain.generator import generate_one_completion_langchain
from human_eval.data import write_jsonl, read_problems

def generate_batch_output_filename(model="gpt-4o-mini", num_tasks=10, prefix="langchain_batch"):
    """
    Generate output filename for batch processing
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_clean = model.replace("-", "_").replace(".", "_")
    return f"benchmarks/humaneval/data/{prefix}_{num_tasks}_tasks_{model_clean}_{timestamp}.jsonl"

def run_batch_langchain_pipeline(problem_file="benchmarks/humaneval/data/HumanEval.jsonl", 
                                num_tasks=10, 
                                model="gpt-4o-mini",
                                start_task=0):
    """
    Run batch LangChain pipeline on multiple HumanEval tasks
    """
    try:
        # Generate output filename
        output_file = generate_batch_output_filename(model, num_tasks)
        
        # Read HumanEval problems
        print(f"Reading problem file: {problem_file}")
        problems = read_problems(problem_file)
        print(f"Total problems available: {len(problems)}")
        
        # Select tasks to process
        task_items = list(problems.items())
        end_task = min(start_task + num_tasks, len(task_items))
        selected_tasks = task_items[start_task:end_task]
        
        print(f"Processing tasks {start_task} to {end_task-1} ({len(selected_tasks)} tasks)")
        print(f"Using model: {model}")
        print("=" * 50)
        
        # Process tasks with progress bar
        samples = []
        for task_id, problem in tqdm(selected_tasks, desc="Generating code"):
            try:
                # Generate code completion
                completion = generate_one_completion_langchain(problem['prompt'], model)
                
                # Create sample with detailed information
                sample = {
                    "task_id": task_id,
                    "prompt": problem['prompt'],
                    "completion": completion,
                    "method": "langchain",
                    "model": model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "entry_point": problem.get('entry_point', ''),
                    "canonical_solution": problem.get('canonical_solution', ''),
                    "test": problem.get('test', '')
                }
                samples.append(sample)
                
            except Exception as e:
                print(f"Error processing {task_id}: {e}")
                # Add error sample
                sample = {
                    "task_id": task_id,
                    "prompt": problem['prompt'],
                    "completion": "    pass",  # Default error response
                    "method": "langchain",
                    "model": model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "error": str(e),
                    "entry_point": problem.get('entry_point', ''),
                    "canonical_solution": problem.get('canonical_solution', ''),
                    "test": problem.get('test', '')
                }
                samples.append(sample)
        
        # Save results
        write_jsonl(output_file, samples)
        print(f"\nResults saved: {output_file}")
        
        # Print summary
        successful = sum(1 for s in samples if 'error' not in s)
        failed = len(samples) - successful
        print(f"Summary: {successful} successful, {failed} failed")
        
        return output_file
        
    except Exception as e:
        print(f"Batch processing failed: {e}")
        return None

def main():
    """
    Main function for batch processing
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch LangChain HumanEval Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/humaneval/data/HumanEval.jsonl", 
                       help="Problem file path")
    
    args = parser.parse_args()
    
    print("Starting Batch LangChain HumanEval Pipeline")
    print("=" * 50)
    
    output_file = run_batch_langchain_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    
    if output_file:
        print("\nBatch pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Run evaluation: evaluate_functional_correctness {output_file} --problem_file={args.problem_file}")
        print(f"2. View results: cat {output_file}")
    else:
        print("\nBatch pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 