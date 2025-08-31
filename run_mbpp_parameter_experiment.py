#!/usr/bin/env python3
"""
MBPP参数化实验脚本

运行一次完整的TDD (200 tasks, T:0.0) 和多次Test Only (200 tasks, 不同temperature)
然后评估测试用例质量指标
"""

import os
import sys
import json
import datetime
from typing import Dict, Any, List
from tqdm import tqdm
import argparse

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipelines.batch_mbpp_tdd import TDDMBPPBatchPipeline
from pipelines.batch_mbpp_test_only import TestOnlyMBPPBatchPipeline
from pipelines.lc_chain.generator import generate_tests_for_mbpp


def run_full_tdd_mbpp(num_tasks: int = 200, start_task: int = 0, model: str = "gpt-4o-mini", temp_dir: str = None):
    """运行完整的TDD pipeline (200 tasks, T:0.0)"""
    print(f"\n{'='*60}")
    print(f"Running Full TDD MBPP Experiment")
    print(f"Tasks: {num_tasks}, Start: {start_task}, Model: {model}")
    print(f"{'='*60}")
    
    try:
        pipeline = TDDMBPPBatchPipeline(model)
        
        # 修改输出路径到临时目录
        if temp_dir:
            # 重写 pipeline 的 get_output_filename 方法
            def temp_output_filename(num_tasks, prefix):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{prefix}_{num_tasks}_tasks_{model}_{timestamp}.jsonl"
                return os.path.join(temp_dir, filename)
            
            pipeline.get_output_filename = temp_output_filename
        
        output_file = pipeline.run_batch_pipeline(
            problem_file="benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl",
            num_tasks=num_tasks,
            start_task=start_task
        )
        
        # 读取结果用于返回
        results = []
        if output_file and os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
        
        print(f"\n✅ Full TDD completed successfully!")
        print(f"Output file: {output_file}")
        print(f"Generated {len(results)} samples")
        
        return output_file, results
        
    except Exception as e:
        print(f"❌ Full TDD failed: {e}")
        return None, []


def run_test_only_mbpp(num_tasks: int, start_task: int, temperature: float, 
                       model: str = "gpt-4o-mini", temp_dir: str = None):
    """运行Test Only pipeline (指定temperature)"""
    print(f"\n{'='*60}")
    print(f"Running Test Only MBPP Experiment")
    print(f"Tasks: {num_tasks}, Start: {start_task}, Temperature: {temperature}, Model: {model}")
    print(f"{'='*60}")
    
    try:
        # 创建自定义的Test Only pipeline
        pipeline = TestOnlyMBPPBatchPipeline(model)
        
        # 读取问题
        problems = pipeline.read_problems("benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl")
        
        # 选择任务
        task_ids = list(problems.keys())
        task_ids.sort(key=int)
        end_task = min(start_task + num_tasks, len(task_ids))
        selected_task_ids = task_ids[start_task:end_task]
        
        print(f"Processing {len(selected_task_ids)} tasks...")
        
        results = []
        # 使用tqdm显示进度条
        for task_id in tqdm(selected_task_ids, desc=f"Test Generation (T:{temperature})"):
            problem = problems[task_id]
            try:
                description = problem['prompt']  # 修复：使用'prompt'而不是'text'
                reference_code = problem.get('reference_code', '')
                
                # 生成测试（使用指定temperature）
                generated_tests = generate_tests_for_mbpp(
                    description, reference_code, model, temperature=temperature
                )
                
                # 创建样本
                sample = {
                    "task_id": task_id,
                    "prompt": problem['prompt'],
                    "reference_code": reference_code,
                    "generated_tests": generated_tests,
                    "method": "test_only_mbpp",
                    "model": model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "stage": "test_generation_only",
                    "temperature": temperature
                }
                results.append(sample)
                
            except Exception as e:
                print(f"Error in task {task_id}: {e}")
                sample = {
                    "task_id": task_id,
                    "prompt": problem['prompt'],
                    "reference_code": reference_code,
                    "generated_tests": "",
                    "method": "test_only_mbpp",
                    "model": model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "stage": "test_generation_only",
                    "temperature": temperature,
                    "error": str(e)
                }
                results.append(sample)
        
        # 保存结果到临时目录
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if temp_dir:
            output_file = os.path.join(temp_dir, f"test_only_mbpp_batch_{num_tasks}_tasks_T{temperature}_{model}_{timestamp}.jsonl")
        else:
            output_file = f"benchmarks/mbpp/data/test_only_mbpp_batch_{num_tasks}_tasks_T{temperature}_{model}_{timestamp}.jsonl"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in results:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Test Only (T:{temperature}) completed successfully!")
        print(f"Output file: {output_file}")
        print(f"Generated {len(results)} samples")
        
        return output_file, results
        
    except Exception as e:
        print(f"❌ Test Only (T:{temperature}) failed: {e}")
        return None, []


