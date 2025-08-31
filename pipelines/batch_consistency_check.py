#!/usr/bin/env python3
"""
一致性检查Pipeline

使用不同参数多次生成测试，然后比较结果的一致性。
"""

import os
import json
import datetime
import random
from typing import Dict, Any, List
from tqdm import tqdm
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.batch_mbpp_test_only import TestOnlyMBPPBatchPipeline
from pipelines.batch_humaneval_test_only import TestOnlyHumanEvalBatchPipeline


class ConsistencyCheckPipeline:
    """一致性检查Pipeline"""
    
    def __init__(self, base_model="gpt-4o-mini"):
        self.base_model = base_model
        self.temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]
        self.random_seeds = [42, 123, 456, 789, 999]
    
    def generate_consistency_tests_mbpp(self, problem_file: str, num_tasks: int = 5, 
                                       start_task: int = 0, num_runs: int = 3):
        """为MBPP生成一致性检查的测试"""
        print(f"Generating MBPP consistency tests for {num_tasks} tasks, {num_runs} runs each")
        print("=" * 60)
        
        # 读取问题
        pipeline = TestOnlyMBPPBatchPipeline(self.base_model)
        problems = pipeline.read_problems(problem_file)
        
        # 选择任务
        task_ids = list(problems.keys())
        task_ids.sort(key=int)
        end_task = min(start_task + num_tasks, len(task_ids))
        selected_task_ids = task_ids[start_task:end_task]
        
        all_results = []
        
        for run_id in range(num_runs):
            print(f"\n--- Run {run_id + 1}/{num_runs} ---")
            
            # 设置随机种子
            random.seed(self.random_seeds[run_id])
            temperature = self.temperatures[run_id % len(self.temperatures)]
            
            print(f"Using temperature: {temperature}, seed: {self.random_seeds[run_id]}")
            
            run_results = []
            for task_id in tqdm(selected_task_ids, desc=f"Run {run_id + 1}"):
                problem = problems[task_id]
                try:
                    description = problem['text']
                    reference_code = problem.get('code', '')
                    
                    # 生成测试
                    from pipelines.lc_chain.generator import generate_tests_for_mbpp
                    generated_tests = generate_tests_for_mbpp(description, reference_code, self.base_model, temperature=temperature)
                    
                    # 创建样本
                    sample = {
                        "task_id": task_id,
                        "prompt": problem['text'],
                        "reference_code": reference_code,
                        "generated_tests": generated_tests,
                        "method": "consistency_check_mbpp",
                        "model": self.base_model,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "stage": "consistency_check",
                        "run_id": run_id,
                        "temperature": temperature,
                        "random_seed": self.random_seeds[run_id]
                    }
                    run_results.append(sample)
                    
                except Exception as e:
                    print(f"Error in run {run_id + 1}, task {task_id}: {e}")
                    sample = {
                        "task_id": task_id,
                        "prompt": problem['text'],
                        "reference_code": reference_code,
                        "generated_tests": "",
                        "method": "consistency_check_mbpp",
                        "model": self.base_model,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "stage": "consistency_check",
                        "run_id": run_id,
                        "temperature": temperature,
                        "random_seed": self.random_seeds[run_id],
                        "error": str(e)
                    }
                    run_results.append(sample)
            
            all_results.extend(run_results)
        
        # 保存结果
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"benchmarks/mbpp/data/consistency_check_mbpp_{num_tasks}_tasks_{num_runs}_runs_{self.base_model}_{timestamp}.jsonl"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in all_results:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"\nConsistency check results saved: {output_file}")
        return output_file, all_results
    
    def generate_consistency_tests_humaneval(self, problem_file: str, num_tasks: int = 5, 
                                           start_task: int = 0, num_runs: int = 3):
        """为HumanEval生成一致性检查的测试"""
        print(f"Generating HumanEval consistency tests for {num_tasks} tasks, {num_runs} runs each")
        print("=" * 60)
        
        # 读取问题
        pipeline = TestOnlyHumanEvalBatchPipeline(self.base_model)
        problems = pipeline.read_problems(problem_file)
        
        # 选择任务
        task_items = list(problems.items())
        end_task = min(start_task + num_tasks, len(task_items))
        selected_tasks = task_items[start_task:end_task]
        
        all_results = []
        
        for run_id in range(num_runs):
            print(f"\n--- Run {run_id + 1}/{num_runs} ---")
            
            # 设置随机种子
            random.seed(self.random_seeds[run_id])
            temperature = self.temperatures[run_id % len(self.temperatures)]
            
            print(f"Using temperature: {temperature}, seed: {self.random_seeds[run_id]}")
            
            run_results = []
            for task_id, problem in tqdm(selected_tasks, desc=f"Run {run_id + 1}"):
                try:
                    prompt = problem['prompt']
                    canonical_solution = problem.get('canonical_solution', '')
                    
                    # 生成测试
                    from pipelines.lc_chain.generator import generate_tests_for_humaneval
                    generated_tests = generate_tests_for_humaneval(prompt, canonical_solution, self.base_model, temperature=temperature)
                    
                    # 创建样本
                    sample = {
                        "task_id": task_id,
                        "prompt": problem['prompt'],
                        "canonical_solution": canonical_solution,
                        "test": problem.get('test', ''),
                        "generated_tests": generated_tests,
                        "method": "consistency_check_humaneval",
                        "model": self.base_model,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "stage": "consistency_check",
                        "run_id": run_id,
                        "temperature": temperature,
                        "random_seed": self.random_seeds[run_id]
                    }
                    run_results.append(sample)
                    
                except Exception as e:
                    print(f"Error in run {run_id + 1}, task {task_id}: {e}")
                    sample = {
                        "task_id": task_id,
                        "prompt": problem['prompt'],
                        "canonical_solution": canonical_solution,
                        "test": problem.get('test', ''),
                        "generated_tests": "",
                        "method": "consistency_check_humaneval",
                        "model": self.base_model,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "stage": "consistency_check",
                        "run_id": run_id,
                        "temperature": temperature,
                        "random_seed": self.random_seeds[run_id],
                        "error": str(e)
                    }
                    run_results.append(sample)
            
            all_results.extend(run_results)
        
        # 保存结果
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"benchmarks/humaneval/data/consistency_check_humaneval_{num_tasks}_tasks_{num_runs}_runs_{self.base_model}_{timestamp}.jsonl"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in all_results:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"\nConsistency check results saved: {output_file}")
        return output_file, all_results


