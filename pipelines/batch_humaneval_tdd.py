#!/usr/bin/env python3
"""
TDD HumanEval Pipeline
Two-stage pipeline: test generation -> implementation generation
"""

import os
import sys
import datetime
sys.path.append('.')

from human_eval.data import write_jsonl, read_problems
from pipelines.batch_base import BaseBatchPipeline
from pipelines.lc_chain.generator import (
    generate_tests_for_humaneval, 
    generate_implementation_with_tests_humaneval
)

class TDDHumanEvalBatchPipeline(BaseBatchPipeline):
    """TDD版本的HumanEval批处理管道"""
    
    def read_problems(self, problem_file):
        """复用HumanEval的问题读取逻辑"""
        return read_problems(problem_file)
    
    def get_output_filename(self, num_tasks, prefix):
        """生成TDD版本的输出文件名"""
        return f"benchmarks/humaneval/data/{prefix}_{num_tasks}_tasks_{self.model}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def create_sample(self, task_id, problem, completion, error=None, generated_tests=None):
        """创建TDD版本的样本"""
        sample = {
            "task_id": task_id,
            "prompt": problem['prompt'],
            "completion": completion,
            "method": "tdd_humaneval",  # 标识这是TDD方法
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "entry_point": problem.get('entry_point', ''),
            "canonical_solution": problem.get('canonical_solution', ''),
            "test": problem.get('test', ''),
            "generated_tests": generated_tests,  # 新增：生成的测试
            "tdd_stage": "implementation"  # 标识这是实现阶段的结果
        }
        if error:
            sample["error"] = error
        return sample
    
    def save_results(self, output_file, samples):
        """复用HumanEval的保存逻辑"""
        write_jsonl(output_file, samples)
    
    def get_prompt(self, problem):
        """TDD流程不需要传统prompt，返回函数签名"""
        return problem['prompt']
    
    def run_batch_pipeline(self, problem_file, num_tasks=10, start_task=0):
        """重写批处理逻辑，实现两阶段TDD流程"""
        try:
            # 生成输出文件名
            output_file = self.generate_batch_output_filename(num_tasks, "tdd_humaneval_batch")
            
            # 读取问题
            print(f"Reading HumanEval problem file: {problem_file}")
            problems = self.read_problems(problem_file)
            print(f"Total HumanEval problems available: {len(problems)}")
            
            # 选择任务
            task_items = list(problems.items())
            end_task = min(start_task + num_tasks, len(task_items))
            selected_tasks = task_items[start_task:end_task]
            
            print(f"Processing TDD HumanEval tasks {start_task} to {end_task-1} ({len(selected_tasks)} tasks)")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # 两阶段处理
            samples = []
            for task_id, problem in selected_tasks:
                try:
                    prompt = problem['prompt']
                    canonical_solution = problem.get('canonical_solution', '')
                    
                    # 阶段1：生成测试
                    print(f"\n🔄 Stage 1: Generating tests for task {task_id}")
                    generated_tests = generate_tests_for_humaneval(prompt, canonical_solution, self.model)
                    print(f"✅ Tests generated: {len(generated_tests)} characters")
                    
                    # 阶段2：根据测试生成实现
                    print(f"🔄 Stage 2: Generating implementation for task {task_id}")
                    implementation = generate_implementation_with_tests_humaneval(
                        prompt, generated_tests, self.model
                    )
                    print(f"✅ Implementation generated: {len(implementation)} characters")
                    
                    # 创建样本
                    sample = self.create_sample(task_id, problem, implementation, generated_tests=generated_tests)
                    samples.append(sample)
                    
                except Exception as e:
                    print(f"Error processing {task_id}: {e}")
                    sample = self.create_sample(task_id, problem, "    pass", error=str(e))
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
            print(f"TDD batch processing failed: {e}")
            return None

def run_tdd_humaneval_pipeline(problem_file="benchmarks/humaneval/data/HumanEval.jsonl", 
                              num_tasks=10, 
                              model="gpt-4o-mini",
                              start_task=0):
    """运行TDD HumanEval管道"""
    pipeline = TDDHumanEvalBatchPipeline(model)
    return pipeline.run_batch_pipeline(problem_file, num_tasks, start_task)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TDD HumanEval Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/humaneval/data/HumanEval.jsonl", 
                       help="HumanEval problem file path")
    
    args = parser.parse_args()
    
    print("Starting TDD HumanEval Pipeline")
    print("=" * 50)
    
    output_file = run_tdd_humaneval_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    
    if output_file:
        print("\nTDD pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Run evaluation: evaluate_functional_correctness {output_file} --problem_file={args.problem_file}")
        print(f"2. View results: cat {output_file}")
    else:
        print("\nTDD pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
