#!/usr/bin/env python3
"""
Test TDD Pipeline
Simple test to verify TDD pipeline functionality
"""

import sys
import os
sys.path.append('.')

from pipelines.lc_chain.generator import (
    generate_tests_for_mbpp, 
    generate_implementation_with_tests
)

def test_tdd_pipeline():
    """测试TDD管道的两阶段流程"""
    
    # 测试问题描述
    test_description = """
    Write a function that takes a list of integers and returns the sum of all even numbers in the list.
    If the list is empty, return 0.
    """
    
    print("Testing TDD Pipeline")
    print("=" * 50)
    print(f"Problem: {test_description.strip()}")
    print()
    
    try:
        # 阶段1：生成测试
        print("🔄 Stage 1: Generating tests...")
        reference_code = """def sum_even_numbers(numbers):
    return sum(num for num in numbers if isinstance(num, int) and num % 2 == 0)"""
        generated_tests = generate_tests_for_mbpp(test_description, reference_code)
        print("✅ Tests generated:")
        print(generated_tests)
        print()
        
        # 阶段2：生成实现
        print("🔄 Stage 2: Generating implementation...")
        implementation = generate_implementation_with_tests(test_description, generated_tests, reference_code)
        print("✅ Implementation generated:")
        print(implementation)
        print()
        
        print("🎉 TDD pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ TDD pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_tdd_pipeline()
    sys.exit(0 if success else 1)
