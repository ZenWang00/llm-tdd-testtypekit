#!/usr/bin/env python3
"""
综合TDD分析脚本

结合契约验证器和启发式检查器，提供全面的测试质量分析。
"""

import json
import argparse
from pathlib import Path
from test_contract_validator import TestContractValidator, ContractValidationResult
from test_heuristic_checker import TestHeuristicChecker, HeuristicAnalysisResult


def load_tdd_results(result_file: str) -> list:
    """加载TDD结果文件"""
    samples = []
    with open(result_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def extract_generated_tests(samples: list) -> tuple:
    """从样本中提取生成的测试代码"""
    test_codes = []
    valid_samples = []
    
    for sample in samples:
        if 'generated_tests' in sample and sample['generated_tests']:
            test_codes.append(sample['generated_tests'])
            valid_samples.append(sample)
        else:
            print(f"Sample {sample.get('task_id', 'unknown')} missing generated_tests")
    
    print(f"Found {len(test_codes)} samples with generated tests out of {len(samples)} total")
    return test_codes, valid_samples


def comprehensive_analysis(result_file: str, min_assertions: int = 3) -> None:
    """执行综合分析"""
    print(f"Comprehensive TDD Analysis from: {result_file}")
    print("=" * 80)
    
    # 加载结果
    samples = load_tdd_results(result_file)
    print(f"Loaded {len(samples)} samples")
    
    # 提取生成的测试
    test_codes, valid_samples = extract_generated_tests(samples)
    
    if not test_codes:
        print("No generated tests found to analyze")
        return
    
    # 初始化检查器
    contract_validator = TestContractValidator(min_assertions)
    heuristic_checker = TestHeuristicChecker()
    
    # 执行分析
    print(f"\nContract Validation Analysis...")
    contract_results = []
    for i, test_code in enumerate(test_codes):
        print(f"  Validating test {i+1}/{len(test_codes)}...")
        result = contract_validator.validate_test_code(test_code)
        contract_results.append(result)
    
    print(f"\nHeuristic Analysis...")
    heuristic_results = []
    for i, test_code in enumerate(test_codes):
        print(f"  Analyzing test {i+1}/{len(test_codes)}...")
        result = heuristic_checker.analyze_test_code(test_code)
        heuristic_results.append(result)
    
    # 打印结果摘要
    print_contract_summary(contract_results)
    print_heuristic_summary(heuristic_results)
    
    # 详细分析
    print_detailed_analysis(valid_samples, contract_results, heuristic_results)
    
    # 生成综合报告
    generate_comprehensive_report(valid_samples, contract_results, heuristic_results, result_file)
    
    # 相关性分析
    analyze_correlations(contract_results, heuristic_results)


def print_contract_summary(results: list) -> None:
    """打印契约验证摘要"""
    if not results:
        return
    
    total_tests = len(results)
    compliant_tests = sum(1 for r in results if r.is_compliant)
    avg_score = sum(r.score for r in results) / total_tests
    
    print("\n" + "="*60)
    print("CONTRACT VALIDATION SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Compliant Tests: {compliant_tests} ({compliant_tests/total_tests*100:.1f}%)")
    print(f"Average Score: {avg_score:.3f}")
    
    # 各项指标的统计
    metrics = {
        'Function Names': 'function_name_compliant',
        'Assertion Count': 'assertion_count_compliant', 
        'Boundary Tests': 'boundary_test_present',
        'Exception Tests': 'exception_test_present',
        'Pytest Format': 'pytest_format_compliant'
    }
    
    print("\nCompliance by Category:")
    print("-" * 40)
    for metric_name, attr_name in metrics.items():
        compliant_count = sum(1 for r in results if getattr(r, attr_name))
        percentage = compliant_count / total_tests * 100
        print(f"{metric_name:20} {compliant_count:3d}/{total_tests} ({percentage:5.1f}%)")


def print_heuristic_summary(results: list) -> None:
    """打印启发式分析摘要"""
    if not results:
        return
    
    total_tests = len(results)
    avg_overall_score = sum(r.overall_score for r in results) / total_tests
    
    print("\n" + "="*60)
    print("HEURISTIC ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Tests Analyzed: {total_tests}")
    print(f"Average Overall Score: {avg_overall_score:.3f}")
    
    # 各项指标的统计
    categories = [
        ('Exception Tests', 'exception_score'),
        ('Boundary Tests', 'boundary_score'),
        ('Input Diversity', 'diversity_score'),
        ('Test Patterns', 'pattern_score'),
        ('Code Quality', 'quality_score')
    ]
    
    print("\nAverage Scores by Category:")
    print("-" * 50)
    for category_name, attr_name in categories:
        avg_score = sum(getattr(r, attr_name) for r in results) / total_tests
        print(f"{category_name:20} {avg_score:.3f}")


def print_detailed_analysis(samples: list, contract_results: list, heuristic_results: list) -> None:
    """打印详细分析"""
    print(f"\nDETAILED ANALYSIS BY TASK")
    print("=" * 80)
    
    for i, (sample, contract_result, heuristic_result) in enumerate(zip(samples, contract_results, heuristic_results)):
        task_id = sample.get('task_id', f'Task_{i}')
        print(f"\nTask {task_id}:")
        
        # 契约验证结果
        print(f"  Contract Validation:")
        print(f"    Compliance: {contract_result.is_compliant}")
        print(f"    Score: {contract_result.score:.3f}")
        print(f"    Function Names: {'PASS' if contract_result.function_name_compliant else 'FAIL'}")
        print(f"    Assertions: {'PASS' if contract_result.assertion_count_compliant else 'FAIL'}")
        print(f"    Boundary Tests: {'PASS' if contract_result.boundary_test_present else 'FAIL'}")
        print(f"    Exception Tests: {'PASS' if contract_result.exception_test_present else 'FAIL'}")
        print(f"    Pytest Format: {'PASS' if contract_result.pytest_format_compliant else 'FAIL'}")
        
        # 启发式分析结果
        print(f"  Heuristic Analysis:")
        print(f"    Overall Score: {heuristic_result.overall_score:.3f}")
        print(f"    Exception Score: {heuristic_result.exception_score:.3f}")
        print(f"    Boundary Score: {heuristic_result.boundary_score:.3f}")
        print(f"    Diversity Score: {heuristic_result.diversity_score:.3f}")
        print(f"    Pattern Score: {heuristic_result.pattern_score:.3f}")
        print(f"    Quality Score: {heuristic_result.quality_score:.3f}")
        
        # 洞察
        if heuristic_result.insights:
            print(f"    Insights: {', '.join(heuristic_result.insights)}")


def generate_comprehensive_report(samples: list, contract_results: list, heuristic_results: list, result_file: str) -> None:
    """生成综合报告"""
    print(f"\nGENERATING COMPREHENSIVE REPORT")
    print("=" * 80)
    
    # 计算统计信息
    total_tests = len(contract_results)
    
    # 契约验证统计
    compliant_tests = sum(1 for r in contract_results if r.is_compliant)
    avg_contract_score = sum(r.score for r in contract_results) / total_tests
    
    # 启发式分析统计
    avg_heuristic_score = sum(r.overall_score for r in heuristic_results) / total_tests
    
    # 生成报告文件名
    report_file = result_file.replace('.jsonl', '_comprehensive_report.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("COMPREHENSIVE TDD TEST QUALITY ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Source File: {result_file}\n")
        f.write(f"Analysis Date: {__import__('datetime').datetime.now().isoformat()}\n\n")
        
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Tests Analyzed: {total_tests}\n")
        f.write(f"Contract Compliance Rate: {compliant_tests/total_tests*100:.1f}%\n")
        f.write(f"Average Contract Score: {avg_contract_score:.3f}\n")
        f.write(f"Average Heuristic Score: {avg_heuristic_score:.3f}\n\n")
        
        # 契约验证详细统计
        f.write("CONTRACT VALIDATION DETAILS\n")
        f.write("-" * 40 + "\n")
        metrics = {
            'Function Names': 'function_name_compliant',
            'Assertion Count': 'assertion_count_compliant', 
            'Boundary Tests': 'boundary_test_present',
            'Exception Tests': 'exception_test_present',
            'Pytest Format': 'pytest_format_compliant'
        }
        
        for metric_name, attr_name in metrics.items():
            compliant_count = sum(1 for r in contract_results if getattr(r, attr_name))
            percentage = compliant_count / total_tests * 100
            f.write(f"{metric_name:20} {compliant_count:3d}/{total_tests} ({percentage:5.1f}%)\n")
        
        f.write("\n")
        
        # 启发式分析详细统计
        f.write("HEURISTIC ANALYSIS DETAILS\n")
        f.write("-" * 40 + "\n")
        categories = [
            ('Exception Tests', 'exception_score'),
            ('Boundary Tests', 'boundary_score'),
            ('Input Diversity', 'diversity_score'),
            ('Test Patterns', 'pattern_score'),
            ('Code Quality', 'quality_score')
        ]
        
        for category_name, attr_name in categories:
            avg_score = sum(getattr(r, attr_name) for r in heuristic_results) / total_tests
            f.write(f"{category_name:20} {avg_score:.3f}\n")
        
        f.write("\n")
        
        # 详细任务分析
        f.write("DETAILED TASK ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        for i, (sample, contract_result, heuristic_result) in enumerate(zip(samples, contract_results, heuristic_results)):
            task_id = sample.get('task_id', f'Task_{i}')
            f.write(f"\nTask {task_id}:\n")
            f.write(f"  Contract Score: {contract_result.score:.3f}\n")
            f.write(f"  Heuristic Score: {heuristic_result.overall_score:.3f}\n")
            f.write(f"  Compliance: {contract_result.is_compliant}\n")
            
            if heuristic_result.insights:
                f.write(f"  Insights: {', '.join(heuristic_result.insights)}\n")
    
    print(f"Comprehensive report saved to: {report_file}")


def analyze_correlations(contract_results: list, heuristic_results: list) -> None:
    """分析契约验证和启发式分析的相关性"""
    print(f"\nCORRELATION ANALYSIS")
    print("=" * 80)
    
    if len(contract_results) != len(heuristic_results):
        print("Cannot analyze correlations: result counts don't match")
        return
    
    # 计算相关性
    contract_scores = [r.score for r in contract_results]
    heuristic_scores = [r.overall_score for r in heuristic_results]
    
    # 简单的相关性计算
    n = len(contract_scores)
    if n > 1:
        mean_contract = sum(contract_scores) / n
        mean_heuristic = sum(heuristic_scores) / n
        
        numerator = sum((c - mean_contract) * (h - mean_heuristic) for c, h in zip(contract_scores, heuristic_scores))
        denominator_contract = sum((c - mean_contract) ** 2 for c in contract_scores)
        denominator_heuristic = sum((h - mean_heuristic) ** 2 for h in heuristic_scores)
        
        if denominator_contract > 0 and denominator_heuristic > 0:
            correlation = numerator / (denominator_contract ** 0.5 * denominator_heuristic ** 0.5)
            print(f"Correlation between Contract and Heuristic scores: {correlation:.3f}")
            
            if correlation > 0.7:
                print("Strong positive correlation - both methods agree well")
            elif correlation > 0.3:
                print("Moderate positive correlation - some agreement")
            elif correlation > -0.3:
                print("Weak correlation - methods provide different perspectives")
            else:
                print("Negative correlation - methods disagree")
        else:
            print("Cannot calculate correlation: insufficient variance")
    else:
        print("Cannot calculate correlation: need at least 2 samples")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Comprehensive TDD test quality analysis")
    parser.add_argument("result_file", help="TDD result file to analyze")
    parser.add_argument("--min_assertions", type=int, default=3, 
                       help="Minimum number of assertions required (default: 3)")
    
    args = parser.parse_args()
    
    if not Path(args.result_file).exists():
        print(f"❌ Error: File {args.result_file} not found")
        return
    
    try:
        comprehensive_analysis(args.result_file, args.min_assertions)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
