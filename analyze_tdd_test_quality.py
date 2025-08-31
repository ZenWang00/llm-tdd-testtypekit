#!/usr/bin/env python3
"""
分析TDD生成的测试质量

这个脚本使用契约验证器来分析TDD管道生成的测试代码质量。
"""

import json
import argparse
from pathlib import Path
from test_contract_validator import TestContractValidator, validate_multiple_tests, print_validation_summary


def load_tdd_results(result_file: str) -> list:
    """加载TDD结果文件"""
    samples = []
    with open(result_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def extract_generated_tests(samples: list) -> list:
    """从样本中提取生成的测试代码"""
    test_codes = []
    valid_samples = []
    
    for sample in samples:
        if 'generated_tests' in sample and sample['generated_tests']:
            test_codes.append(sample['generated_tests'])
            valid_samples.append(sample)
        else:
            print(f"⚠️  Sample {sample.get('task_id', 'unknown')} missing generated_tests")
    
    print(f"📊 Found {len(test_codes)} samples with generated tests out of {len(samples)} total")
    return test_codes, valid_samples


def analyze_tdd_test_quality(result_file: str, min_assertions: int = 3) -> None:
    """分析TDD测试质量"""
    print(f"🔍 Analyzing TDD test quality from: {result_file}")
    print("=" * 60)
    
    # 加载结果
    samples = load_tdd_results(result_file)
    print(f"📁 Loaded {len(samples)} samples")
    
    # 提取生成的测试
    test_codes, valid_samples = extract_generated_tests(samples)
    
    if not test_codes:
        print("❌ No generated tests found to analyze")
        return
    
    # 验证测试质量
    print(f"\n🔍 Validating {len(test_codes)} generated tests...")
    validation_results = validate_multiple_tests(test_codes, min_assertions)
    
    # 打印验证摘要
    print_validation_summary(validation_results)
    
    # 详细分析每个样本
    print(f"\n📋 Detailed Analysis by Task:")
    print("-" * 60)
    
    for i, (sample, result) in enumerate(zip(valid_samples, validation_results)):
        task_id = sample.get('task_id', f'Task_{i}')
        print(f"\nTask {task_id}:")
        print(f"  ✅ Compliance: {result.is_compliant}")
        print(f"  📊 Score: {result.score:.2f}")
        print(f"  🧪 Function Names: {'✅' if result.function_name_compliant else '❌'}")
        print(f"  📝 Assertions: {'✅' if result.assertion_count_compliant else '❌'}")
        print(f"  🎯 Boundary Tests: {'✅' if result.boundary_test_present else '❌'}")
        print(f"  ⚠️  Exception Tests: {'✅' if result.exception_test_present else '❌'}")
        print(f"  🐍 Pytest Format: {'✅' if result.pytest_format_compliant else '❌'}")
        
        # 显示详细信息
        if result.details:
            if 'function_names' in result.details:
                print(f"  📛 Functions: {', '.join(result.details['function_names'])}")
            if 'assertion_count' in result.details:
                print(f"  📊 Assertions: {result.details['assertion_count']}")
            if 'boundary_test_details' in result.details:
                boundary_info = result.details['boundary_test_details']
                if boundary_info['has_boundary_tests']:
                    print(f"  🎯 Boundary Types: {', '.join(boundary_info['boundary_types'])}")
            if 'exception_test_details' in result.details:
                exception_info = result.details['exception_test_details']
                if exception_info['has_exception_tests']:
                    print(f"  ⚠️  Exception Types: {', '.join(exception_info['exception_types'])}")
    
    # 生成质量报告
    generate_quality_report(valid_samples, validation_results, result_file)


def generate_quality_report(samples: list, results: list, result_file: str) -> None:
    """生成质量报告"""
    print(f"\n📊 GENERATING QUALITY REPORT")
    print("=" * 60)
    
    # 计算统计信息
    total_tests = len(results)
    compliant_tests = sum(1 for r in results if r.is_compliant)
    avg_score = sum(r.score for r in results) / total_tests if results else 0
    
    # 各项指标的统计
    metrics = {
        'Function Names': 'function_name_compliant',
        'Assertion Count': 'assertion_count_compliant', 
        'Boundary Tests': 'boundary_test_present',
        'Exception Tests': 'exception_test_present',
        'Pytest Format': 'pytest_format_compliant'
    }
    
    metric_stats = {}
    for metric_name, attr_name in metrics.items():
        compliant_count = sum(1 for r in results if getattr(r, attr_name))
        percentage = compliant_count / total_tests * 100 if total_tests > 0 else 0
        metric_stats[metric_name] = {
            'compliant': compliant_count,
            'total': total_tests,
            'percentage': percentage
        }
    
    # 生成报告文件名
    report_file = result_file.replace('.jsonl', '_quality_report.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("TDD TEST QUALITY ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Source File: {result_file}\n")
        f.write(f"Analysis Date: {__import__('datetime').datetime.now().isoformat()}\n\n")
        
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Tests Analyzed: {total_tests}\n")
        f.write(f"Compliant Tests: {compliant_tests} ({compliant_tests/total_tests*100:.1f}%)\n")
        f.write(f"Average Quality Score: {avg_score:.2f}\n\n")
        
        f.write("COMPLIANCE BY CATEGORY\n")
        f.write("-" * 30 + "\n")
        for metric_name, stats in metric_stats.items():
            f.write(f"{metric_name:20} {stats['compliant']:3d}/{stats['total']} ({stats['percentage']:5.1f}%)\n")
        
        f.write("\nDETAILED ANALYSIS\n")
        f.write("-" * 30 + "\n")
        
        for i, (sample, result) in enumerate(zip(samples, results)):
            task_id = sample.get('task_id', f'Task_{i}')
            f.write(f"\nTask {task_id}:\n")
            f.write(f"  Compliance: {result.is_compliant}\n")
            f.write(f"  Score: {result.score:.2f}\n")
            f.write(f"  Function Names: {'✅' if result.function_name_compliant else '❌'}\n")
            f.write(f"  Assertions: {'✅' if result.assertion_count_compliant else '❌'}\n")
            f.write(f"  Boundary Tests: {'✅' if result.boundary_test_present else '❌'}\n")
            f.write(f"  Exception Tests: {'✅' if result.exception_test_present else '❌'}\n")
            f.write(f"  Pytest Format: {'✅' if result.pytest_format_compliant else '❌'}\n")
            
            if result.details:
                if 'function_names' in result.details:
                    f.write(f"  Functions: {', '.join(result.details['function_names'])}\n")
                if 'assertion_count' in result.details:
                    f.write(f"  Assertions: {result.details['assertion_count']}\n")
    
    print(f"📄 Quality report saved to: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Analyze TDD test quality")
    parser.add_argument("result_file", help="TDD result file to analyze")
    parser.add_argument("--min_assertions", type=int, default=3, 
                       help="Minimum number of assertions required (default: 3)")
    
    args = parser.parse_args()
    
    if not Path(args.result_file).exists():
        print(f"❌ Error: File {args.result_file} not found")
        return
    
    try:
        analyze_tdd_test_quality(args.result_file, args.min_assertions)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
