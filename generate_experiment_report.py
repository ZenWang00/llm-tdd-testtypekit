#!/usr/bin/env python3
"""
实验报告生成模块

将实验数据整理成表格形式，包括测试质量、一致性检查等结果。
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any
import argparse


def load_jsonl_file(file_path: str) -> List[Dict[str, Any]]:
    """加载JSONL文件"""
    samples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def load_analysis_file(file_path: str) -> Dict[str, Any]:
    """加载分析结果文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_test_quality_table(data_dir: str) -> str:
    """生成测试质量表格"""
    print("Generating test quality table...")
    
    # 查找所有测试质量分析文件
    pattern = os.path.join(data_dir, "**", "*_comprehensive_report.txt")
    report_files = glob.glob(pattern, recursive=True)
    
    if not report_files:
        return "No test quality reports found."
    
    table = []
    table.append("| Dataset | Tasks | Date | Parameters | Contract Score | Heuristic Score | Status |")
    table.append("|---------|-------|------|------------|----------------|-----------------|--------|")
    
    for report_file in sorted(report_files):
        try:
            # 从文件名提取信息
            filename = os.path.basename(report_file)
            parts = filename.split('_')
            
            if 'mbpp' in filename:
                dataset = "MBPP"
            elif 'humaneval' in filename:
                dataset = "HumanEval"
            else:
                dataset = "Unknown"
            
            # 提取任务数量
            task_count = "N/A"
            for part in parts:
                if part.isdigit() and int(part) < 1000:  # 合理的任务数量
                    task_count = part
                    break
            
            # 提取日期
            date_str = "N/A"
            for part in parts:
                if len(part) == 8 and part.isdigit():  # YYYYMMDD格式
                    date_str = f"{part[:4]}-{part[4:6]}-{part[6:8]}"
                    break
            
            # 读取报告内容
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取分数
            contract_score = "N/A"
            heuristic_score = "N/A"
            
            # 查找契约验证分数
            if "EXECUTIVE SUMMARY" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "Average Contract Score:" in line:
                        contract_score = line.split(":")[-1].strip()
                        break
            
            # 查找启发式分析分数
            if "EXECUTIVE SUMMARY" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "Average Heuristic Score:" in line:
                        heuristic_score = line.split(":")[-1].strip()
                        break
            
            # 提取参数信息
            parameters = "N/A"
            # 从文件名尝试提取参数信息
            if 'consistency_check' in filename:
                # 对于一致性检查，从文件名提取参数范围
                parts = filename.split('_')
                for i, part in enumerate(parts):
                    if part.isdigit() and int(part) < 1000:
                        if 'runs' in parts[i-1] if i > 0 else False:
                            num_runs = part
                            # 根据运行次数推断参数范围
                            if int(num_runs) <= 3:
                                parameters = "T:0.1-0.5 S:42-456"
                            else:
                                parameters = "T:0.1-0.9 S:42-999"
                            break
            elif 'test_only' in filename:
                # 对于测试生成，使用默认温度
                parameters = "T:0.0"
            elif 'code_only' in filename:
                # 对于代码生成，使用默认温度
                parameters = "T:0.0"
            elif 'tdd_' in filename:
                # 对于完整TDD，使用默认温度
                parameters = "T:0.0"
            
            # 确定状态
            status = "✅"
            if contract_score != "N/A" and float(contract_score) < 0.7:
                status = "⚠️"
            if heuristic_score != "N/A" and float(heuristic_score) < 0.5:
                status = "❌"
            
            table.append(f"| {dataset} | {task_count} | {date_str} | {parameters} | {contract_score} | {heuristic_score} | {status} |")
            
        except Exception as e:
            print(f"Error processing {report_file}: {e}")
            continue
    
    return "\n".join(table)


