import json
import sys
sys.path.append('benchmarks/humaneval')
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

def analyze_logic_patterns(code, task_id):
    """分析代码中的逻辑模式"""
    patterns = []
    lines = code.split('\n')
    
    # 1. 检查是否有return语句
    has_return = any('return' in line for line in lines)
    if not has_return:
        patterns.append("No return statement")
    
    # 2. 检查return语句的位置
    return_lines = [i for i, line in enumerate(lines) if 'return' in line]
    if len(return_lines) > 1:
        # 检查是否有条件return
        has_conditional_return = any('if ' in lines[i-1] for i in return_lines if i > 0)
        if not has_conditional_return:
            patterns.append("Multiple returns without conditions")
    
    # 3. 检查循环结构
    has_for = any('for ' in line for line in lines)
    has_while = any('while ' in line for line in lines)
    if has_while and not any('break' in line for line in lines):
        patterns.append("While loop without break")
    
    # 4. 检查条件结构
    if_count = sum(1 for line in lines if line.strip().startswith('if '))
    elif_count = sum(1 for line in lines if line.strip().startswith('elif '))
    else_count = sum(1 for line in lines if line.strip().startswith('else:'))
    
    if if_count == 0 and (elif_count > 0 or else_count > 0):
        patterns.append("elif/else without if")
    
    # 5. 检查变量使用
    code_lower = code.lower()
    if 'result' in code_lower and 'result =' not in code_lower:
        patterns.append("Uses 'result' but doesn't define it")
    
    # 6. 检查函数调用
    if 'append' in code_lower and '[]' not in code_lower and 'list' not in code_lower:
        patterns.append("Uses append but may not have list")
    
    # 7. 检查字符串操作
    if 'split' in code_lower and 'join' not in code_lower:
        patterns.append("Splits but doesn't join")
    
    return patterns

# 分离语法正确和错误的样本
syntax_correct = []
syntax_errors = []

for sample in samples:
    if check_syntax(sample['completion']):
        syntax_correct.append(sample)
    else:
        syntax_errors.append(sample)

print(f"=== 样本分类 ===")
print(f"语法正确: {len(syntax_correct)}")
print(f"语法错误: {len(syntax_errors)}")

print(f"\n=== 语法正确样本的逻辑模式分析 ===")
logic_patterns = {}
pattern_examples = {}

for sample in syntax_correct:
    patterns = analyze_logic_patterns(sample['completion'], sample['task_id'])
    
    for pattern in patterns:
        logic_patterns[pattern] = logic_patterns.get(pattern, 0) + 1
        if pattern not in pattern_examples:
            pattern_examples[pattern] = {
                'task_id': sample['task_id'],
                'code': sample['completion'],
                'patterns': patterns
            }

print(f"\n逻辑模式统计:")
for pattern, count in sorted(logic_patterns.items(), key=lambda x: x[1], reverse=True):
    print(f"{pattern}: {count}")

print(f"\n=== 逻辑模式示例 ===")
for pattern, example in pattern_examples.items():
    print(f"\n--- {pattern} ---")
    print(f"Task: {example['task_id']}")
    print(f"All patterns: {example['patterns']}")
    print(f"Code:\n{example['code']}")

# 分析一些特别简单的样本
print(f"\n=== 简单样本分析 ===")
simple_samples = []
for sample in syntax_correct:
    code = sample['completion']
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    if len(lines) <= 5:  # 5行或更少的样本
        simple_samples.append(sample)

print(f"简单样本数量: {len(simple_samples)}")
for i, sample in enumerate(simple_samples[:5]):  # 显示前5个
    print(f"\n简单样本 {i+1}: {sample['task_id']}")
    print(f"Code:\n{sample['completion']}")
    patterns = analyze_logic_patterns(sample['completion'], sample['task_id'])
    print(f"Patterns: {patterns}")

# 分析一些复杂的样本
print(f"\n=== 复杂样本分析 ===")
complex_samples = []
for sample in syntax_correct:
    code = sample['completion']
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    if len(lines) >= 15:  # 15行或更多的样本
        complex_samples.append(sample)

print(f"复杂样本数量: {len(complex_samples)}")
for i, sample in enumerate(complex_samples[:3]):  # 显示前3个
    print(f"\n复杂样本 {i+1}: {sample['task_id']}")
    print(f"Code:\n{sample['completion']}")
    patterns = analyze_logic_patterns(sample['completion'], sample['task_id'])
    print(f"Patterns: {patterns}") 