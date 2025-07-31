import json
import sys
sys.path.append('benchmarks/humaneval')
from human_eval.data import read_problems
import ast
import re

problems = read_problems('benchmarks/humaneval/data/HumanEval.jsonl')
samples = []
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250731_122842.jsonl', 'r') as f:
    for line in f:
        samples.append(json.loads(line.strip()))

def analyze_code_issues(code, task_id):
    """分析代码中的具体问题"""
    issues = []
    
    # 1. 语法检查
    try:
        wrapped = f'def test_func():\n{code if code.endswith("\n") else code+chr(10)}'
        ast.parse(wrapped)
    except SyntaxError as e:
        issues.append(f"SyntaxError: {str(e)}")
    
    # 2. 基本结构检查
    lines = code.split('\n')
    
    # 检查是否有return语句
    has_return = any('return' in line for line in lines)
    if not has_return:
        issues.append("Missing return statement")
    
    # 检查缩进问题
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
            
        # 检查elif/else缩进
        if stripped.startswith('elif ') or stripped.startswith('else:'):
            if i > 0:
                prev_line = lines[i-1].strip()
                if not (prev_line.startswith('if ') or prev_line.startswith('elif ')):
                    issues.append(f"Line {i+1}: elif/else without preceding if")
    
    # 3. 检查常见的逻辑错误模式
    code_lower = code.lower()
    
    # 检查是否有无限循环风险
    if 'while true' in code_lower and 'break' not in code_lower:
        issues.append("Potential infinite loop (while True without break)")
    
    # 检查是否有未定义的变量
    if 'result' in code_lower and 'result =' not in code_lower:
        issues.append("Variable 'result' used but not defined")
    
    # 检查是否有明显的逻辑错误
    if 'return true' in code_lower and 'return false' in code_lower:
        # 检查是否有条件判断
        if not any('if ' in line for line in lines):
            issues.append("Returns both True and False without condition")
    
    return issues

def analyze_specific_errors():
    """分析具体的错误模式"""
    error_patterns = {
        'missing_return': 0,
        'syntax_error': 0,
        'control_flow_error': 0,
        'logic_error': 0,
        'other': 0
    }
    
    detailed_errors = []
    
    for sample in samples:
        code = sample['completion']
        task_id = sample['task_id']
        
        issues = analyze_code_issues(code, task_id)
        
        if issues:
            error_type = 'other'
            if any('SyntaxError' in issue for issue in issues):
                error_type = 'syntax_error'
            elif any('elif/else without preceding if' in issue for issue in issues):
                error_type = 'control_flow_error'
            elif any('Missing return statement' in issue for issue in issues):
                error_type = 'missing_return'
            elif any('logic' in issue.lower() for issue in issues):
                error_type = 'logic_error'
            
            error_patterns[error_type] += 1
            
            detailed_errors.append({
                'task_id': task_id,
                'issues': issues,
                'code': code
            })
    
    return error_patterns, detailed_errors

# 执行分析
error_patterns, detailed_errors = analyze_specific_errors()

print("=== 错误模式统计 ===")
for pattern, count in error_patterns.items():
    print(f"{pattern}: {count}")

print(f"\n=== 详细错误分析 (共{len(detailed_errors)}个有问题的样本) ===")

# 按错误类型分组显示
for pattern in ['syntax_error', 'control_flow_error', 'missing_return', 'logic_error', 'other']:
    pattern_errors = [e for e in detailed_errors if any(pattern.replace('_', '') in issue.lower() for issue in e['issues'])]
    if pattern_errors:
        print(f"\n--- {pattern.upper()} 错误 ({len(pattern_errors)}个) ---")
        for error in pattern_errors[:3]:  # 只显示前3个例子
            print(f"\nTask: {error['task_id']}")
            print(f"Issues: {error['issues']}")
            print(f"Code:\n{error['code']}")
        if len(pattern_errors) > 3:
            print(f"... 还有 {len(pattern_errors) - 3} 个类似错误")

# 显示一些特别有问题的样本
print(f"\n=== 特别有问题的样本 ===")
for error in detailed_errors:
    if len(error['issues']) >= 3:  # 有3个或以上问题的样本
        print(f"\nTask: {error['task_id']} (有{len(error['issues'])}个问题)")
        print(f"Issues: {error['issues']}")
        print(f"Code:\n{error['code']}") 