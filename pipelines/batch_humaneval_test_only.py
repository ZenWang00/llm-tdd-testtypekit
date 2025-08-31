#!/usr/bin/env python3
"""
HumanEval测试专用Pipeline

只生成测试代码，不生成实现代码。用于测试数据管理和一致性检验。
"""

import os
import json
import datetime
from typing import Dict, Any
from tqdm import tqdm

from pipelines.batch_base import BaseBatchPipeline
from pipelines.lc_chain.generator import generate_tests_for_humaneval
from pipelines.batch_humaneval import write_jsonl


class TestOnlyHumanEvalBatchPipeline(BaseBatchPipeline):
    """只生成测试的HumanEval Pipeline"""
    
    def __init__(self, model="gpt-4o-mini"):
        super().__init__(model)
    
    def read_problems(self, problem_file: str) -> Dict[str, Any]:
        """复用HumanEval的问题读取逻辑"""
        problems = {}
        with open(problem_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    task_id = data['task_id']
                    problems[task_id] = data
        return problems
    
    def get_output_filename(self, num_tasks, prefix):
        """实现抽象方法"""
        return os.path.join("benchmarks", "humaneval", "data", f"{prefix}_{num_tasks}_tasks_{self.model}.jsonl")
    
    def generate_batch_output_filename(self, num_tasks: int, prefix: str) -> str:
        """生成输出文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%M%S")
        filename = f"{prefix}_{num_tasks}_tasks_{self.model}_{timestamp}.jsonl"
        return os.path.join("benchmarks", "humaneval", "data", filename)
    
    def create_sample(self, task_id: str, problem: Dict[str, Any], generated_tests: str, error: str = None) -> Dict[str, Any]:
        """创建样本数据"""
        sample = {
            "task_id": task_id,
            "prompt": problem['prompt'],
            "canonical_solution": problem.get('canonical_solution', ''),
            "test": problem.get('test', ''),
            "generated_tests": generated_tests,
            "method": "test_only_humaneval",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": "test_generation_only"
        }
        if error:
            sample["error"] = error
        return sample
    
    def save_results(self, output_file: str, samples: list):
        """复用HumanEval的保存逻辑"""
        write_jsonl(output_file, samples)
    
    def get_prompt(self, problem):
        """返回函数签名"""
        return problem['prompt']
    
    def run_batch_pipeline(self, problem_file: str, num_tasks: int = 10, start_task: int = 0):
        """运行测试生成Pipeline"""
        try:
            # 生成输出文件名
            output_file = self.generate_batch_output_filename(num_tasks, "test_only_humaneval_batch")
            
            # 读取问题
            print(f"Reading HumanEval problem file: {problem_file}")
            problems = self.read_problems(problem_file)
            print(f"Total HumanEval problems available: {len(problems)}")
            
            # 选择任务
            task_items = list(problems.items())
            end_task = min(start_task + num_tasks, len(task_items))
            selected_tasks = task_items[start_task:end_task]
            
            print(f"Processing Test-Only HumanEval tasks {start_task} to {end_task-1} ({len(selected_tasks)} tasks)")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # 只执行测试生成阶段
            samples = []
            for task_id, problem in selected_tasks:
                try:
                    prompt = problem['prompt']
                    canonical_solution = problem.get('canonical_solution', '')
                    
                    # 生成测试
                    print(f"\nGenerating tests for task {task_id}")
                    generated_tests = generate_tests_for_humaneval(prompt, canonical_solution, self.model)
                    print(f"Tests generated: {len(generated_tests)} characters")
                    
                    # 创建样本
                    sample = self.create_sample(task_id, problem, generated_tests)
                    samples.append(sample)
                    
                except Exception as e:
                    print(f"Error processing {task_id}: {e}")
                    sample = self.create_sample(task_id, problem, "", error=str(e))
                    samples.append(sample)
            
            # 保存结果
            self.save_results(output_file, samples)
               
            print(f"\nResults saved: {output_file}")
            
            # 打印摘要
            successful = sum(1 for s in samples if 'error' not in s)
            failed = len(samples) - successful
            print(f"Summary: {successful} successful, {failed} failed")
            
            return output_file
            
        except Exception as e:
            print(f"Test-only batch processing failed: {e}")
            return None


def run_test_only_humaneval_pipeline(problem_file="benchmarks/humaneval/data/HumanEval.jsonl", 
                                    num_tasks=10, 
                                    model="gpt-4o-mini",
                                    start_task=0):
    """运行测试专用HumanEval Pipeline"""
    pipeline = TestOnlyHumanEvalBatchPipeline(model)
    return pipeline.run_batch_pipeline(problem_file, num_tasks, start_task)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HumanEval Test-Only Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/humaneval/data/HumanEval.jsonl", 
                       help="HumanEval problem file path")
    
    args = parser.parse_args()
    
    print("Starting HumanEval Test-Only Pipeline")
    print("=" * 50)
    
    output_file = run_test_only_humaneval_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    
    if output_file:
        print("\nTest-only pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Use tests for code generation: batch_humaneval_code_only.py --test_file {output_file}")
        print(f"2. Analyze test quality: analyze_tdd_comprehensive.py {output_file}")
        print(f"3. View results: cat {output_file}")
    else:
        print("\nTest-only pipeline failed")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