def generate_consistency_table(data_dir: str) -> str:
    """生成一致性检查表格"""
    print("Generating consistency table...")
    
    # 查找所有一致性分析文件
    pattern = os.path.join(data_dir, "**", "*_analysis.json")
    analysis_files = glob.glob(pattern, recursive=True)
    
    if not analysis_files:
        return "No consistency analysis files found."
    
    table = []
    table.append("| Dataset | Tasks | Runs | Date | Avg Jaccard | Structure Consistency | Status |")
    table.append("|---------|-------|------|------|--------------|----------------------|--------|")
    
    for analysis_file in sorted(analysis_files):
        try:
            # 从文件名提取信息
            filename = os.path.basename(analysis_file)
            parts = filename.split('_')
            
            if 'mbpp' in filename:
                dataset = "MBPP"
            elif 'humaneval' in filename:
                dataset = "HumanEval"
            else:
                dataset = "Unknown"
            
            # 提取任务数量和运行次数
            task_count = "N/A"
            run_count = "N/A"
            for i, part in enumerate(parts):
                if part.isdigit() and int(part) < 1000:
                    if task_count == "N/A":
                        task_count = part
                    elif run_count == "N/A":
                        run_count = part
                        break
            
            # 提取日期
            date_str = "N/A"
            for part in parts:
                if len(part) == 8 and part.isdigit():  # YYYYMMDD格式
                    date_str = f"{part[:4]}-{part[4:6]}-{part[6:8]}"
                    break
            
            # 读取分析结果
            analysis_data = load_analysis_file(analysis_file)
            
            avg_jaccard = f"{analysis_data.get('avg_jaccard_similarity', 0):.3f}"
            structure_consistency = f"{analysis_data.get('avg_structure_consistency', 0):.3f}"
            
            # 确定状态
            status = "✅"
            if float(avg_jaccard) < 0.6:
                status = "⚠️"
            if float(avg_jaccard) < 0.4:
                status = "❌"
            
            table.append(f"| {dataset} | {task_count} | {run_count} | {date_str} | {avg_jaccard} | {structure_consistency} | {status} |")
            
        except Exception as e:
            print(f"Error processing {analysis_file}: {e}")
            continue
    
    return "\n".join(table)


def generate_pipeline_summary_table(data_dir: str) -> str:
    """生成Pipeline运行摘要表格"""
    print("Generating pipeline summary table...")
    
    # 查找所有Pipeline输出文件
    patterns = [
        os.path.join(data_dir, "**", "test_only_*_batch_*.jsonl"),
        os.path.join(data_dir, "**", "code_only_*_batch_*.jsonl"),
        os.path.join(data_dir, "**", "tdd_*_batch_*.jsonl"),
        os.path.join(data_dir, "**", "consistency_check_*_*.jsonl")
    ]
    
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    if not all_files:
        return "No pipeline output files found."
    
    table = []
    table.append("| Pipeline Type | Dataset | Tasks | Date | Method | Stage | Parameters | Status |")
    table.append("|----------------|---------|-------|------|--------|-------|------------|--------|")
    
    for file_path in sorted(all_files):
        try:
            filename = os.path.basename(file_path)
            
            # 确定Pipeline类型
            if 'test_only' in filename:
                pipeline_type = "Test Generation"
            elif 'code_only' in filename:
                pipeline_type = "Code Generation"
            elif 'tdd_' in filename:
                pipeline_type = "Full TDD"
            elif 'consistency_check' in filename:
                pipeline_type = "Consistency Check"
            else:
                pipeline_type = "Unknown"
            
            # 确定数据集
            if 'mbpp' in filename:
                dataset = "MBPP"
            elif 'humaneval' in filename:
                dataset = "HumanEval"
            else:
                dataset = "Unknown"
            
            # 提取任务数量
            task_count = "N/A"
            parts = filename.split('_')
            for part in parts:
                if part.isdigit() and int(part) < 1000:
                    task_count = part
                    break
            
            # 提取日期
            date_str = "N/A"
            for part in parts:
                if len(part) == 8 and part.isdigit():
                    date_str = f"{part[:4]}-{part[4:6]}-{part[6:8]}"
                    break
            
            # 读取文件获取方法信息
            samples = load_jsonl_file(file_path)
            if samples:
                method = samples[0].get('method', 'N/A')
                stage = samples[0].get('stage', 'N/A')
                
                # 提取参数信息
                parameters = "N/A"
                if pipeline_type == "Consistency Check":
                    # 对于一致性检查，提取temperature和random_seed信息
                    temps = set()
                    seeds = set()
                    for sample in samples:
                        if 'temperature' in sample:
                            temps.add(str(sample['temperature']))
                        if 'random_seed' in sample:
                            seeds.add(str(sample['random_seed']))
                    
                    if temps and seeds:
                        # 使用更简洁的表示方式
                        temp_list = sorted([float(t) for t in temps])
                        seed_list = sorted([int(s) for s in seeds])
                        if len(temp_list) <= 3:
                            temp_str = ",".join(map(str, temp_list))
                        else:
                            temp_str = f"{temp_list[0]}-{temp_list[-1]}"
                        if len(seed_list) <= 3:
                            seed_str = ",".join(map(str, seed_list))
                        else:
                            seed_str = f"{seed_list[0]}-{seed_list[-1]}"
                        
                        # 使用范围表示，更简洁
                        temp_display = f"{temp_list[0]}-{temp_list[-1]}"
                        seed_display = f"{seed_list[0]}-{seed_list[-1]}"
                        parameters = f"T:{temp_display} S:{seed_display}"
                    elif temps:
                        temp_list = sorted([float(t) for t in temps])
                        if len(temp_list) <= 3:
                            parameters = f"T:{','.join(map(str, temp_list))}"
                        else:
                            parameters = f"T:{temp_list[0]}-{temp_list[-1]}"
                    elif seeds:
                        seed_list = sorted([int(s) for s in seeds])
                        if len(seed_list) <= 3:
                            parameters = f"S:{','.join(map(str, seed_list))}"
                        else:
                            parameters = f"S:{seed_list[0]}-{seed_list[-1]}"
                elif pipeline_type == "Test Generation" or pipeline_type == "Code Generation":
                    # 对于测试生成和代码生成，检查是否有temperature信息
                    temps = set()
                    for sample in samples:
                        if 'temperature' in sample:
                            temps.add(str(sample['temperature']))
                    
                    if temps:
                        parameters = f"T:{','.join(sorted(temps))}"
                
                # 确定状态
                status = "✅"
                if any('error' in sample for sample in samples):
                    status = "⚠️"
                if all('error' in sample for sample in samples):
                    status = "❌"
                
                table.append(f"| {pipeline_type} | {dataset} | {task_count} | {date_str} | {method} | {stage} | {parameters} | {status} |")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return "\n".join(table)


