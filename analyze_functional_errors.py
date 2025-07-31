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
passed_count = 0

for i, sample in enumerate(samples):
    print(f"Processing {i+1}/{len(samples)}: {sample['task_id']}")
    try:
        result = check_correctness(problems[sample['task_id']], sample['completion'], timeout=3.0)
        if result['passed']:
            passed_count += 1
        else:
            err = result.get('error', 'UnknownError')
            fail_types[err] = fail_types.get(err, 0) + 1
            if err not in fail_examples:
                fail_examples[err] = {
                    'task_id': sample['task_id'],
                    'error': err,
                    'code': sample['completion']
                }
    except Exception as e:
        print(f"Error processing {sample['task_id']}: {e}")
        err = f"ProcessingError: {str(e)}"
        fail_types[err] = fail_types.get(err, 0) + 1

print(f'\nFinal Summary: {passed_count}/{len(samples)} passed ({passed_count/len(samples)*100:.2f}%)')

print('\nFailure Type Distribution:')
for k, v in sorted(fail_types.items(), key=lambda x: x[1], reverse=True):
    print(f'{k}: {v}')

print('\nRepresentative Failure Examples:')
for k, v in fail_examples.items():
    print(f'---\nTask: {v["task_id"]}\nError: {v["error"]}\nCode:\n{v["code"]}\n') 