def run_consistency_check_mbpp(problem_file="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                              num_tasks=5, start_task=0, num_runs=3):
    """运行MBPP一致性检查"""
    pipeline = ConsistencyCheckPipeline()
    return pipeline.generate_consistency_tests_mbpp(problem_file, num_tasks, start_task, num_runs)


def run_consistency_check_humaneval(problem_file="benchmarks/humaneval/data/HumanEval.jsonl", 
                                   num_tasks=5, start_task=0, num_runs=3):
    """运行HumanEval一致性检查"""
    pipeline = ConsistencyCheckPipeline()
    return pipeline.generate_consistency_tests_humaneval(problem_file, num_tasks, start_task, num_runs)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Consistency Check Pipeline")
    parser.add_argument("--dataset", choices=["mbpp", "humaneval"], required=True, 
                       help="Dataset to use")
    parser.add_argument("--num_tasks", type=int, default=5, help="Number of tasks to process")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--num_runs", type=int, default=3, help="Number of runs per task")
    parser.add_argument("--problem_file", type=str, 
                       default="benchmarks/mbpp/mbpp/mbpp.jsonl",
                       help="Problem file path")
    
    args = parser.parse_args()
    
    print("Starting Consistency Check Pipeline")
    print("=" * 50)
    
    if args.dataset == "mbpp":
        if args.problem_file == "benchmarks/mbpp/mbpp/mbpp.jsonl":
            args.problem_file = "benchmarks/mbpp/mbpp/mbpp.jsonl"
        output_file, results = run_consistency_check_mbpp(
            args.problem_file, args.num_tasks, args.start_task, args.num_runs
        )
    else:  # humaneval
        if args.problem_file == "benchmarks/mbpp/mbpp/mbpp.jsonl":
            args.problem_file = "benchmarks/humaneval/data/HumanEval.jsonl"
        output_file, results = run_consistency_check_humaneval(
            args.problem_file, args.num_tasks, args.start_task, args.num_runs
        )
    
    print(f"\nConsistency check completed!")
    print(f"Result file: {output_file}")
    print(f"Total samples: {len(results)}")
    print(f"Tasks per run: {args.num_tasks}")
    print(f"Number of runs: {args.num_runs}")
    
    print("\nNext steps:")
    print(f"1. Analyze consistency: python analyze_consistency.py {output_file}")
    print(f"2. View results: cat {output_file}")


if __name__ == "__main__":
    main()
