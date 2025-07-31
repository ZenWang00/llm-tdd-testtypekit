import json
import sys
sys.path.append('benchmarks/humaneval')
from human_eval.execution import check_correctness
from human_eval.data import read_problems
import ast

problems = read_problems('benchmarks/humaneval/data/HumanEval.jsonl')
samples = []
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250731_141844.jsonl', 'r') as f:
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

def analyze_logic_error(code, task_id):
    """分析代码中的逻辑错误"""
    issues = []
    lines = code.split('\n')
    
    # 1. 检查return语句问题
    return_lines = [i for i, line in enumerate(lines) if 'return' in line]
    if len(return_lines) > 1:
        # 检查是否有条件return
        has_conditional_return = False
        for i in return_lines:
            if i > 0 and 'if ' in lines[i-1]:
                has_conditional_return = True
                break
        if not has_conditional_return:
            issues.append("Multiple returns without conditions")
    
    # 2. 检查循环问题
    has_while = any('while ' in line for line in lines)
    has_break = any('break' in line for line in lines)
    if has_while and not has_break:
        issues.append("While loop without break")
    
    # 3. 检查变量使用问题
    code_lower = code.lower()
    if 'result' in code_lower and 'result =' not in code_lower:
        issues.append("Uses 'result' but doesn't define it")
    
    # 4. 检查字符串操作问题
    if 'split' in code_lower and 'join' not in code_lower:
        issues.append("Splits but doesn't join")
    
    # 5. 检查逻辑结构问题
    if_count = sum(1 for line in lines if line.strip().startswith('if '))
    else_count = sum(1 for line in lines if line.strip().startswith('else:'))
    elif_count = sum(1 for line in lines if line.strip().startswith('elif '))
    
    if if_count == 0 and (else_count > 0 or elif_count > 0):
        issues.append("elif/else without if")
    
    # 6. 检查函数调用问题
    if 'append' in code_lower and '[]' not in code_lower and 'list' not in code_lower:
        issues.append("Uses append but may not have list")
    
    return issues

# 分析所有样本
syntax_correct = []
syntax_errors = []
logic_failures = []

for sample in samples:
    code = sample['completion']
    task_id = sample['task_id']
    
    if check_syntax(code):
        syntax_correct.append(sample)
        # 检查功能测试
        try:
            result = check_correctness(problems[task_id], code, timeout=3.0)
            if not result['passed']:
                logic_failures.append({
                    'task_id': task_id,
                    'code': code,
                    'error': result.get('error', 'UnknownError'),
                    'logic_issues': analyze_logic_error(code, task_id)
                })
        except Exception as e:
            print(f"Error testing {task_id}: {e}")
    else:
        syntax_errors.append(sample)

print(f"=== 样本分类 ===")
print(f"语法正确: {len(syntax_correct)}")
print(f"语法错误: {len(syntax_errors)}")
print(f"逻辑失败: {len(logic_failures)}")

# 分析逻辑错误类型
error_types = {}
logic_issue_types = {}

for failure in logic_failures:
    error_type = failure['error']
    error_types[error_type] = error_types.get(error_type, 0) + 1
    
    for issue in failure['logic_issues']:
        logic_issue_types[issue] = logic_issue_types.get(issue, 0) + 1

print(f"\n=== 错误类型分布 ===")
for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
    print(f"{error_type}: {count}")

print(f"\n=== 逻辑问题类型分布 ===")
for issue_type, count in sorted(logic_issue_types.items(), key=lambda x: x[1], reverse=True):
    print(f"{issue_type}: {count}")

# 显示一些典型的逻辑错误案例
print(f"\n=== 典型逻辑错误案例 ===")
for i, failure in enumerate(logic_failures[:10]):  # 显示前10个
    print(f"\n--- 案例 {i+1}: {failure['task_id']} ---")
    print(f"错误类型: {failure['error']}")
    print(f"逻辑问题: {failure['logic_issues']}")
    print(f"代码:\n{failure['code']}")

# 分析一些特别有问题的样本
print(f"\n=== 特别有问题的样本 ===")
for failure in logic_failures:
    if len(failure['logic_issues']) >= 3:  # 有3个或以上逻辑问题
        print(f"\n--- {failure['task_id']} (有{len(failure['logic_issues'])}个逻辑问题) ---")
        print(f"错误类型: {failure['error']}")
        print(f"逻辑问题: {failure['logic_issues']}")
        print(f"代码:\n{failure['code']}")

# 分析简单但失败的样本
print(f"\n=== 简单但失败的样本 ===")
simple_failures = []
for failure in logic_failures:
    lines = [line.strip() for line in failure['code'].split('\n') if line.strip()]
    if len(lines) <= 5:  # 5行或更少
        simple_failures.append(failure)

print(f"简单失败样本数量: {len(simple_failures)}")
for i, failure in enumerate(simple_failures[:5]):  # 显示前5个
    print(f"\n--- 简单失败 {i+1}: {failure['task_id']} ---")
    print(f"错误类型: {failure['error']}")
    print(f"逻辑问题: {failure['logic_issues']}")
    print(f"代码:\n{failure['code']}") 