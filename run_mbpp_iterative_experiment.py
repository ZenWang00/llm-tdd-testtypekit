#!/usr/bin/env python3
"""
MBPP迭代修复大规模实验脚本

运行100个任务的3轮迭代修复实验，测试不同温度参数的效果
"""

import os
import sys
import subprocess
import time
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

from tqdm import tqdm


class MBPPIterativeExperiment:
    """MBPP迭代修复实验管理器"""
    
    def __init__(self, 
                 problem_file: str,
                 num_tasks: int = 100,
                 start_task: int = 0,
                 max_rounds: int = 3,
                 temperatures: List[float] = None,
                 model: str = "gpt-4o-mini"):
        
        self.problem_file = problem_file
        self.num_tasks = num_tasks
        self.start_task = start_task
        self.max_rounds = max_rounds
        self.temperatures = temperatures or [0.1, 0.3, 0.5, 0.7, 0.9]
        self.model = model
        
        # 创建实验目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.experiment_dir = f"mbpp_iterative_experiment_{num_tasks}tasks_{max_rounds}rounds_{timestamp}"
        os.makedirs(self.experiment_dir, exist_ok=True)
        
        print(f"🚀 MBPP Iterative Repair Experiment")
        print(f"📁 Experiment Directory: {self.experiment_dir}")
        print(f"📊 Tasks: {start_task} to {start_task + num_tasks - 1} ({num_tasks} total)")
        print(f"🔄 Max Rounds: {max_rounds}")
        print(f"🌡️  Temperatures: {self.temperatures}")
        print(f"🤖 Model: {model}")
        print("=" * 80)
    
    def run_single_temperature_experiment(self, temperature: float) -> Dict[str, Any]:
        """运行单个温度的实验"""
        print(f"\n🌡️  Starting experiment for temperature {temperature}")
        
        # 创建温度特定的输出目录
        temp_dir = os.path.join(self.experiment_dir, f"T{temperature}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 构建命令
        cmd = [
            "python", "pipelines/batch_mbpp_iterative_repair.py",
            "--problem_file", self.problem_file,
            "--num_tasks", str(self.num_tasks),
            "--start_task", str(self.start_task),
            "--max_rounds", str(self.max_rounds),
            "--temperature", str(temperature),
            "--model", self.model
        ]
        
        print(f"📝 Command: {' '.join(cmd)}")
        
        start_time = time.time()
        
        try:
            # 运行实验
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Temperature {temperature} completed in {execution_time:.1f}s")
                
                # 查找输出目录
                output_dirs = [d for d in os.listdir("benchmarks/mbpp/data") 
                              if d.startswith(f"iterative_repair_T{temperature}_")]
                
                if output_dirs:
                    latest_output = max(output_dirs, key=lambda x: x.split('_')[-1])
                    output_path = os.path.join("benchmarks/mbpp/data", latest_output)
                    
                    # 移动到实验目录
                    final_output = os.path.join(temp_dir, "results")
                    os.rename(output_path, final_output)
                    
                    return {
                        "temperature": temperature,
                        "status": "success",
                        "execution_time": execution_time,
                        "output_dir": final_output,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                else:
                    return {
                        "temperature": temperature,
                        "status": "error",
                        "execution_time": execution_time,
                        "error": "No output directory found",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
            else:
                print(f"❌ Temperature {temperature} failed with return code {result.returncode}")
                return {
                    "temperature": temperature,
                    "status": "error",
                    "execution_time": execution_time,
                    "error": f"Process failed with return code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ Temperature {temperature} timed out after {execution_time:.1f}s")
            return {
                "temperature": temperature,
                "status": "timeout",
                "execution_time": execution_time,
                "error": "Process timed out"
            }
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"💥 Temperature {temperature} crashed: {e}")
            return {
                "temperature": temperature,
                "status": "crashed",
                "execution_time": execution_time,
                "error": str(e)
            }
    
    def run_experiments(self):
        """运行所有温度的实验"""
        print(f"\n🚀 Starting experiments for {len(self.temperatures)} temperatures...")
        print("🔄 Running experiments sequentially...")
        
        results = []
        
        for temp in tqdm(self.temperatures, desc="Temperatures"):
            result = self.run_single_temperature_experiment(temp)
            results.append(result)
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]):
        """分析实验结果"""
        print(f"\n📊 Analyzing results...")
        
        # 保存原始结果
        results_file = os.path.join(self.experiment_dir, "experiment_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 统计成功/失败
        successful_temps = [r for r in results if r["status"] == "success"]
        failed_temps = [r for r in results if r["status"] != "success"]
        
        print(f"\n=== Experiment Summary ===")
        print(f"Total temperatures: {len(self.temperatures)}")
        print(f"Successful: {len(successful_temps)}")
        print(f"Failed: {len(failed_temps)}")
        
        if successful_temps:
            print(f"\n=== Successful Experiments ===")
            for result in successful_temps:
                temp = result["temperature"]
                exec_time = result["execution_time"]
                output_dir = result["output_dir"]
                print(f"T{temp}: {exec_time:.1f}s -> {output_dir}")
        
        if failed_temps:
            print(f"\n=== Failed Experiments ===")
            for result in failed_temps:
                temp = result["temperature"]
                status = result["status"]
                error = result.get("error", "Unknown error")
                print(f"T{temp}: {status} - {error}")
        
        # 分析每个成功的实验
        if successful_temps:
            print(f"\n=== Detailed Analysis ===")
            for result in successful_temps:
                temp = result["temperature"]
                output_dir = result["output_dir"]
                
                print(f"\n🌡️  Temperature {temp}:")
                
                # 分析最终状态
                status_files = []
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.startswith("task_") and file.endswith("_final_status.json"):
                            status_files.append(os.path.join(root, file))
                
                if status_files:
                    success_count = 0
                    total_count = 0
                    total_rounds = 0
                    
                    for status_file in status_files:
                        with open(status_file, 'r') as f:
                            status = json.load(f)
                            total_count += 1
                            total_rounds += status['total_rounds']
                            if status['final_success']:
                                success_count += 1
                    
                    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                    avg_rounds = total_rounds / total_count if total_count > 0 else 0
                    
                    print(f"  📈 Success Rate: {success_count}/{total_count} ({success_rate:.1f}%)")
                    print(f"  🔄 Average Rounds: {avg_rounds:.1f}")
                    print(f"  📁 Output: {output_dir}")
                else:
                    print(f"  ⚠️  No status files found in {output_dir}")
        
        return results
    
    def convert_to_mbpp_format(self, results: List[Dict[str, Any]]):
        """转换成功实验的结果为MBPP格式"""
        print(f"\n🔄 Converting results to MBPP format...")
        
        successful_results = [r for r in results if r["status"] == "success"]
        
        for result in successful_results:
            temp = result["temperature"]
            output_dir = result["output_dir"]
            
            print(f"🌡️  Converting T{temp}...")
            
            # 查找round_1_code.jsonl文件
            code_file = os.path.join(output_dir, "round_1_code.jsonl")
            if os.path.exists(code_file):
                mbpp_file = os.path.join(output_dir, "mbpp_format_results.jsonl")
                
                try:
                    # 运行转换脚本
                    convert_cmd = [
                        "python", "convert_iterative_to_mbpp_format.py",
                        "--iterative_file", code_file,
                        "--output_file", mbpp_file
                    ]
                    
                    convert_result = subprocess.run(
                        convert_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if convert_result.returncode == 0:
                        print(f"  ✅ T{temp} converted successfully")
                        
                        # 运行MBPP评估
                        eval_cmd = [
                            "python", "analyze_mbpp_results_fixed.py",
                            "--result_file", mbpp_file
                        ]
                        
                        eval_result = subprocess.run(
                            eval_cmd,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        
                        if eval_result.returncode == 0:
                            print(f"  📊 T{temp} MBPP evaluation completed")
                            
                            # 保存评估结果
                            eval_file = os.path.join(output_dir, "mbpp_evaluation.txt")
                            with open(eval_file, 'w', encoding='utf-8') as f:
                                f.write(eval_result.stdout)
                        else:
                            print(f"  ❌ T{temp} MBPP evaluation failed")
                    else:
                        print(f"  ❌ T{temp} conversion failed")
                        
                except Exception as e:
                    print(f"  💥 T{temp} conversion error: {e}")
            else:
                print(f"  ⚠️  T{temp} no code file found")
    
    def generate_final_report(self, results: List[Dict[str, Any]]):
        """生成最终实验报告"""
        print(f"\n📝 Generating final report...")
        
        report_file = os.path.join(self.experiment_dir, "experiment_report.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# MBPP Iterative Repair Experiment Report\n\n")
            f.write(f"**Experiment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Tasks:** {self.start_task} to {self.start_task + self.num_tasks - 1} ({self.num_tasks} total)\n")
            f.write(f"**Max Rounds:** {self.max_rounds}\n")
            f.write(f"**Model:** {self.model}\n")
            f.write(f"**Temperatures:** {', '.join(map(str, self.temperatures))}\n\n")
            
            # 实验摘要
            successful_temps = [r for r in results if r["status"] == "success"]
            failed_temps = [r for r in results if r["status"] != "success"]
            
            f.write("## Experiment Summary\n\n")
            f.write(f"- **Total Temperatures:** {len(self.temperatures)}\n")
            f.write(f"- **Successful:** {len(successful_temps)}\n")
            f.write(f"- **Failed:** {len(failed_temps)}\n\n")
            
            # 详细结果
            f.write("## Detailed Results\n\n")
            
            for result in results:
                temp = result["temperature"]
                status = result["status"]
                exec_time = result.get("execution_time", 0)
                
                f.write(f"### Temperature {temp}\n\n")
                f.write(f"- **Status:** {status}\n")
                f.write(f"- **Execution Time:** {exec_time:.1f}s\n")
                
                if status == "success":
                    output_dir = result["output_dir"]
                    f.write(f"- **Output Directory:** {output_dir}\n")
                    
                    # 分析成功率
                    status_files = []
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            if file.startswith("task_") and file.endswith("_final_status.json"):
                                status_files.append(os.path.join(root, file))
                    
                    if status_files:
                        success_count = 0
                        total_count = 0
                        total_rounds = 0
                        
                        for status_file in status_files:
                            with open(status_file, 'r') as sf:
                                status_data = json.load(sf)
                                total_count += 1
                                total_rounds += status_data['total_rounds']
                                if status_data['final_success']:
                                    success_count += 1
                        
                        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                        avg_rounds = total_rounds / total_count if total_count > 0 else 0
                        
                        f.write(f"- **Success Rate:** {success_count}/{total_count} ({success_rate:.1f}%)\n")
                        f.write(f"- **Average Rounds:** {avg_rounds:.1f}\n")
                else:
                    error = result.get("error", "Unknown error")
                    f.write(f"- **Error:** {error}\n")
                
                f.write("\n")
        
        print(f"📄 Final report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Run MBPP iterative repair experiment")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl", 
                       help="Path to MBPP problem file")
    parser.add_argument("--num_tasks", type=int, default=100, help="Number of tasks to process")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--max_rounds", type=int, default=3, help="Maximum repair rounds")
    parser.add_argument("--temperatures", nargs="+", type=float, default=[0.1, 0.3, 0.5, 0.7, 0.9],
                       help="List of temperatures to test")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use")

    parser.add_argument("--skip_conversion", action="store_true", help="Skip MBPP format conversion")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.problem_file):
        print(f"❌ Error: Problem file {args.problem_file} not found")
        sys.exit(1)
    
    try:
        # 创建实验管理器
        experiment = MBPPIterativeExperiment(
            problem_file=args.problem_file,
            num_tasks=args.num_tasks,
            start_task=args.start_task,
            max_rounds=args.max_rounds,
            temperatures=args.temperatures,
            model=args.model
        )
        
        # 运行实验
        results = experiment.run_experiments()
        
        # 分析结果
        experiment.analyze_results(results)
        
        # 转换为MBPP格式（可选）
        if not args.skip_conversion:
            experiment.convert_to_mbpp_format(results)
        
        # 生成最终报告
        experiment.generate_final_report(results)
        
        print(f"\n🎉 Experiment completed successfully!")
        print(f"📁 Results saved in: {experiment.experiment_dir}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Experiment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
