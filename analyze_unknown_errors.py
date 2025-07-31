import json
import sys
sys.path.append('benchmarks/humaneval')
from human_eval.data import read_problems
import ast
import traceback

problems = read_problems('benchmarks/humaneval/data/HumanEval.jsonl')
samples = []
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250731_154121.jsonl', 'r') as f:
    for line in f:
        samples.append(json.loads(line.strip()))

def check_syntax(code):
    """检查代码语法是否正确"""
    try:
        wrapped = f'def test_func():\n{code if code.endswith("\n") else code+chr(10)}'
        ast.parse(wrapped)
        return True
    except SyntaxError:
        return False

def analyze_specific_error(code, task_id):
    """分析具体的错误原因"""
    try:
        # 获取测试用例
        problem = problems[task_id]
        test_cases = problem['test']
        
        # 构造完整的函数
        function_code = f"""
{code}
"""
        
        # 创建本地环境
        local_env = {}
        
        # 执行函数定义
        exec(function_code, {}, local_env)
        
        # 获取函数对象
        func_name = problem['entry_point']
        if func_name not in local_env:
            return f"Function '{func_name}' not found in code"
        
        func = local_env[func_name]
        
        # 运行测试用例
        for i, test_case in enumerate(test_cases):
            try:
                # 提取测试用例的代码
                test_lines = test_case.strip().split('\n')
                for line in test_lines:
                    if line.strip() and not line.strip().startswith('#'):
                        # 执行测试行
                        exec(line, local_env)
                        break
            except Exception as e:
                return f"Test case {i+1} failed: {type(e).__name__}: {str(e)}"
        
        return "All test cases passed"
        
    except Exception as e:
        return f"Execution error: {type(e).__name__}: {str(e)}"

def analyze_code_patterns(code):
    """分析代码中的问题模式"""
    issues = []
    lines = code.split('\n')
    
    # 1. 检查循环中的提前返回
    for i, line in enumerate(lines):
        if 'for ' in line or 'while ' in line:
            # 查找循环内的return语句
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith('return '):
                    # 检查是否在循环内
                    if j < len(lines) - 1:
                        next_line = lines[j+1].strip()
                        if next_line and not next_line.startswith(('if ', 'elif ', 'else:', 'return ')):
                            issues.append(f"Early return in loop at line {j+1}")
                    break
    
    # 2. 检查条件逻辑
    if_count = sum(1 for line in lines if line.strip().startswith('if '))
    return_count = sum(1 for line in lines if 'return ' in line)
    
    if if_count > 0 and return_count > if_count:
        issues.append("More returns than if statements")
    
    # 3. 检查变量使用
    code_lower = code.lower()
    if 'result' in code_lower and 'result =' not in code_lower:
        issues.append("Uses 'result' but doesn't define it")
    
    # 4. 检查字符串操作
    if 'split' in code_lower and 'join' not in code_lower:
        issues.append("Splits but doesn't join")
    
    return issues

# 分析UnknownError样本
unknown_errors = []
syntax_correct = []

for sample in samples:
    code = sample['completion']
    task_id = sample['task_id']
    
    if check_syntax(code):
        syntax_correct.append(sample)
        # 这里我们模拟UnknownError的情况
        # 实际上我们需要运行测试来获取具体错误
        issues = analyze_code_patterns(code)
        if issues:  # 假设有问题的代码会导致UnknownError
            unknown_errors.append({
                'task_id': task_id,
                'code': code,
                'issues': issues
            })

print(f"=== UnknownError 详细分析 ===")
print(f"语法正确样本: {len(syntax_correct)}")
print(f"有问题的样本: {len(unknown_errors)}")

# 按问题类型分组
issue_types = {}
for error in unknown_errors:
    for issue in error['issues']:
        issue_types[issue] = issue_types.get(issue, 0) + 1

print(f"\n=== 问题类型分布 ===")
for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
    print(f"{issue_type}: {count}")

# 显示具体的错误案例
print(f"\n=== 具体错误案例 ===")
for i, error in enumerate(unknown_errors[:10]):  # 显示前10个
    print(f"\n--- 案例 {i+1}: {error['task_id']} ---")
    print(f"问题: {error['issues']}")
    print(f"代码:\n{error['code']}")

# 分析一些典型的错误模式
print(f"\n=== 典型错误模式分析 ===")

# 1. 循环提前返回
early_return_errors = [e for e in unknown_errors if any('Early return in loop' in issue for issue in e['issues'])]
print(f"\n循环提前返回错误: {len(early_return_errors)}个")
for i, error in enumerate(early_return_errors[:3]):
    print(f"\n--- 循环提前返回 {i+1}: {error['task_id']} ---")
    print(f"代码:\n{error['code']}")

# 2. 条件逻辑错误
condition_errors = [e for e in unknown_errors if any('More returns than if' in issue for issue in e['issues'])]
print(f"\n条件逻辑错误: {len(condition_errors)}个")
for i, error in enumerate(condition_errors[:3]):
    print(f"\n--- 条件逻辑错误 {i+1}: {error['task_id']} ---")
    print(f"代码:\n{error['code']}")

# 3. 字符串操作错误
string_errors = [e for e in unknown_errors if any('Splits but doesn\'t join' in issue for issue in e['issues'])]
print(f"\n字符串操作错误: {len(string_errors)}个")
for i, error in enumerate(string_errors[:3]):
    print(f"\n--- 字符串操作错误 {i+1}: {error['task_id']} ---")
    print(f"代码:\n{error['code']}")

# 分析简单样本的错误
simple_errors = []
for error in unknown_errors:
    lines = [line.strip() for line in error['code'].split('\n') if line.strip()]
    if len(lines) <= 5:
        simple_errors.append(error)

print(f"\n=== 简单样本错误分析 ===")
print(f"简单错误样本: {len(simple_errors)}个")
for i, error in enumerate(simple_errors[:5]):
    print(f"\n--- 简单错误 {i+1}: {error['task_id']} ---")
    print(f"问题: {error['issues']}")
    print(f"代码:\n{error['code']}") 