#!/usr/bin/env python3
"""
MBPP代码专用Pipeline

使用已生成的测试来生成代码实现。用于测试数据复用和一致性检验。
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
from pipelines.lc_chain.generator import generate_implementation_with_tests


class CodeOnlyMBPPBatchPipeline(BaseBatchPipeline):
    """只生成代码的MBPP Pipeline"""
    
    def __init__(self, model="gpt-4o-mini"):
        super().__init__(model)
    
    def load_test_data(self, test_file: str) -> list:
        """加载测试数据"""
        samples = []
        with open(test_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    samples.append(json.loads(line))
        return samples
    
    def get_output_filename(self, num_tasks, prefix):
        """实现抽象方法"""
        return os.path.join("benchmarks", "mbpp", "data", f"{prefix}_{num_tasks}_tasks_{self.model}.jsonl")
    
    def generate_batch_output_filename(self, num_tasks: int, prefix: str) -> str:
        """生成输出文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{num_tasks}_tasks_{self.model}_{timestamp}.jsonl"
        return os.path.join("benchmarks", "mbpp", "data", filename)
    
    def create_sample(self, test_sample: Dict[str, Any], implementation: str, error: str = None) -> Dict[str, Any]:
        """创建样本数据"""
        sample = {
            "task_id": test_sample['task_id'],
            "prompt": test_sample['prompt'],
            "completion": implementation,
            "method": "code_only_mbpp",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "test_list": test_sample.get('test_list', []),
            "challenge_test_list": test_sample.get('challenge_test_list', []),
            "reference_code": test_sample.get('reference_code', ''),
            "generated_tests": test_sample.get('generated_tests', ''),
            "stage": "code_generation_only"
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
    
    def run_batch_pipeline(self, test_file: str, num_tasks: int = None):
        """运行代码生成Pipeline"""
        try:
            # 加载测试数据
            print(f"Loading test data from: {test_file}")
            test_samples = self.load_test_data(test_file)
            print(f"Loaded {len(test_samples)} test samples")
            
            # 确定处理数量
            if num_tasks is None:
                num_tasks = len(test_samples)
            else:
                num_tasks = min(num_tasks, len(test_samples))
            
            # 生成输出文件名
            output_file = self.generate_batch_output_filename(num_tasks, "code_only_mbpp_batch")
            
            print(f"Processing Code-Only MBPP tasks (0 to {num_tasks-1})")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # 只执行代码生成阶段
            samples = []
            for i in tqdm(range(num_tasks), desc="Code Generation"):
                test_sample = test_samples[i]
                try:
                    description = test_sample['prompt']
                    generated_tests = test_sample['generated_tests']
                    reference_code = test_sample.get('reference_code', '')
                    
                    # 生成代码实现
                    print(f"\nGenerating implementation for task {test_sample['task_id']}")
                    implementation = generate_implementation_with_tests(
                        description, generated_tests, reference_code, self.model
                    )
                    print(f"Implementation generated: {len(implementation)} characters")
                    
                    # 创建样本
                    sample = self.create_sample(test_sample, implementation)
                    samples.append(sample)
                    
                except Exception as e:
                    print(f"Error processing task {test_sample['task_id']}: {e}")
                    sample = self.create_sample(test_sample, "    pass", error=str(e))
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
            print(f"Code-only batch processing failed: {e}")
            return None
    
    def read_problems(self, problem_file: str) -> Dict[str, Any]:
        """实现抽象方法 - 代码专用Pipeline不需要读取问题文件"""
        return {}
    
    def get_prompt(self, problem):
        """实现抽象方法 - 代码专用Pipeline不需要获取prompt"""
        return ""


def run_code_only_mbpp_pipeline(test_file: str, 
                               num_tasks: int = None,
                               model: str = "gpt-4o-mini"):
    """运行代码专用MBPP Pipeline"""
    pipeline = CodeOnlyMBPPBatchPipeline(model)
    return pipeline.run_batch_pipeline(test_file, num_tasks)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MBPP Code-Only Pipeline")
    parser.add_argument("--test_file", required=True, help="Test file path")
    parser.add_argument("--num_tasks", type=int, default=None, help="Number of tasks to process (default: all)")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.test_file):
        print(f"Error: Test file {args.test_file} not found")
        import sys
        sys.exit(1)
    
    print("Starting MBPP Code-Only Pipeline")
    print("=" * 50)
    
    output_file = run_code_only_mbpp_pipeline(
        test_file=args.test_file,
        num_tasks=args.num_tasks,
        model=args.model
    )
    
    if output_file:
        print("\nCode-only pipeline completed successfully!")
        print(f"Result file: {output_file}")
        print("\nNext steps:")
        print(f"1. Run evaluation: analyze_mbpp_results_fixed.py {output_file}")
        print(f"2. View results: cat {output_file}")
    else:
        print("\nCode-only pipeline failed")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
