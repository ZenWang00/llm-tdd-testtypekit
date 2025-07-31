import json
import ast

samples = []
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250731_154121.jsonl', 'r') as f:
    for line in f:
        samples.append(json.loads(line.strip()))

syntax_errors = []
other_errors = []

for sample in samples:
    code = sample['completion']
    try:
        # 尝试将代码包装在函数体内做AST检查
        wrapped = f'def test_func():\n{code if code.endswith("\n") else code+chr(10)}'
        ast.parse(wrapped)
    except SyntaxError as e:
        syntax_errors.append({'task_id': sample['task_id'], 'error': str(e), 'code': code})
    except Exception as e:
        other_errors.append({'task_id': sample['task_id'], 'error': str(e), 'code': code})

print(f'Total samples: {len(samples)}')
print(f'Syntax errors: {len(syntax_errors)}')
print(f'Non-syntax errors: {len(other_errors)}')
print(f'Pass (no syntax error): {len(samples) - len(syntax_errors) - len(other_errors)}')

if syntax_errors:
    print('\nAll Syntax Errors:')
    for err in syntax_errors:
        print(f'---\nTask: {err["task_id"]}\nError: {err["error"]}\nCode:\n{err["code"]}\n')
if other_errors:
    print('\nAll Non-Syntax Errors:')
    for err in other_errors:
        print(f'---\nTask: {err["task_id"]}\nError: {err["error"]}\nCode:\n{err["code"]}\n') 