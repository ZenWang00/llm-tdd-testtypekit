#!/usr/bin/env python3
"""
MBPP迭代修复Pipeline - 完整流程

完整的TDD迭代修复流程：
1. 从问题描述开始，生成测试用例
2. 基于测试生成初始代码
3. 执行测试
4. 如果失败，进行迭代修复
"""

import os
import sys
import json
import datetime
from typing import Dict, List, Any, Optional
from tqdm import tqdm

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.pytest_executor import PytestExecutor
from pipelines.lc_chain.prompts.mbpp_repair_prompt import build_repair_prompt
from pipelines.lc_chain.generator import generate_tests_for_mbpp, generate_implementation_with_tests_mbpp, generate_repaired_code_mbpp


class IterativeRepairMBPPPipeline:
    """MBPP迭代修复Pipeline - 完整流程"""
    
    def __init__(self, model: str = "gpt-4o-mini", max_rounds: int = 2, temperature: float = 0.1):
        self.model = model
        self.max_rounds = max_rounds
        self.temperature = temperature
        self.executor = PytestExecutor()
        
    def create_output_directory(self, base_dir: str) -> str:
        """创建输出目录"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_dir, f"iterative_repair_T{self.temperature}_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def load_mbpp_problems(self, problem_file: str, start_task: int, num_tasks: int) -> List[Dict[str, Any]]:
        """从真实MBPP数据集中加载问题，按范围返回规范化字段(prompt/reference_code)"""
        all_items: List[Dict[str, Any]] = []
        with open(problem_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                # 兼容不同字段命名：text/prompt, code/reference_code
                prompt = data.get('prompt') or data.get('text') or ''
                reference_code = data.get('reference_code') or data.get('code') or ''
                task_id = data.get('task_id')
                if task_id is None:
                    continue
                all_items.append({
                    'task_id': str(task_id),
                    'prompt': prompt,
                    'reference_code': reference_code,
                    'test_list': data.get('test_list', []),
                    'challenge_test_list': data.get('challenge_test_list', []),
                })
        # 按task_id排序（数值）后切片
        all_items.sort(key=lambda x: int(x['task_id']))
        end = min(start_task + num_tasks, len(all_items))
        return all_items[start_task:end]
    
    def save_initial_tests(self, output_dir: str, task_id: str, generated_tests: str, temperature: float):
        """保存第一次生成的测试用例"""
        test_data = {
            "task_id": task_id,
            "temperature": temperature,
            "generated_tests": generated_tests,
            "method": "iterative_repair_mbpp",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": "test_generation"
        }
        
        filename = "initial_tests.jsonl"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(test_data, ensure_ascii=False) + '\n')
    
    def _get_tests_for_task(self, output_dir: str, task_id: str) -> Optional[str]:
        """从 initial_tests.jsonl 读取指定 task 的测试用例文本"""
        filepath = os.path.join(output_dir, "initial_tests.jsonl")
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if str(data.get('task_id')) == str(task_id):
                    return data.get('generated_tests')
        return None
    
    def run_iterative_repair_for_task(self, problem: Dict[str, Any], output_dir: str, temperature: float):
        """为单个任务运行迭代修复"""
        task_id = str(problem['task_id'])
        print(f"\n🔄 Processing task {task_id}")
        
        # Step 1: 生成测试用例
        print(f"  📝 Step 1: Generating tests for task {task_id}")
        try:
            description = problem['prompt']
            reference_code = problem.get('reference_code', '')
            
            # 生成测试用例
            generated_tests = generate_tests_for_mbpp(
                description, 
                reference_code, 
                self.model,
                temperature=temperature
            )
            print(f"  ✅ Tests generated: {len(generated_tests)} characters")
            
            # 立即保存第一次生成的测试用例
            self.save_initial_tests(output_dir, task_id, generated_tests, temperature)
            
            # 从文件读取回固定测试，确保后续严格以磁盘为准
            persisted_tests = self._get_tests_for_task(output_dir, task_id)
            if persisted_tests is not None:
                generated_tests = persisted_tests
            
        except Exception as e:
            print(f"  ❌ Test generation failed: {e}")
            return {
                "task_id": task_id,
                "status": "test_generation_failed",
                "error": str(e),
                "rounds_used": 0
            }
        
        # Step 2: 生成初始代码（使用 initial_tests.jsonl 中的固定测试）
        print(f"  💻 Step 2: Generating initial code for task {task_id}")
        try:
            generated_code = generate_implementation_with_tests_mbpp(
                description,
                generated_tests,
                reference_code,
                self.model,
                temperature=temperature
            )
            print(f"  ✅ Code generated: {len(generated_code)} characters")
            
        except Exception as e:
            print(f"  ❌ Code generation failed: {e}")
            return {
                "task_id": task_id,
                "status": "code_generation_failed",
                "error": str(e),
                "rounds_used": 0,
                "generated_tests": generated_tests
            }
        
        # Step 3: 执行测试
        print(f"  🧪 Step 3: Executing tests for task {task_id}")
        test_result = self.executor.execute_tests(generated_code, generated_tests)
        
        if test_result.failed_tests == 0:
            print(f"  🎉 All tests passed! Task {task_id} completed successfully")
            # 保存第1轮的结果
            self.save_round_data(output_dir, 1, {
                "task_id": task_id,
                "round": 1,
                "temperature": temperature,
                "test_execution_summary": {
                    "total_tests": test_result.total_tests,
                    "passed_tests": test_result.passed_tests,
                    "failed_tests": test_result.failed_tests,
                    "success_rate": test_result.success_rate
                },
                "passed_test_details": test_result.passed_test_details,
                "failed_test_details": test_result.failed_test_details,
                "execution_metadata": {
                    "execution_time": test_result.execution_time,
                    "memory_usage": test_result.memory_usage,
                    "python_version": test_result.python_version,
                    "pytest_version": test_result.pytest_version
                },
                "method": "iterative_repair_mbpp",
                "model": self.model,
                "timestamp": datetime.datetime.now().isoformat(),
                "stage": "test_execution",
                "ready_for_repair": False,
                "can_stop_iteration": True
            }, "results")
            
            # 保存第1轮的代码（不再冗余存测试，保留指针）
            self.save_round_data(output_dir, 1, {
                "task_id": task_id,
                "round": 1,
                "temperature": temperature,
                "generated_code": generated_code,
                "tests_source": "initial_tests.jsonl",
                "tests_task_id": task_id,
                "method": "iterative_repair_mbpp",
                "model": self.model,
                "timestamp": datetime.datetime.now().isoformat(),
                "stage": "code_generation"
            }, "code")
            
            return {
                "task_id": task_id,
                "status": "success",
                "rounds_used": 1,
                "generated_tests": generated_tests,
                "generated_code": generated_code,
                "test_result": {
                    "total_tests": test_result.total_tests,
                    "passed_tests": test_result.passed_tests,
                    "failed_tests": test_result.failed_tests
                }
            }
        
        print(f"  ⚠️  Tests failed: {test_result.failed_tests}/{test_result.total_tests} failed")
        
        # 保存第1轮的结果
        self.save_round_data(output_dir, 1, {
            "task_id": task_id,
            "round": 1,
            "temperature": temperature,
            "test_execution_summary": {
                "total_tests": test_result.total_tests,
                "passed_tests": test_result.passed_tests,
                "failed_tests": test_result.failed_tests,
                "success_rate": test_result.success_rate
            },
            "passed_test_details": test_result.passed_test_details,
            "failed_test_details": test_result.failed_test_details,
            "execution_metadata": {
                "execution_time": test_result.execution_time,
                "memory_usage": test_result.memory_usage,
                "python_version": test_result.python_version,
                "pytest_version": test_result.pytest_version
            },
            "method": "iterative_repair_mbpp",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": "test_execution",
            "ready_for_repair": True,
            "can_stop_iteration": False
        }, "results")
        
        # 保存第1轮的代码（不再冗余存测试，保留指针）
        self.save_round_data(output_dir, 1, {
            "task_id": task_id,
            "round": 1,
            "temperature": temperature,
            "generated_code": generated_code,
            "tests_source": "initial_tests.jsonl",
            "tests_task_id": task_id,
            "method": "iterative_repair_mbpp",
            "model": self.model,
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": "code_generation"
        }, "code")
        
        # Step 4: 迭代修复
        current_code = generated_code
        current_round = 1
        
        while current_round <= self.max_rounds:
            print(f"  🔧 Round {current_round + 1}: Attempting repair for task {task_id}")
            
            try:
                # 构建修复提示（包含参考实现）
                repair_prompt = build_repair_prompt(
                    description=description,
                    reference_code=reference_code,
                    all_tests=generated_tests,
                    passed_tests=test_result.passed_test_details,
                    failed_tests=test_result.failed_test_details,
                    traceback=test_result.error_summary
                )
                
                # 使用专门的MBPP修复代码生成函数
                repaired_code = generate_repaired_code_mbpp(
                    repair_prompt, 
                    self.model,
                    temperature=temperature
                )
                
                print(f"  ✅ Repair code generated: {len(repaired_code)} characters")
                
                # 执行修复后的测试
                test_result = self.executor.execute_tests(repaired_code, generated_tests)
                
                # 保存修复轮次的结果
                self.save_round_data(output_dir, current_round + 1, {
                    "task_id": task_id,
                    "round": current_round + 1,
                    "temperature": temperature,
                    "test_execution_summary": {
                        "total_tests": test_result.total_tests,
                        "passed_tests": test_result.passed_tests,
                        "failed_tests": test_result.failed_tests,
                        "success_rate": test_result.success_rate
                    },
                    "passed_test_details": test_result.passed_test_details,
                    "failed_test_details": test_result.failed_test_details,
                    "execution_metadata": {
                        "execution_time": test_result.execution_time,
                        "memory_usage": test_result.memory_usage,
                        "python_version": test_result.python_version,
                        "pytest_version": test_result.pytest_version
                    },
                    "method": "iterative_repair_mbpp",
                    "model": self.model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "stage": "test_execution",
                    "ready_for_repair": test_result.failed_tests > 0,
                    "can_stop_iteration": test_result.failed_tests == 0
                }, "results")
                
                # 保存修复轮次的代码（不再冗余存测试，保留指针）
                self.save_round_data(output_dir, current_round + 1, {
                    "task_id": task_id,
                    "round": current_round + 1,
                    "temperature": temperature,
                    "generated_code": repaired_code,
                    "tests_source": "initial_tests.jsonl",
                    "tests_task_id": task_id,
                    "method": "iterative_repair_mbpp",
                    "model": self.model,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "stage": "code_repair"
                }, "code")
                
                if test_result.failed_tests == 0:
                    print(f"  🎉 Repair successful! All tests passed in round {current_round + 1}")
                    return {
                        "task_id": task_id,
                        "status": "success",
                        "rounds_used": current_round + 1,
                        "generated_tests": generated_tests,
                        "generated_code": repaired_code,
                        "test_result": {
                            "total_tests": test_result.total_tests,
                            "passed_tests": test_result.passed_tests,
                            "failed_tests": test_result.failed_tests
                        }
                    }
                
                print(f"  ⚠️  Repair failed: {test_result.failed_tests}/{test_result.total_tests} still failing")
                current_code = repaired_code
                current_round += 1
                
            except Exception as e:
                print(f"  ❌ Repair round {current_round + 1} failed: {e}")
                current_round += 1
        
        # 所有修复尝试都失败了
        print(f"  💥 All repair attempts failed for task {task_id}")
        
        # 保存最终状态
        self.save_task_final_status(output_dir, task_id, current_round, False, 
                                  test_result.passed_tests / test_result.total_tests if test_result.total_tests > 0 else 0)
        
        return {
            "task_id": task_id,
            "status": "failed",
            "rounds_used": self.max_rounds + 1,
            "generated_tests": generated_tests,
            "generated_code": current_code,
            "test_result": {
                "total_tests": test_result.total_tests,
                "passed_tests": test_result.passed_tests,
                "failed_tests": test_result.failed_tests
            },
            "final_errors": [test.get('error_message', 'Unknown error') for test in test_result.failed_test_details]
        }
    
    def save_round_data(self, output_dir: str, round_num: int, data: Dict[str, Any], data_type: str):
        """保存轮次数据"""
        filename = f"round_{round_num}_{data_type}.jsonl"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def save_task_final_status(self, output_dir: str, task_id: str, total_rounds: int, final_success: bool, final_success_rate: float):
        """保存任务最终状态"""
        status_data = {
            "task_id": task_id,
            "temperature": self.temperature,
            "total_rounds": total_rounds,
            "final_success": final_success,
            "final_success_rate": final_success_rate,
            "completed_at": datetime.datetime.now().isoformat()
        }
        
        filename = f"task_{task_id}_final_status.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    def convert_to_mbpp_eval_format(self, output_dir: str, problems: List[Dict[str, Any]], max_rounds: int):
        """将最后一次round的代码转换为MBPP评估格式"""
        print(f"\n🔄 Converting final round code to MBPP evaluation format...")
        
        # 构建task_id到问题的映射
        problem_map = {str(p['task_id']): p for p in problems}
        
        # 读取每个任务的最终状态，确定实际使用的round数
        task_final_rounds = {}
        for i in range(1, len(problems) + 1):
            status_file = os.path.join(output_dir, f"task_{i}_final_status.json")
            if os.path.exists(status_file):
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    task_final_rounds[str(i)] = status_data.get('total_rounds', 1)
            else:
                # 如果没有状态文件，默认为第1轮
                task_final_rounds[str(i)] = 1
        
        # 读取并转换每个任务的最终代码
        converted_items = []
        for task_id in sorted(problem_map.keys(), key=int):
            final_round = task_final_rounds.get(task_id, 1)
            round_code_file = os.path.join(output_dir, f"round_{final_round}_code.jsonl")
            
            if not os.path.exists(round_code_file):
                print(f"  ⚠️  Round {final_round} code file not found for task {task_id}")
                continue
            
            # 从对应的round文件中读取该task的代码
            task_code = None
            with open(round_code_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    if str(data.get('task_id')) == task_id:
                        task_code = data.get('generated_code', '')
                        break
            
            if not task_code:
                print(f"  ⚠️  No code found for task {task_id} in round {final_round}")
                continue
            
            # 获取problem数据
            problem = problem_map[task_id]
            

            
            # 调试信息
            print(f"  DEBUG: Task {task_id}, Round {final_round}")
            print(f"  DEBUG: Code length: {len(task_code)}")
            print(f"  DEBUG: First 100 chars: {task_code[:100]}")
            
            converted_items.append({
                'task_id': task_id,
                'prompt': problem['prompt'],
                'completion': task_code,
                'test_list': problem.get('test_list', []),
                'challenge_test_list': problem.get('challenge_test_list', []),
                'reference_code': problem.get('reference_code', '')
            })
        
        # 保存转换后的文件
        output_file = os.path.join(output_dir, "mbpp_eval_final.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in converted_items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"  ✅ Converted {len(converted_items)} tasks to MBPP evaluation format")
        print(f"  📁 Output file: {output_file}")
        print(f"  💡 You can now run: python analyze_mbpp_results_fixed.py --result_file {output_file}")
        
        return output_file
    

    

    
    def run_pipeline(self, problem_file: str, num_tasks: int, start_task: int, max_rounds: int, 
                    temperature: float, model: str, output_dir: str = None):
        """运行完整的迭代修复Pipeline"""
        
        print(f"🚀 Starting MBPP Iterative Repair Pipeline")
        print(f"📖 Problem file: {problem_file}")
        print(f"📊 Tasks: {start_task} to {start_task + num_tasks - 1} ({num_tasks} total)")
        print(f"🔄 Max rounds: {max_rounds}")
        print(f"🌡️  Temperature: {temperature}")
        print(f"🤖 Model: {model}")
        print("=" * 80)
        
        # 创建输出目录
        if output_dir is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"mbpp_iterative_repair_{num_tasks}tasks_{max_rounds}rounds_T{temperature}_{timestamp}"
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        
        # 加载MBPP问题数据（真实数据源）
        print(f"📖 Loading MBPP problems...")
        selected_problems = self.load_mbpp_problems(problem_file, start_task, num_tasks)
        
        print(f"🎯 Processing {len(selected_problems)} tasks")
        
        # 处理每个任务
        results = []
        for problem in tqdm(selected_problems, desc="Processing tasks"):
            result = self.run_iterative_repair_for_task(problem, output_dir, temperature)
            results.append(result)
            
            # 如果任务成功，保存最终状态
            if result["status"] == "success":
                self.save_task_final_status(output_dir, result["task_id"], result["rounds_used"], True, 1.0)
        
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"📁 Results saved in: {output_dir}")
        
        # 转换为MBPP评估格式
        self.convert_to_mbpp_eval_format(output_dir, selected_problems, max_rounds)
        
        return output_dir, results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MBPP Iterative Repair Pipeline - Complete Flow")
    parser.add_argument("--problem_file", type=str, default="benchmarks/mbpp/mbpp/mbpp.jsonl", help="MBPP problem file path")
    parser.add_argument("--num_tasks", type=int, default=10, help="Number of tasks to process")
    parser.add_argument("--start_task", type=int, default=0, help="Starting task index")
    parser.add_argument("--max_rounds", type=int, default=3, help="Maximum repair rounds")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature for generation")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--output_dir", type=str, help="Output directory (optional)")
    
    args = parser.parse_args()
    
    try:
        # 创建Pipeline
        pipeline = IterativeRepairMBPPPipeline(
            model=args.model,
            max_rounds=args.max_rounds,
            temperature=args.temperature
        )
        
        # 运行Pipeline
        output_dir, results = pipeline.run_pipeline(
            problem_file=args.problem_file,
            num_tasks=args.num_tasks,
            start_task=args.start_task,
            max_rounds=args.max_rounds,
            temperature=args.temperature,
            model=args.model,
            output_dir=args.output_dir
        )
        
    except Exception as e:
        print(f"💥 Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()