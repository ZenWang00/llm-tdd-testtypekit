#!/usr/bin/env python3
"""
Batch LangChain MBPP Pipeline
Process multiple MBPP tasks in batch
"""

import os
import sys
import datetime
import json
from tqdm import tqdm
sys.path.append('.')

from pipelines.lc_chain.generator import generate_one_completion_langchain
from pipelines.lc_chain.prompts.mbpp import MBPP_PROMPT_TEMPLATE

def read_mbpp_problems(file_path):
    """读取MBPP问题，返回task_id到问题的映射"""
    problems = {}
    with open(file_path, 'r') as f:
        for line in f:
            problem = json.loads(line.strip())
            problems[problem['task_id']] = problem
    return problems

def generate_mbpp_output_filename(model="gpt-4o-mini", num_tasks=10, prefix="langchain_mbpp_batch"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_clean = model.replace("-", "_").replace(".", "_")
    return f"benchmarks/mbpp/data/{prefix}_{num_tasks}_tasks_{model_clean}_{timestamp}.jsonl"

def run_batch_langchain_mbpp_pipeline(problem_file="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                                      num_tasks=10, 
                                      model="gpt-4o-mini",
                                      start_task=0):
    try:
        output_file = generate_mbpp_output_filename(model, num_tasks)
        print(f"Reading MBPP problem file: {problem_file}")
        problems = read_mbpp_problems(problem_file)
        print(f"Total MBPP problems available: {len(problems)}")

        # 只用官方推荐的test split: 11-510
        task_ids = [tid for tid in problems if 11 <= int(tid) <= 510]
        task_ids.sort(key=int)
        end_task = min(start_task + num_tasks, len(task_ids))
        selected_task_ids = task_ids[start_task:end_task]
        print(f"Processing MBPP tasks {selected_task_ids[0]} to {selected_task_ids[-1]} ({len(selected_task_ids)} tasks)")
        print(f"Using model: {model}")
        print("=" * 50)

        samples = []
        for tid in tqdm(selected_task_ids, desc="Generating code"):
            problem = problems[tid]
            try:
                # 直接使用problem['text']作为prompt，generate_one_completion_langchain会使用MBPP_PROMPT_TEMPLATE包装
                prompt = problem['text']
                print(f"\n[DEBUG] Original prompt for task {tid}:\n{prompt}\n")
                completion = generate_one_completion_langchain(prompt, model, MBPP_PROMPT_TEMPLATE)
                print(f"[DEBUG] Completion for task {tid}:\n{completion}\n")
                sample = {
                    "task_id": tid,
                    "prompt": prompt,
                    "completion": completion,
                    "method": "langchain",
                    "model": model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "test_list": problem.get('test_list', []),
                    "challenge_test_list": problem.get('challenge_test_list', []),
                    "reference_code": problem.get('code', '')
                }
                samples.append(sample)
            except Exception as e:
                print(f"Error processing {tid}: {e}")
                sample = {
                    "task_id": tid,
                    "prompt": problem['text'],
                    "completion": "    pass",
                    "method": "langchain",
                    "model": model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "error": str(e),
                    "test_list": problem.get('test_list', []),
                    "challenge_test_list": problem.get('challenge_test_list', []),
                    "reference_code": problem.get('code', '')
                }
                samples.append(sample)

        # 保存结果
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        print(f"\nResults saved: {output_file}")
        successful = sum(1 for s in samples if 'error' not in s)
        failed = len(samples) - successful
        print(f"Summary: {successful} successful, {failed} failed")
        return output_file
    except Exception as e:
        print(f"Batch processing failed: {e}")
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch LangChain MBPP Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/mbpp/mbpp.jsonl", help="MBPP problem file path")
    args = parser.parse_args()
    print("Starting Batch LangChain MBPP Pipeline")
    print("=" * 50)
    output_file = run_batch_langchain_mbpp_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    if output_file:
        print("\nBatch pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Run evaluation: <your_evaluation_script> {output_file}")
        print(f"2. View results: cat {output_file}")
    else:
        print("\nBatch pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 