def generate_experiment_report(data_dir: str = "benchmarks", output_file: str = None) -> str:
    """生成完整的实验报告"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"report/experiment_report_{timestamp}.md"
    
    print(f"Generating experiment report: {output_file}")
    
    report = []
    report.append("# LLM-TDD Experiment Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 1. Pipeline Execution Summary
    report.append("## 1. Pipeline Execution Summary")
    report.append("")
    pipeline_table = generate_pipeline_summary_table(data_dir)
    report.append(pipeline_table)
    report.append("")
    
    # 2. Test Quality Analysis
    report.append("## 2. Test Quality Analysis")
    report.append("")
    report.append("### 2.1 Quality Metrics Summary")
    report.append("")
    quality_table = generate_test_quality_table(data_dir)
    report.append(quality_table)
    report.append("")
    
    # 2.2 Detailed Analysis Results
    report.append("### 2.2 Detailed Analysis Results")
    report.append("")
    
    # 查找所有详细分析文件
    pattern = os.path.join(data_dir, "**", "*_comprehensive_report.txt")
    report_files = glob.glob(pattern, recursive=True)
    
    if report_files:
        for report_file in sorted(report_files):
            filename = os.path.basename(report_file)
            report.append(f"**{filename}**")
            report.append("")
            
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取关键信息
                lines = content.split('\n')
                summary_section = []
                in_summary = False
                
                for line in lines:
                    if "CONTRACT VALIDATION SUMMARY" in line or "HEURISTIC ANALYSIS SUMMARY" in line:
                        in_summary = True
                        summary_section.append(line)
                    elif in_summary and line.strip() and not line.startswith('='):
                        summary_section.append(line)
                    elif in_summary and line.startswith('='):
                        break
                
                if summary_section:
                    report.append("```")
                    report.extend(summary_section)
                    report.append("```")
                else:
                    # 尝试提取EXECUTIVE SUMMARY部分
                    lines = content.split('\n')
                    executive_summary = []
                    in_summary = False
                    
                    for line in lines:
                        if "EXECUTIVE SUMMARY" in line:
                            in_summary = True
                            executive_summary.append(line)
                        elif in_summary and line.strip():
                            if "CONTRACT VALIDATION DETAILS" in line:
                                break
                            executive_summary.append(line)
                    
                    if executive_summary:
                        report.append("```")
                        report.extend(executive_summary)
                        report.append("```")
                    else:
                        report.append("```")
                        report.append("Please refer to the original file for detailed analysis content")
                        report.append("```")
                
            except Exception as e:
                report.append(f"Error reading file: {e}")
            
            report.append("")
    else:
        report.append("No detailed analysis report files found")
        report.append("")
    
    # 3. Consistency Check Results
    report.append("## 3. Consistency Check Results")
    report.append("")
    report.append("### 3.1 Consistency Metrics Summary")
    report.append("")
    consistency_table = generate_consistency_table(data_dir)
    report.append(consistency_table)
    report.append("")
    
    # 3.2 Detailed Consistency Analysis
    report.append("### 3.2 Detailed Consistency Analysis")
    report.append("")
    
    # 查找所有一致性分析文件
    pattern = os.path.join(data_dir, "**", "*_analysis.json")
    analysis_files = glob.glob(pattern, recursive=True)
    
    if analysis_files:
        for analysis_file in sorted(analysis_files):
            filename = os.path.basename(analysis_file)
            report.append(f"**{filename}**")
            report.append("")
            
            try:
                analysis_data = load_analysis_file(analysis_file)
                
                # Display overall metrics
                report.append(f"- Total Tasks: {analysis_data.get('total_tasks', 'N/A')}")
                report.append(f"- Analyzed Tasks: {analysis_data.get('analyzed_tasks', 'N/A')}")
                report.append(f"- Average Jaccard Similarity: {analysis_data.get('avg_jaccard_similarity', 0):.3f}")
                report.append(f"- Average Structure Consistency: {analysis_data.get('avg_structure_consistency', 0):.3f}")
                report.append("")
                
                # Display task-level consistency
                if 'task_consistency' in analysis_data:
                    report.append("**Task-Level Consistency:**")
                    report.append("")
                    for task_id, task_data in analysis_data['task_consistency'].items():
                        report.append(f"  - Task {task_id}:")
                        report.append(f"    - Number of Runs: {task_data.get('num_runs', 'N/A')}")
                        report.append(f"    - Valid Runs: {task_data.get('valid_runs', 'N/A')}")
                        report.append(f"    - Average Jaccard: {task_data.get('avg_jaccard', 0):.3f}")
                        report.append(f"    - Structure Consistency: {task_data.get('structure_consistency', 0):.3f}")
                        report.append("")
                
            except Exception as e:
                report.append(f"Error reading analysis file: {e}")
                report.append("")
    else:
        report.append("No consistency analysis files found")
        report.append("")
    
    # 4. Status Description
    report.append("## 4. Status Description")
    report.append("")
    report.append("- ✅ Success: All metrics meet expectations")
    report.append("- ⚠️ Warning: Some metrics do not meet expectations")
    report.append("- ❌ Failure: Major metrics do not meet expectations")
    report.append("")
    
    # 5. File Statistics
    report.append("## 5. File Statistics")
    report.append("")
    
    # Statistics for various types of files
    file_types = {
        "test_only": "Test Generation",
        "code_only": "Code Generation", 
        "tdd_": "Full TDD",
        "consistency_check": "Consistency Check",
        "_comprehensive_report.txt": "Quality Analysis Reports",
        "_analysis.json": "Consistency Analysis"
    }
    
    for pattern, description in file_types.items():
        if pattern.endswith('.txt') or pattern.endswith('.json'):
            files = glob.glob(os.path.join(data_dir, "**", f"*{pattern}"), recursive=True)
        else:
            files = glob.glob(os.path.join(data_dir, "**", f"{pattern}*"), recursive=True)
        
        report.append(f"- {description}: {len(files)} files")
    
    report.append("")
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"Report saved to: {output_file}")
    return output_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Generate experiment report")
    parser.add_argument("--data_dir", default="benchmarks", help="Data directory path")
    parser.add_argument("--output", help="Output report file path")
    
    args = parser.parse_args()
    
    try:
        output_file = generate_experiment_report(args.data_dir, args.output)
        print(f"\nExperiment report generated successfully!")
        print(f"Report file: {output_file}")
        
        # 显示报告内容
        print("\n" + "="*60)
        print("REPORT PREVIEW")
        print("="*60)
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:2000] + "..." if len(content) > 2000 else content)
        
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
