import json
import sys
sys.path.append('benchmarks/humaneval')
from human_eval.execution import check_correctness
from human_eval.data import read_problems

problems = read_problems('benchmarks/humaneval/data/HumanEval.jsonl')
samples = []
with open('benchmarks/humaneval/data/langchain_batch_164_tasks_gpt_4o_mini_20250731_122842.jsonl', 'r') as f:
    for line in f:
        samples.append(json.loads(line.strip()))

fail_types = {}
fail_examples = {}

for sample in samples:
    result = check_correctness(problems[sample['task_id']], sample['completion'], timeout=3.0)
    if not result['passed']:
        err = result.get('error', 'UnknownError')
        fail_types[err] = fail_types.get(err, 0) + 1
        if err not in fail_examples:
            fail_examples[err] = {
                'task_id': sample['task_id'],
                'error': err,
                'code': sample['completion']
            }

print('Failure Type Distribution:')
for k, v in fail_types.items():
    print(f'{k}: {v}')

print('\nRepresentative Failure Examples:')
for k, v in fail_examples.items():
    print(f'---\nTask: {v["task_id"]}\nError: {v["error"]}\nCode:\n{v["code"]}\n') 