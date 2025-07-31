import json
import ast
import subprocess
import tempfile
import os
import sys

def read_mbpp_problems(file_path):
    """读取MBPP问题"""
    problems = {}
    with open(file_path, 'r') as f:
        for line in f:
            problem = json.loads(line.strip())
            problems[problem['task_id']] = problem
    return problems

def check_correctness_mbpp(problem, completion, timeout=3.0):
    """检查MBPP问题的正确性"""
    try:
        # 构造完整的代码（函数定义 + 测试用例）
        test_code = f"{completion}\n"
        
        # 添加测试用例
        for test in problem['test_list']:
            test_code += f"{test}\n"
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # 执行代码
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # 检查是否成功执行（没有错误输出）
            return result.returncode == 0 and not result.stderr
            
        finally:
            # 清理临时文件
            os.unlink(temp_file)
            
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_mbpp_evaluation():
    """测试MBPP评估逻辑"""
    # 读取MBPP数据
    problems = read_mbpp_problems('benchmarks/mbpp/mbpp/mbpp.jsonl')
    
    # 测试第一个问题
    problem = problems[1]
    print(f"Testing problem {problem['task_id']}: {problem['text'][:100]}...")
    
    # 使用原始代码作为"候选代码"
    candidate_code = problem['code']
    
    # 检查正确性
    is_correct = check_correctness_mbpp(problem, candidate_code)
    
    print(f"Original code correctness: {is_correct}")
    
    # 测试一个错误的代码
    wrong_code = "def min_cost(cost, m, n):\n    return 0"  # 总是返回0
    is_wrong = check_correctness_mbpp(problem, wrong_code)
    
    print(f"Wrong code correctness: {is_wrong}")
    
    # 显示测试用例
    print(f"\nTest cases:")
    for i, test in enumerate(problem['test_list']):
        print(f"  {i+1}. {test}")

if __name__ == "__main__":
    test_mbpp_evaluation() 