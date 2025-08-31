#!/usr/bin/env python3
"""
MBPP测试专用Pipeline

只生成测试代码，不生成实现代码。用于测试数据管理和一致性检验。
"""

import os
import json
import datetime
from typing import Dict, Any
from tqdm import tqdm

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.batch_base import BaseBatchPipeline
from pipelines.lc_chain.generator import generate_tests_for_mbpp


class TestOnlyMBPPBatchPipeline(BaseBatchPipeline):
    """只生成测试的MBPP Pipeline"""
    
    def __init__(self, model="gpt-4o-mini"):
        super().__init__(model)
    
    def read_problems(self, problem_file: str) -> Dict[str, Any]:
        """复用MBPP的问题读取逻辑"""
        problems = {}
        with open(problem_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    task_id = str(data['task_id'])
                    problems[task_id] = data
        return problems
    
    def get_output_filename(self, num_tasks, prefix):
        """实现抽象方法"""
        return os.path.join("benchmarks", "mbpp", "data", f"{prefix}_{num_tasks}_tasks_{self.model}.jsonl")
    
    def generate_batch_output_filename(self, num_tasks: int, prefix: str) -> str:
        """生成输出文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{num_tasks}_tasks_{self.model}_{timestamp}.jsonl"
        return os.path.join("benchmarks", "mbpp", "data", filename)
    
    def create_sample(self, task_id: str, problem: Dict[str, Any], generated_tests: str, error: str = None) -> Dict[str, Any]:
        """创建样本数据"""
        sample = {
            "task_id": task_id,
            "prompt": problem['text'],
            "reference_code": problem.get('code', ''),
            "generated_tests": generated_tests,
            "method": "test_only_mbpp",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": "test_generation_only"
        }
        if error:
            sample["error"] = error
        return sample
    
    def save_results(self, output_file: str, samples: list):
        """保存结果"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    def get_prompt(self, problem):
        """返回问题描述"""
        return problem['text']
    
    def run_batch_pipeline(self, problem_file: str, num_tasks: int = 10, start_task: int = 0):
        """运行测试生成Pipeline"""
        try:
            # 生成输出文件名
            output_file = self.generate_batch_output_filename(num_tasks, "test_only_mbpp_batch")
            
            # 读取问题
            print(f"Reading MBPP problem file: {problem_file}")
            problems = self.read_problems(problem_file)
            print(f"Total MBPP problems available: {len(problems)}")
            
            # 使用所有可用任务（不过滤官方测试集）
            task_ids = list(problems.keys())
            task_ids.sort(key=int)
            
            end_task = min(start_task + num_tasks, len(task_ids))
            selected_task_ids = task_ids[start_task:end_task]
            
            print(f"Processing Test-Only MBPP tasks {selected_task_ids[0]} to {selected_task_ids[-1]} ({len(selected_task_ids)} tasks)")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # 只执行测试生成阶段
            samples = []
            for task_id in tqdm(selected_task_ids, desc="Test Generation"):
                problem = problems[task_id]
                try:
                    description = problem['text']
                    
                    # 生成测试
                    print(f"\nGenerating tests for task {task_id}")
                    reference_code = problem.get('code', '')
                    generated_tests = generate_tests_for_mbpp(description, reference_code, self.model)
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


def run_test_only_mbpp_pipeline(problem_file="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                               num_tasks=10, 
                               model="gpt-4o-mini",
                               start_task=0):
    """运行测试专用MBPP Pipeline"""
    pipeline = TestOnlyMBPPBatchPipeline(model)
    return pipeline.run_batch_pipeline(problem_file, num_tasks, start_task)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MBPP Test-Only Pipeline")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/mbpp/mbpp.jsonl", 
                       help="MBPP problem file path")
    
    args = parser.parse_args()
    
    print("Starting MBPP Test-Only Pipeline")
    print("=" * 50)
    
    output_file = run_test_only_mbpp_pipeline(
        problem_file=args.problem_file,
        num_tasks=args.num_tasks,
        model=args.model,
        start_task=args.start_task
    )
    
    if output_file:
        print("\nTest-only pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Use tests for code generation: batch_mbpp_code_only.py --test_file {output_file}")
        print(f"2. Analyze test quality: analyze_tdd_comprehensive.py {output_file}")
        print(f"3. View results: cat {output_file}")
    else:
        print("\nTest-only pipeline failed")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
