#!/usr/bin/env python3
"""
Test HumanEval TDD Pipeline
Simple test to verify HumanEval TDD pipeline functionality
"""

import sys
import os
sys.path.append('.')

from pipelines.lc_chain.generator import (
    generate_tests_for_humaneval, 
    generate_implementation_with_tests_humaneval
)

def test_humaneval_tdd_pipeline():
    """测试HumanEval TDD管道的两阶段流程"""
    
    # 测试函数签名和参考答案
    test_prompt = """def has_close_elements(numbers: List[float], threshold: float) -> bool:
    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True

    return False"""
    
    test_canonical_solution = """    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True

    return False"""
    
    print("Testing HumanEval TDD Pipeline")
    print("=" * 50)
    print(f"Function signature: {test_prompt.split('def ')[1].split('(')[0]}")
    print()
    
    try:
        # 阶段1：生成测试
        print("🔄 Stage 1: Generating tests...")
        generated_tests = generate_tests_for_humaneval(test_prompt, test_canonical_solution)
        print("✅ Tests generated:")
        print(generated_tests)
        print()
        
        # 阶段2：生成实现
        print("🔄 Stage 2: Generating implementation...")
        implementation = generate_implementation_with_tests_humaneval(test_prompt, generated_tests)
        print("✅ Implementation generated:")
        print(implementation)
        print()
        
        print("🎉 HumanEval TDD pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ HumanEval TDD pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_humaneval_tdd_pipeline()
    sys.exit(0 if success else 1)
