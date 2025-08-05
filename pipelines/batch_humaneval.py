#!/usr/bin/env python3
"""
Batch HumanEval Pipeline
Process multiple HumanEval tasks in batch
"""

import os
import sys
import datetime
sys.path.append('.')

from human_eval.data import write_jsonl, read_problems
from pipelines.batch_base import BaseBatchPipeline

class HumanEvalBatchPipeline(BaseBatchPipeline):
    """HumanEval batch pipeline implementation"""
    
    def read_problems(self, problem_file):
        """Read HumanEval problems"""
        return read_problems(problem_file)
    
    def get_output_filename(self, num_tasks, prefix):
        """Generate HumanEval output filename"""
        return f"benchmarks/humaneval/data/{prefix}_{num_tasks}_tasks_{self.model}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def create_sample(self, task_id, problem, completion, error=None):
        """Create HumanEval sample"""
        sample = {
            "task_id": task_id,
            "prompt": problem['prompt'],
            "completion": completion,
            "method": "langchain",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "entry_point": problem.get('entry_point', ''),
            "canonical_solution": problem.get('canonical_solution', ''),
            "test": problem.get('test', '')
        }
        if error:
            sample["error"] = error
        return sample
    
    def save_results(self, output_file, samples):
        """Save HumanEval results using write_jsonl"""
        write_jsonl(output_file, samples)
    
    def get_prompt(self, problem):
        """Get HumanEval prompt (already includes function signature)"""
        return problem['prompt']

def run_batch_humaneval_pipeline(problem_file="benchmarks/humaneval/data/HumanEval.jsonl", 
                                num_tasks=10, 
                                model="gpt-4o-mini",
                                start_task=0):
    """Run batch HumanEval pipeline"""
    pipeline = HumanEvalBatchPipeline(model)
    return pipeline.run_batch_pipeline(problem_file, num_tasks, start_task)

def main():
    """Main function for HumanEval batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch HumanEval Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/humaneval/data/HumanEval.jsonl", 
                       help="Problem file path")
    
    args = parser.parse_args()
    
    print("Starting Batch HumanEval Pipeline")
    print("=" * 50)
    
    output_file = run_batch_humaneval_pipeline(
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