import json
import ast
import subprocess
import tempfile
import os
import sys
from tqdm import tqdm

def check_mbpp_sample(sample, timeout=3.0):
    """检查单个MBPP样本的正确性，返回(True/False, 错误类型/None)"""
    code = sample['completion']
    test_list = sample.get('test_list', [])
    if not code.strip():
        return False, 'EmptyCode'
    # 拼接代码和测试用例
    test_code = f"{code}\n"
    for test in test_list:
        test_code += f"{test}\n"
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    try:
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0 and not result.stderr:
            return True, None
        # 语法错误检测
        try:
            ast.parse(code)
        except SyntaxError:
            return False, 'SyntaxError'
        # 其他错误类型
        if 'AssertionError' in result.stderr:
            return False, 'AssertionError'
        if 'Timeout' in result.stderr:
            return False, 'Timeout'
        if result.stderr:
            return False, result.stderr.strip().split('\n')[0][:100]
        return False, 'UnknownError'
    except subprocess.TimeoutExpired:
        return False, 'Timeout'
    finally:
        os.unlink(temp_file)

def analyze_mbpp_results(result_file):
    with open(result_file, 'r') as f:
        samples = [json.loads(line.strip()) for line in f]
    total = len(samples)
    passed = 0
    error_types = {}
    failed_cases = []
    for sample in tqdm(samples, desc='Analyzing results'):
        ok, err = check_mbpp_sample(sample)
        if ok:
            passed += 1
        else:
            error_types[err] = error_types.get(err, 0) + 1
            failed_cases.append({'task_id': sample['task_id'], 'error': err, 'code': sample['completion']})
    print(f"Total samples: {total}")
    print(f"Passed: {passed} ({passed/total*100:.2f}%)")
    print(f"Failed: {total-passed}")
    print("\nError type distribution:")
    for k, v in sorted(error_types.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\nExamples of failed cases:")
    for case in failed_cases[:5]:
        print(f"---\nTask: {case['task_id']}\nError: {case['error']}\nCode:\n{case['code'][:300]}\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze MBPP LangChain results")
    parser.add_argument('--result_file', type=str, required=True, help='Path to result jsonl file')
    args = parser.parse_args()
    analyze_mbpp_results(args.result_file) 