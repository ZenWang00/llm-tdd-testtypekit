#!/usr/bin/env python3
"""
Fixed MBPP Results Analysis
Properly handles function name mismatches between generated code and test cases
"""

import json
import subprocess
import tempfile
import os
import sys
import argparse
from tqdm import tqdm
from collections import defaultdict

def extract_function_name(completion):
    """从生成的代码中提取函数名"""
    lines = completion.split('\n')
    for line in lines:
        if line.strip().startswith('def '):
            # 提取函数名：def function_name(...)
            func_def = line.strip()
            func_name = func_def.split('(')[0].split('def ')[1].strip()
            return func_name
    return None

def check_mbpp_sample(sample):
    """检查单个MBPP样本的正确性"""
    try:
        completion = sample['completion']
        test_list = sample.get('test_list', [])
        
        # 提取生成的函数名
        generated_func_name = extract_function_name(completion)
        if not generated_func_name:
            return 'SyntaxError', 'No function definition found'
        
        # 构造测试代码
        test_code = f"{completion}\n"
        
        # 分析测试用例中的函数名模式
        test_func_names = set()
        for test in test_list:
            # 提取测试用例中的函数名（在assert之后，第一个括号之前）
            if test.startswith('assert '):
                func_call = test[7:]  # 去掉"assert "
                func_name = func_call.split('(')[0].strip()
                test_func_names.add(func_name)
        
        # 如果测试用例中的函数名与生成的函数名不同，需要替换
        if test_func_names and list(test_func_names)[0] != generated_func_name:
            old_func_name = list(test_func_names)[0]
            for test in test_list:
                # 替换测试用例中的函数名
                modified_test = test.replace(old_func_name, generated_func_name)
                test_code += f"{modified_test}\n"
        else:
            # 直接使用原始测试用例
            for test in test_list:
                test_code += f"{test}\n"
        
        # 执行测试
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=3.0
            )
            
            if result.returncode == 0 and not result.stderr:
                return 'Pass', 'All tests passed'
            else:
                error_output = result.stderr or result.stdout
                if 'AssertionError' in error_output:
                    return 'AssertionError', error_output
                elif 'SyntaxError' in error_output:
                    return 'SyntaxError', error_output
                elif 'NameError' in error_output:
                    return 'NameError', error_output
                elif 'TypeError' in error_output:
                    return 'TypeError', error_output
                else:
                    return 'RuntimeError', error_output
                    
        finally:
            os.unlink(temp_file)
            
    except subprocess.TimeoutExpired:
        return 'Timeout', 'Execution timeout'
    except Exception as e:
        return 'UnknownError', str(e)

def analyze_mbpp_results(result_file):
    """分析MBPP结果文件"""
    print(f"Analyzing results: {result_file}")
    
    samples = []
    with open(result_file, 'r') as f:
        for line in f:
            sample = json.loads(line.strip())
            samples.append(sample)
    
    print(f"Total samples: {len(samples)}")
    
    # 统计结果
    results = []
    error_types = defaultdict(int)
    
    for sample in tqdm(samples, desc="Analyzing results"):
        result_type, result_msg = check_mbpp_sample(sample)
        results.append((sample['task_id'], result_type, result_msg))
        
        if result_type == 'Pass':
            error_types['Pass'] += 1
        else:
            error_types[result_type] += 1
    
    # 输出统计
    passed = error_types.get('Pass', 0)
    total = len(samples)
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n=== MBPP Results Summary ===")
    print(f"Total samples: {total}")
    print(f"Passed: {passed} ({pass_rate:.2f}%)")
    print(f"Failed: {total - passed}")
    
    print(f"\nError type distribution:")
    for error_type, count in sorted(error_types.items()):
        percentage = (count / total) * 100
        print(f"  {error_type}: {count} ({percentage:.1f}%)")
    
    # 显示失败案例的详细信息
    failed_cases = [(tid, error_type, msg) for tid, error_type, msg in results if error_type != 'Pass']
    
    if failed_cases:
        print(f"\nExamples of failed cases:")
        for i, (task_id, error_type, error_msg) in enumerate(failed_cases[:5]):  # 只显示前5个
            print(f"---")
            print(f"Task: {task_id}")
            print(f"Error: {error_type}")
            print(f"Message: {error_msg[:200]}...")  # 截断长消息
            
            # 显示生成的代码
            sample = next(s for s in samples if s['task_id'] == task_id)
            print(f"Generated code:")
            print(f"{sample['completion'][:300]}...")  # 截断长代码
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Analyze MBPP results')
    parser.add_argument('--result_file', required=True, help='Path to MBPP result file')
    args = parser.parse_args()
    
    analyze_mbpp_results(args.result_file)

if __name__ == "__main__":
    main() 