def analyze_test_quality(output_files: List[str]):
    """分析所有输出文件的测试质量"""
    print(f"\n{'='*60}")
    print(f"Analyzing Test Quality for All Experiments")
    print(f"{'='*60}")
    
    for output_file in output_files:
        if not output_file or not os.path.exists(output_file):
            continue
            
        print(f"\n--- Analyzing: {os.path.basename(output_file)} ---")
        
        try:
            # 读取结果
            samples = []
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        samples.append(json.loads(line))
            
            if not samples:
                print("No samples found")
                continue
            
            # 提取参数信息
            temperature = samples[0].get('temperature', 'N/A')
            method = samples[0].get('method', 'N/A')
            num_samples = len(samples)
            
            print(f"Method: {method}")
            print(f"Temperature: {temperature}")
            print(f"Total samples: {num_samples}")
            
            # 统计错误
            errors = [s for s in samples if 'error' in s]
            if errors:
                print(f"Errors: {len(errors)}")
            
            # 统计成功生成的测试
            successful = [s for s in samples if s.get('generated_tests') and 'error' not in s]
            print(f"Successful generations: {len(successful)}")
            
            # 计算平均测试长度
            if successful:
                avg_length = sum(len(s['generated_tests']) for s in successful) / len(successful)
                print(f"Average test length: {avg_length:.0f} characters")
            
        except Exception as e:
            print(f"Error analyzing {output_file}: {e}")


def run_parameter_experiment(num_tasks: int = 200, start_task: int = 0, 
                           model: str = "gpt-4o-mini"):
    """运行完整的参数化实验"""
    print(f"🚀 Starting MBPP Parameter Experiment")
    print(f"Tasks: {num_tasks}, Start: {start_task}, Model: {model}")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建临时目录
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"benchmarks/mbpp/data/temp_{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"📁 Created temporary directory: {temp_dir}")
    
    output_files = []
    
    # 1. 运行完整TDD (baseline)
    print(f"\n📊 Step 1: Running Full TDD (Baseline)")
    tdd_file, tdd_results = run_full_tdd_mbpp(num_tasks, start_task, model, temp_dir)
    if tdd_file:
        output_files.append(tdd_file)
    
    # 2. 运行多次Test Only (不同temperature)
    temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    print(f"\n📊 Step 2: Running Test Only with Different Temperatures")
    for i, temp in enumerate(temperatures, 1):
        print(f"\n--- Experiment {i}/{len(temperatures)} ---")
        test_file, test_results = run_test_only_mbpp(num_tasks, start_task, temp, model, temp_dir)
        if test_file:
            output_files.append(test_file)
    
    # 3. 分析所有结果
    print(f"\n📊 Step 3: Analyzing All Results")
    analyze_test_quality(output_files)
    
    # 4. 运行测试质量分析
    print(f"\n📊 Step 4: Running Test Quality Analysis")
    print(f"Analyzing data in: {temp_dir}")
    
    # 为每个输出文件运行分析
    for output_file in output_files:
        if output_file and os.path.exists(output_file):
            print(f"Analyzing: {os.path.basename(output_file)}")
            try:
                # 运行分析脚本
                import subprocess
                result = subprocess.run([
                    "python", "analyze_tdd_comprehensive.py", 
                    output_file
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Analysis completed for {os.path.basename(output_file)}")
                else:
                    print(f"⚠️ Analysis failed for {os.path.basename(output_file)}: {result.stderr}")
            except Exception as e:
                print(f"⚠️ Could not run analysis for {os.path.basename(output_file)}: {e}")
    
    # 5. 生成实验报告
    print(f"\n📊 Step 5: Generating Experiment Report")
    print(f"Analyzing data in: {temp_dir}")
    
    try:
        # 调用报告生成脚本
        import subprocess
        result = subprocess.run([
            "python", "generate_experiment_report.py", 
            "--data_dir", temp_dir,
            "--output", f"report/mbpp_experiment_{timestamp}.md"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Report generated successfully!")
            print(f"Report file: report/mbpp_experiment_{timestamp}.md")
        else:
            print(f"⚠️ Report generation failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Could not generate report automatically: {e}")
        print("You can manually run:")
        print(f"python generate_experiment_report.py --data_dir {temp_dir}")
    
    print(f"\n🎉 Parameter experiment completed!")
    print(f"Generated {len(output_files)} output files in: {temp_dir}")
    for file in output_files:
        print(f"  - {os.path.basename(file)}")
    
    return output_files, temp_dir


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Run MBPP parameter experiment")
    parser.add_argument("--num_tasks", type=int, default=200, help="Number of tasks to process")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use")
    
    args = parser.parse_args()
    
    try:
        output_files, temp_dir = run_parameter_experiment(
            num_tasks=args.num_tasks,
            start_task=args.start_task,
            model=args.model
        )
        
        print(f"\n✅ Experiment completed successfully!")
        print(f"Total output files: {len(output_files)}")
        print(f"Data directory: {temp_dir}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Experiment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
