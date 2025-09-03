#!/usr/bin/env python3
"""
MBPP迭代修复快速测试脚本

用于快速测试小规模实验，验证脚本功能
"""

import os
import sys
import subprocess
import time
import json
import argparse
from datetime import datetime


def run_quick_test(problem_file: str, num_tasks: int = 5, temperatures: list = None):
    """运行快速测试"""
    
    if temperatures is None:
        temperatures = [0.1, 0.7]
    
    print(f"🚀 MBPP Quick Test")
    print(f"📊 Tasks: {num_tasks}")
    print(f"🌡️  Temperatures: {temperatures}")
    print("=" * 50)
    
    results = []
    
    for temp in temperatures:
        print(f"\n🌡️  Testing temperature {temp}...")
        
        start_time = time.time()
        
        # 运行迭代修复
        cmd = [
            "python", "pipelines/batch_mbpp_iterative_repair.py",
            "--problem_file", problem_file,
            "--num_tasks", str(num_tasks),
            "--start_task", "0",
            "--max_rounds", "2",
            "--temperature", str(temp),
            "--model", "gpt-4o-mini"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            exec_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ T{temp} completed in {exec_time:.1f}s")
                
                # 查找输出目录
                output_dirs = [d for d in os.listdir("benchmarks/mbpp/data") 
                              if d.startswith(f"iterative_repair_T{temp}_")]
                
                if output_dirs:
                    latest_output = max(output_dirs, key=lambda x: x.split('_')[-1])
                    output_path = os.path.join("benchmarks/mbpp/data", latest_output)
                    
                    # 分析结果
                    success_count = 0
                    total_count = 0
                    
                    status_files = []
                    for root, dirs, files in os.walk(output_path):
                        for file in files:
                            if file.startswith("task_") and file.endswith("_final_status.json"):
                                status_files.append(os.path.join(root, file))
                    
                    for status_file in status_files:
                        with open(status_file, 'r') as f:
                            status = json.load(f)
                            total_count += 1
                            if status['final_success']:
                                success_count += 1
                    
                    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                    
                    results.append({
                        "temperature": temp,
                        "success_rate": success_rate,
                        "success_count": success_count,
                        "total_count": total_count,
                        "execution_time": exec_time,
                        "output_dir": output_path
                    })
                    
                    print(f"  📈 Success Rate: {success_count}/{total_count} ({success_rate:.1f}%)")
                else:
                    print(f"  ⚠️  No output directory found")
            else:
                print(f"❌ T{temp} failed with return code {result.returncode}")
                print(f"  Error: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            exec_time = time.time() - start_time
            print(f"⏰ T{temp} timed out after {exec_time:.1f}s")
        except Exception as e:
            exec_time = time.time() - start_time
            print(f"💥 T{temp} crashed: {e}")
    
    # 总结
    print(f"\n📊 Quick Test Summary:")
    for result in results:
        temp = result["temperature"]
        success_rate = result["success_rate"]
        exec_time = result["execution_time"]
        print(f"  T{temp}: {success_rate:.1f}% success in {exec_time:.1f}s")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Run MBPP quick test")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/data/langchain_mbpp_batch_974_tasks_gpt-4o-mini_20250830_220247.jsonl", 
                       help="Path to MBPP problem file")
    parser.add_argument("--num_tasks", type=int, default=5, help="Number of tasks to process")
    parser.add_argument("--temperatures", nargs="+", type=float, default=[0.1, 0.7],
                       help="List of temperatures to test")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.problem_file):
        print(f"❌ Error: Problem file {args.problem_file} not found")
        sys.exit(1)
    
    try:
        results = run_quick_test(args.problem_file, args.num_tasks, args.temperatures)
        print(f"\n🎉 Quick test completed!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
