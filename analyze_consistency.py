#!/usr/bin/env python3
"""
一致性分析脚本

分析多次生成的测试结果，计算Jaccard相似性和其他一致性指标。
"""

import json
import re
import ast
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import argparse


def extract_test_inputs(test_code: str) -> Set[str]:
    """从测试代码中提取输入值"""
    inputs = set()
    
    try:
        # 解析AST
        tree = ast.parse(test_code)
        
        # 查找所有字符串字面量、数字字面量等
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    # 清理字符串，移除引号
                    clean_str = node.value.strip("'\"")
                    if clean_str and len(clean_str) < 100:  # 避免过长的字符串
                        inputs.add(f"str:{clean_str}")
                elif isinstance(node.value, (int, float)):
                    inputs.add(f"num:{node.value}")
            elif isinstance(node, ast.List):
                # 列表字面量
                list_str = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                inputs.add(f"list:{list_str}")
            elif isinstance(node, ast.Dict):
                # 字典字面量
                dict_str = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                inputs.add(f"dict:{dict_str}")
        
        # 使用正则表达式查找更多模式
        # 查找函数调用中的参数
        func_calls = re.findall(r'\w+\(([^)]*)\)', test_code)
        for call_args in func_calls:
            args = call_args.split(',')
            for arg in args:
                arg = arg.strip()
                if arg and len(arg) < 50:
                    inputs.add(f"arg:{arg}")
        
        # 查找assert语句中的值
        assert_patterns = re.findall(r'assert\s+\w+([^,)]*)', test_code)
        for pattern in assert_patterns:
            if pattern and len(pattern) < 50:
                inputs.add(f"assert:{pattern}")
                
    except Exception as e:
        # 如果AST解析失败，使用正则表达式
        # 提取数字
        numbers = re.findall(r'\b\d+\.?\d*\b', test_code)
        for num in numbers:
            inputs.add(f"num:{num}")
        
        # 提取字符串
        strings = re.findall(r'["\']([^"\']*)["\']', test_code)
        for s in strings:
            if s and len(s) < 100:
                inputs.add(f"str:{s}")
        
        # 提取函数调用
        func_calls = re.findall(r'\w+\(([^)]*)\)', test_code)
        for call_args in func_calls:
            args = call_args.split(',')
            for arg in args:
                arg = arg.strip()
                if arg and len(arg) < 50:
                    inputs.add(f"arg:{arg}")
    
    return inputs


