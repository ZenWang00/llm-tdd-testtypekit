import json
import ast
import re

def fix_missing_colons(lines):
    control_keywords = (
        'if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally'
    )
    fixed = []
    for line in lines:
        stripped = line.strip()
        # 跳过空行
        if not stripped:
            fixed.append(line)
            continue
        # 检查是否是控制流语句且缺冒号
        for kw in control_keywords:
            if (stripped.startswith(kw) and not stripped.endswith(':')):
                # 允许else/try/finally/except后面直接冒号或带条件
                if not re.match(r'.+:$', stripped):
                    line = line.rstrip() + ':'
                break
        fixed.append(line)
    return fixed

def fix_unclosed_brackets_and_quotes(code):
    # 括号
    pairs = [('(', ')'), ('[', ']'), ('{', '}')]
    for left, right in pairs:
        n_left = code.count(left)
        n_right = code.count(right)
        if n_left > n_right:
            code += right * (n_left - n_right)
    # 引号
    for q in ["'", '"']:
        if code.count(q) % 2 == 1:
            code += q
    return code

samples = []
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250730_164334.jsonl', 'r') as f:
    for line in f:
        samples.append(json.loads(line.strip()))

syntax_errors_before = []
syntax_errors_after = []
fixed_samples = []

for sample in samples:
    code = sample['completion']
    # 先做AST检查
    try:
        wrapped = f'def test_func():\n{code if code.endswith("\n") else code+chr(10)}'
        ast.parse(wrapped)
        fixed_samples.append(sample)
        continue
    except SyntaxError as e:
        syntax_errors_before.append({'task_id': sample['task_id'], 'error': str(e), 'code': code})
    # 尝试修复
    lines = code.split('\n')
    lines = fix_missing_colons(lines)
    fixed_code = '\n'.join(lines)
    fixed_code = fix_unclosed_brackets_and_quotes(fixed_code)
    # 再次AST检查
    try:
        wrapped = f'def test_func():\n{fixed_code if fixed_code.endswith("\n") else fixed_code+chr(10)}'
        ast.parse(wrapped)
        sample['completion'] = fixed_code
        fixed_samples.append(sample)
    except SyntaxError as e:
        syntax_errors_after.append({'task_id': sample['task_id'], 'error': str(e), 'code': fixed_code})

print(f'原始语法错误数: {len(syntax_errors_before)}')
print(f'修复后语法错误数: {len(syntax_errors_after)}')
if syntax_errors_after:
    print('\n修复后仍有语法错误的样本:')
    for err in syntax_errors_after:
        print(f'---\nTask: {err["task_id"]}\nError: {err["error"]}\nCode:\n{err["code"]}\n')

# 可选：保存修复后的样本
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250730_164334_fixed.jsonl', 'w') as f:
    for sample in fixed_samples:
        f.write(json.dumps(sample, ensure_ascii=False) + '\n') 