#!/usr/bin/env python3
"""
Batch MBPP Pipeline
Process multiple MBPP tasks in batch
"""

import os
import sys
import datetime
import json
from tqdm import tqdm
sys.path.append('.')

from pipelines.batch_base import BaseBatchPipeline
from pipelines.lc_chain.prompts.mbpp import MBPP_PROMPT_TEMPLATE
from pipelines.lc_chain.generator import generate_one_completion_langchain

class MBPPBatchPipeline(BaseBatchPipeline):
    """MBPP batch pipeline implementation"""
    
    def read_problems(self, problem_file):
        """Read MBPP problems"""
        problems = {}
        with open(problem_file, 'r') as f:
            for line in f:
                problem = json.loads(line.strip())
                problems[problem['task_id']] = problem
        return problems
    
    def get_output_filename(self, num_tasks, prefix):
        """Generate MBPP output filename"""
        return f"benchmarks/mbpp/data/{prefix}_{num_tasks}_tasks_{self.model}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def create_sample(self, task_id, problem, completion, error=None):
        """Create MBPP sample"""
        sample = {
            "task_id": task_id,
            "prompt": problem['text'],
            "completion": completion,
            "method": "langchain",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "test_list": problem.get('test_list', []),
            "challenge_test_list": problem.get('challenge_test_list', []),
            "reference_code": problem.get('code', '')
        }
        if error:
            sample["error"] = error
        return sample
    
    def save_results(self, output_file, samples):
        """Save MBPP results"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    def get_prompt(self, problem):
        """Get MBPP prompt with test cases"""
        prompt = problem['text']
        test_list = problem.get('test_list', [])
        test_list_str = '\n'.join(test_list) if test_list else 'No test cases provided'
        
        # Format prompt using MBPP template
        return MBPP_PROMPT_TEMPLATE.format(description=prompt, test_list=test_list_str)
    
    def run_batch_pipeline(self, problem_file, num_tasks=10, start_task=0):
        """Override to handle MBPP-specific task filtering"""
        try:
            # Generate output filename
            output_file = self.generate_batch_output_filename(num_tasks, "langchain_mbpp_batch")
            
            # Read problems
            print(f"Reading MBPP problem file: {problem_file}")
            problems = self.read_problems(problem_file)
            print(f"Total MBPP problems available: {len(problems)}")
            
            # Filter for official test split (1-500)
            task_ids = [tid for tid in problems if 1 <= int(tid) <= 500]
            task_ids.sort(key=int)
            
            end_task = min(start_task + num_tasks, len(task_ids))
            selected_task_ids = task_ids[start_task:end_task]
            
            print(f"Processing MBPP tasks {selected_task_ids[0]} to {selected_task_ids[-1]} ({len(selected_task_ids)} tasks)")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # Process tasks with progress bar
            samples = []
            for task_id in tqdm(selected_task_ids, desc="Generating code"):
                problem = problems[task_id]
                try:
                    # Get raw data for the problem
                    prompt = problem['text']
                    test_list = problem.get('test_list', [])
                    test_list_str = '\n'.join(test_list) if test_list else 'No test cases provided'
                    
                    # Generate code completion with MBPP template
                    completion = generate_one_completion_langchain(prompt, self.model, MBPP_PROMPT_TEMPLATE, test_list=test_list_str)
                    
                    # Create sample
                    sample = self.create_sample(task_id, problem, completion)
                    samples.append(sample)
                    
                except Exception as e:
                    print(f"Error processing {task_id}: {e}")
                    # Add error sample
                    sample = self.create_sample(task_id, problem, "    pass", error=str(e))
                    samples.append(sample)
            
            # Save results
            self.save_results(output_file, samples)
               
            print(f"\nResults saved: {output_file}")
            
            # Print summary
            successful = sum(1 for s in samples if 'error' not in s)
            failed = len(samples) - successful
            print(f"Summary: {successful} successful, {failed} failed")
            
            return output_file
            
        except Exception as e:
            print(f"Batch processing failed: {e}")
            return None

def run_batch_mbpp_pipeline(problem_file="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                           num_tasks=10, 
                           model="gpt-4o-mini",
                           start_task=0):
    """Run batch MBPP pipeline"""
    pipeline = MBPPBatchPipeline(model)
    return pipeline.run_batch_pipeline(problem_file, num_tasks, start_task)

def main():
    """Main function for MBPP batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch MBPP Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                       help="MBPP problem file path")
    
    args = parser.parse_args()
    
    print("Starting Batch MBPP Pipeline")
    print("=" * 50)
    
    output_file = run_batch_mbpp_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    
    if output_file:
        print("\nBatch pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Run evaluation: analyze_mbpp_results_fixed.py {output_file}")
        print(f"2. View results: cat {output_file}")
    else:
        print("\nBatch pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 