def calculate_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """计算两个集合的Jaccard相似性"""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def analyze_test_structure(test_code: str) -> Dict[str, any]:
    """分析测试代码的结构"""
    structure = {
        'num_test_functions': 0,
        'num_asserts': 0,
        'num_pytest_raises': 0,
        'test_function_names': [],
        'has_edge_cases': False,
        'has_exception_tests': False
    }
    
    try:
        tree = ast.parse(test_code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    structure['num_test_functions'] += 1
                    structure['test_function_names'].append(node.name)
        
        # 统计assert和pytest.raises
        code_str = test_code.lower()
        structure['num_asserts'] = code_str.count('assert')
        structure['num_pytest_raises'] = code_str.count('pytest.raises')
        
        # 检查边界情况
        edge_patterns = ['empty', 'zero', 'negative', 'max', 'min', 'boundary']
        structure['has_edge_cases'] = any(pattern in code_str for pattern in edge_patterns)
        
        # 检查异常测试
        exception_patterns = ['raises', 'error', 'exception', 'invalid']
        structure['has_exception_tests'] = any(pattern in code_str for pattern in exception_patterns)
        
    except Exception as e:
        # 如果AST解析失败，使用正则表达式
        code_str = test_code.lower()
        structure['num_asserts'] = code_str.count('assert')
        structure['num_pytest_raises'] = code_str.count('pytest.raises')
        
        # 统计test_函数
        test_functions = re.findall(r'def\s+(test_\w+)', test_code)
        structure['num_test_functions'] = len(test_functions)
        structure['test_function_names'] = test_functions
        
        # 检查边界和异常
        edge_patterns = ['empty', 'zero', 'negative', 'max', 'min', 'boundary']
        structure['has_edge_cases'] = any(pattern in code_str for pattern in edge_patterns)
        
        exception_patterns = ['raises', 'error', 'exception', 'invalid']
        structure['has_exception_tests'] = any(pattern in code_str for pattern in exception_patterns)
    
    return structure


def analyze_consistency(consistency_file: str) -> Dict[str, any]:
    """分析一致性检查结果"""
    print(f"Analyzing consistency from: {consistency_file}")
    print("=" * 60)
    
    # 加载数据
    samples = []
    with open(consistency_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    
    print(f"Loaded {len(samples)} samples")
    
    # 按任务分组
    tasks = defaultdict(list)
    for sample in samples:
        task_id = sample['task_id']
        tasks[task_id].append(sample)
    
    print(f"Found {len(tasks)} unique tasks")
    
    # 分析每个任务的一致性
    task_consistency = {}
    
    for task_id, task_samples in tasks.items():
        print(f"\nAnalyzing task: {task_id}")
        print("-" * 40)
        
        if len(task_samples) < 2:
            print(f"  Only {len(task_samples)} sample(s), skipping consistency analysis")
            continue
        
        # 提取测试输入
        test_inputs = []
        test_structures = []
        
        for sample in task_samples:
            if 'generated_tests' in sample and sample['generated_tests']:
                inputs = extract_test_inputs(sample['generated_tests'])
                test_inputs.append(inputs)
                
                structure = analyze_test_structure(sample['generated_tests'])
                test_structures.append(structure)
                
                print(f"  Run {sample.get('run_id', 'N/A')}: {len(inputs)} inputs, {structure['num_test_functions']} test functions")
            else:
                print(f"  Run {sample.get('run_id', 'N/A')}: No tests generated")
        
        if len(test_inputs) < 2:
            print(f"  Not enough valid test samples for consistency analysis")
            continue
        
        # 计算Jaccard相似性
        jaccard_scores = []
        for i in range(len(test_inputs)):
            for j in range(i + 1, len(test_inputs)):
                similarity = calculate_jaccard_similarity(test_inputs[i], test_inputs[j])
                jaccard_scores.append(similarity)
                print(f"  Jaccard similarity between run {i} and {j}: {similarity:.3f}")
        
        # 计算结构相似性
        structure_similarity = {
            'num_test_functions': len(set(s['num_test_functions'] for s in test_structures)),
            'num_asserts': len(set(s['num_asserts'] for s in test_structures)),
            'num_pytest_raises': len(set(s['num_pytest_raises'] for s in test_structures)),
            'has_edge_cases': len(set(s['has_edge_cases'] for s in test_structures)),
            'has_exception_tests': len(set(s['has_exception_tests'] for s in test_structures))
        }
        
        # 计算结构一致性分数
        structure_score = sum(structure_similarity.values()) / len(structure_similarity)
        structure_consistency = 1.0 - (structure_score / len(structure_similarity))
        
        print(f"  Structure consistency: {structure_consistency:.3f}")
        
        # 保存任务一致性结果
        task_consistency[task_id] = {
            'num_runs': len(task_samples),
            'valid_runs': len(test_inputs),
            'jaccard_scores': jaccard_scores,
            'avg_jaccard': sum(jaccard_scores) / len(jaccard_scores) if jaccard_scores else 0.0,
            'structure_consistency': structure_consistency,
            'structure_details': structure_similarity
        }
    
    # 计算总体一致性指标
    if task_consistency:
        all_jaccard_scores = []
        all_structure_scores = []
        
        for task_data in task_consistency.values():
            all_jaccard_scores.extend(task_data['jaccard_scores'])
            all_structure_scores.append(task_data['structure_consistency'])
        
        overall_metrics = {
            'total_tasks': len(tasks),
            'analyzed_tasks': len(task_consistency),
            'avg_jaccard_similarity': sum(all_jaccard_scores) / len(all_jaccard_scores) if all_jaccard_scores else 0.0,
            'avg_structure_consistency': sum(all_structure_scores) / len(all_structure_scores) if all_structure_scores else 0.0,
            'task_consistency': task_consistency
        }
        
        print("\n" + "=" * 60)
        print("OVERALL CONSISTENCY METRICS")
        print("=" * 60)
        print(f"Total tasks: {overall_metrics['total_tasks']}")
        print(f"Analyzed tasks: {overall_metrics['analyzed_tasks']}")
        print(f"Average Jaccard similarity: {overall_metrics['avg_jaccard_similarity']:.3f}")
        print(f"Average structure consistency: {overall_metrics['avg_structure_consistency']:.3f}")
        
        return overall_metrics
    else:
        print("\nNo valid tasks found for consistency analysis")
        return {}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Analyze consistency of generated tests")
    parser.add_argument("consistency_file", help="Consistency check result file")
    
    args = parser.parse_args()
    
    try:
        results = analyze_consistency(args.consistency_file)
        
        if results:
            # 保存分析结果
            output_file = args.consistency_file.replace('.jsonl', '_analysis.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nAnalysis results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing consistency: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
