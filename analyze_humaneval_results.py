#!/usr/bin/env python3
"""
Simple HumanEval Results Analyzer
"""

import json
import sys
import argparse
import subprocess
import tempfile
import os
from typing import Dict, List, Any

def extract_function_name(completion: str) -> str:
    """Extract function name from completion"""
    lines = completion.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('def '):
            # Extract function name from "def function_name(...):"
            func_name = line[4:].split('(')[0].strip()
            return func_name
    return "unknown"

def check_humaneval_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Check a single HumanEval sample"""
    task_id = sample['task_id']
    completion = sample['completion']
    test = sample['test']
    entry_point = sample['entry_point']
    
    # Extract function name from completion
    func_name = extract_function_name(completion)
    
    # Create test code - HumanEval completion is just the function body
    # We need to add the function signature from the prompt
    prompt = sample['prompt']
    
    # Extract function signature from prompt
    lines = prompt.split('\n')
    func_signature = None
    for line in lines:
        if line.strip().startswith('def '):
            func_signature = line.strip()
            break
    
    if func_signature:
        # HumanEval completion needs proper indentation for the first line
        lines = completion.split('\n')
        indented_lines = []
        for i, line in enumerate(lines):
            if i == 0 and line.strip():  # First non-empty line
                indented_lines.append('    ' + line)
            else:
                indented_lines.append(line)
        indented_completion = '\n'.join(indented_lines)
        
        # Add typing imports if needed
        typing_imports = ""
        if "List[" in func_signature or "Tuple[" in func_signature or "Optional[" in func_signature or "Any" in func_signature:
            typing_imports = "from typing import List, Tuple, Optional, Any\n\n"
        
        test_code = f"""
{typing_imports}{func_signature}
{indented_completion}

{test}
"""

    else:
        # Fallback: try to use entry_point
        test_code = f"""
def {entry_point}():
{completion}

{test}
"""
    
    # Execute test
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        # Run with timeout
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return {
                'task_id': task_id,
                'status': 'Pass',
                'error': None,
                'func_name': func_name,
                'entry_point': entry_point
            }
        else:
            return {
                'task_id': task_id,
                'status': 'Error',
                'error': result.stderr.strip(),
                'func_name': func_name,
                'entry_point': entry_point
            }
            
    except subprocess.TimeoutExpired:
        return {
            'task_id': task_id,
            'status': 'Timeout',
            'error': 'Execution timeout',
            'func_name': func_name,
            'entry_point': entry_point
        }
    except Exception as e:
        return {
            'task_id': task_id,
            'status': 'Exception',
            'error': str(e),
            'func_name': func_name,
            'entry_point': entry_point
        }

def analyze_humaneval_results(result_file: str):
    """Analyze HumanEval results"""
    print(f"Analyzing results: {result_file}")
    
    # Read samples
    samples = []
    with open(result_file, 'r') as f:
        for line in f:
            samples.append(json.loads(line.strip()))
    
    print(f"Total samples: {len(samples)}")
    
    # Check each sample
    results = []
    for i, sample in enumerate(samples):
        print(f"Checking sample {i+1}/{len(samples)}: {sample['task_id']}")
        result = check_humaneval_sample(sample)
        results.append(result)
    
    # Analyze results
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'Pass')
    failed = total - passed
    
    print(f"\n=== HumanEval Results Summary ===")
    print(f"Total samples: {total}")
    print(f"Passed: {passed} ({passed/total*100:.2f}%)")
    print(f"Failed: {failed}")
    
    # Error type distribution
    error_types = {}
    for result in results:
        status = result['status']
        error_types[status] = error_types.get(status, 0) + 1
    
    print(f"\nError type distribution:")
    for error_type, count in error_types.items():
        print(f"  {error_type}: {count} ({count/total*100:.1f}%)")
    
    # Show examples of failed cases
    failed_cases = [r for r in results if r['status'] != 'Pass']
    if failed_cases:
        print(f"\nExamples of failed cases:")
        for i, case in enumerate(failed_cases[:5]):  # Show first 5
            print(f"---")
            print(f"Task: {case['task_id']}")
            print(f"Error: {case['status']}")
            print(f"Message: {case['error']}")
            print(f"Function name: {case['func_name']}")
            print(f"Expected entry point: {case['entry_point']}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Analyze HumanEval results")
    parser.add_argument("--result_file", required=True, help="Result file path")
    
    args = parser.parse_args()
    analyze_humaneval_results(args.result_file)

if __name__ == "__main__":
    main() 