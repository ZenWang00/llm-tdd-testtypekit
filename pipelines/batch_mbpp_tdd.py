#!/usr/bin/env python3
"""
TDD MBPP Pipeline
Two-stage pipeline: test generation -> implementation generation
"""

import os
import sys
import datetime
import json
from tqdm import tqdm
sys.path.append('.')

from pipelines.batch_base import BaseBatchPipeline
from pipelines.lc_chain.generator import (
    generate_tests_for_mbpp, 
    generate_implementation_with_tests_mbpp
)

class TDDMBPPBatchPipeline(BaseBatchPipeline):
    """TDD版本的MBPP批处理管道"""
    
    def read_problems(self, problem_file):
        """复用MBPP的问题读取逻辑"""
        problems = {}
        with open(problem_file, 'r') as f:
            for line in f:
                problem = json.loads(line.strip())
                problems[problem['task_id']] = problem
        return problems
    
    def get_output_filename(self, num_tasks, prefix):
        """生成TDD版本的输出文件名"""
        return f"benchmarks/mbpp/data/{prefix}_{num_tasks}_tasks_{self.model}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def create_sample(self, task_id, problem, completion, error=None, generated_tests=None):
        """创建TDD版本的样本"""
        sample = {
            "task_id": task_id,
            "prompt": problem['text'],
            "completion": completion,
            "method": "tdd_mbpp",  # 标识这是TDD方法
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "test_list": problem.get('test_list', []),
            "challenge_test_list": problem.get('challenge_test_list', []),
            "reference_code": problem.get('code', ''),
            "generated_tests": generated_tests,  # 新增：生成的测试
            "tdd_stage": "implementation"  # 标识这是实现阶段的结果
        }
        if error:
            sample["error"] = error
        return sample
    
    def save_results(self, output_file, samples):
        """复用MBPP的保存逻辑"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    def get_prompt(self, problem):
        """TDD流程不需要传统prompt，返回问题描述"""
        return problem['text']
    
    def run_batch_pipeline(self, problem_file, num_tasks=10, start_task=0):
        """重写批处理逻辑，实现两阶段TDD流程"""
        try:
            # 生成输出文件名
            output_file = self.generate_batch_output_filename(num_tasks, "tdd_mbpp_batch")
            
            # 读取问题
            print(f"Reading MBPP problem file: {problem_file}")
            problems = self.read_problems(problem_file)
            print(f"Total MBPP problems available: {len(problems)}")
            
            # 使用所有可用任务（不过滤官方测试集）
            task_ids = list(problems.keys())
            task_ids.sort(key=int)
            
            end_task = min(start_task + num_tasks, len(task_ids))
            selected_task_ids = task_ids[start_task:end_task]
            
            print(f"Processing TDD MBPP tasks {selected_task_ids[0]} to {selected_task_ids[-1]} ({len(selected_task_ids)} tasks)")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # 两阶段处理
            samples = []
            for task_id in tqdm(selected_task_ids, desc="TDD Pipeline"):
                problem = problems[task_id]
                try:
                    description = problem['text']
                    
                    # 阶段1：生成测试
                    print(f"\n🔄 Stage 1: Generating tests for task {task_id}")
                    reference_code = problem.get('code', '')  # 修复：使用正确的字段名 'code'
                    generated_tests = generate_tests_for_mbpp(description, reference_code, self.model)
                    print(f"✅ Tests generated: {len(generated_tests)} characters")
                    
                    # 阶段2：根据测试生成实现
                    print(f"🔄 Stage 2: Generating implementation for task {task_id}")
                    implementation = generate_implementation_with_tests_mbpp(
                        description, generated_tests, reference_code, self.model
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

def run_tdd_mbpp_pipeline(problem_file="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                         num_tasks=10, 
                         model="gpt-4o-mini",
                         start_task=0):
    """运行TDD MBPP管道"""
    pipeline = TDDMBPPBatchPipeline(model)
    return pipeline.run_batch_pipeline(problem_file, num_tasks, start_task)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TDD MBPP Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                       help="MBPP problem file path")
    
    args = parser.parse_args()
    
    print("Starting TDD MBPP Pipeline")
    print("=" * 50)
    
    output_file = run_tdd_mbpp_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    
    if output_file:
        print("\nTDD pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Run evaluation: analyze_mbpp_results_fixed.py {output_file}")
        print(f"2. View results: cat {output_file}")
    else:
        print("\nTDD pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
