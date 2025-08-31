#!/usr/bin/env python3
"""
测试新的Pipeline架构

验证测试专用和代码专用Pipeline的功能
"""

import os
import json
import tempfile
from pipelines.batch_mbpp_test_only import TestOnlyMBPPBatchPipeline
from pipelines.batch_humaneval_test_only import TestOnlyHumanEvalBatchPipeline
from pipelines.batch_mbpp_code_only import CodeOnlyMBPPBatchPipeline
from pipelines.batch_humaneval_code_only import CodeOnlyHumanEvalBatchPipeline


def test_mbpp_test_only_pipeline():
    """测试MBPP测试专用Pipeline"""
    print("Testing MBPP Test-Only Pipeline")
    print("=" * 50)
    
    # 创建临时测试数据
    test_data = [
        {
            "task_id": 1,
            "text": "Write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix cost[][] and a position (m, n) in cost[][].",
            "code": "def min_cost(cost, m, n):\n    # implementation here\n    pass"
        },
        {
            "task_id": 2,
            "text": "Write a function to check if a string is a palindrome.",
            "code": "def is_palindrome(s):\n    # implementation here\n    pass"
        }
    ]
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        temp_file = f.name
    
    try:
        # 测试Pipeline
        pipeline = TestOnlyMBPPBatchPipeline("gpt-4o-mini")
        
        # 模拟运行（不实际调用API）
        print(f"Created pipeline with model: {pipeline.model}")
        print(f"Test data loaded from: {temp_file}")
        
        # 测试文件名生成
        filename = pipeline.generate_batch_output_filename(2, "test_only_mbpp_batch")
        print(f"Generated filename: {filename}")
        
        # 测试样本创建
        sample = pipeline.create_sample("1", test_data[0], "def test_min_cost(): pass")
        print(f"Sample created: {sample['task_id']}, method: {sample['method']}, stage: {sample['stage']}")
        
        print("MBPP Test-Only Pipeline test passed!")
        
    finally:
        # 清理临时文件
        os.unlink(temp_file)


def test_humaneval_test_only_pipeline():
    """测试HumanEval测试专用Pipeline"""
    print("\nTesting HumanEval Test-Only Pipeline")
    print("=" * 50)
    
    # 创建临时测试数据
    test_data = [
        {
            "task_id": "HumanEval/1",
            "prompt": "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    \"\"\"\n    pass",
            "canonical_solution": "for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n    return False"
        }
    ]
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        temp_file = f.name
    
    try:
        # 测试Pipeline
        pipeline = TestOnlyHumanEvalBatchPipeline("gpt-4o-mini")
        
        # 模拟运行（不实际调用API）
        print(f"Created pipeline with model: {pipeline.model}")
        print(f"Test data loaded from: {temp_file}")
        
        # 测试文件名生成
        filename = pipeline.generate_batch_output_filename(1, "test_only_humaneval_batch")
        print(f"Generated filename: {filename}")
        
        # 测试样本创建
        sample = pipeline.create_sample("HumanEval/1", test_data[0], "def test_has_close_elements(): pass")
        print(f"Sample created: {sample['task_id']}, method: {sample['method']}, stage: {sample['stage']}")
        
        print("HumanEval Test-Only Pipeline test passed!")
        
    finally:
        # 清理临时文件
        os.unlink(temp_file)


def test_mbpp_code_only_pipeline():
    """测试MBPP代码专用Pipeline"""
    print("\nTesting MBPP Code-Only Pipeline")
    print("=" * 50)
    
    # 创建临时测试数据
    test_data = [
        {
            "task_id": 1,
            "prompt": "Write a function to find the minimum cost path...",
            "reference_code": "def min_cost(cost, m, n):\n    pass",
            "generated_tests": "def test_min_cost(): pass"
        }
    ]
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        temp_file = f.name
    
    try:
        # 测试Pipeline
        pipeline = CodeOnlyMBPPBatchPipeline("gpt-4o-mini")
        
        # 测试数据加载
        samples = pipeline.load_test_data(temp_file)
        print(f"Loaded {len(samples)} test samples")
        
        # 测试文件名生成
        filename = pipeline.generate_batch_output_filename(1, "code_only_mbpp_batch")
        print(f"Generated filename: {filename}")
        
        # 测试样本创建
        sample = pipeline.create_sample(test_data[0], "def min_cost(cost, m, n):\n    return 0")
        print(f"Sample created: {sample['task_id']}, method: {sample['method']}, stage: {sample['stage']}")
        
        print("MBPP Code-Only Pipeline test passed!")
        
    finally:
        # 清理临时文件
        os.unlink(temp_file)


def test_humaneval_code_only_pipeline():
    """测试HumanEval代码专用Pipeline"""
    print("\nTesting HumanEval Code-Only Pipeline")
    print("=" * 50)
    
    # 创建临时测试数据
    test_data = [
        {
            "task_id": "HumanEval/1",
            "prompt": "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n    pass",
            "canonical_solution": "pass",
            "generated_tests": "def test_has_close_elements(): pass"
        }
    ]
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
        temp_file = f.name
    
    try:
        # 测试Pipeline
        pipeline = CodeOnlyHumanEvalBatchPipeline("gpt-4o-mini")
        
        # 测试数据加载
        samples = pipeline.load_test_data(temp_file)
        print(f"Loaded {len(samples)} test samples")
        
        # 测试文件名生成
        filename = pipeline.generate_batch_output_filename(1, "code_only_humaneval_batch")
        print(f"Generated filename: {filename}")
        
        # 测试样本创建
        sample = pipeline.create_sample(test_data[0], "    return False")
        print(f"Sample created: {sample['task_id']}, method: {sample['method']}, stage: {sample['stage']}")
        
        print("HumanEval Code-Only Pipeline test passed!")
        
    finally:
        # 清理临时文件
        os.unlink(temp_file)


def main():
    """主测试函数"""
    print("Testing New Pipeline Architecture")
    print("=" * 60)
    
    try:
        test_mbpp_test_only_pipeline()
        test_humaneval_test_only_pipeline()
        test_mbpp_code_only_pipeline()
        test_humaneval_code_only_pipeline()
        
        print("\n" + "=" * 60)
        print("All pipeline tests passed!")
        print("\nPipeline architecture summary:")
        print("- Test-Only Pipelines: Generate tests only, save separately")
        print("- Code-Only Pipelines: Use saved tests to generate code")
        print("- File naming: test_only_*_batch_*.jsonl, code_only_*_batch_*.jsonl")
        print("- Data fields: stage, method, generated_tests preserved")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
