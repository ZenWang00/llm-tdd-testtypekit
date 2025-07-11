#!/usr/bin/env python3
"""
LangChain HumanEval Pipeline
"""

import os
import sys
import datetime
sys.path.append('.')

from pipelines.langchain.generator import generate_one_completion_langchain
from human_eval.data import write_jsonl, read_problems

def generate_output_filename(model="gpt-4o-mini", prefix="langchain_results"):
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    model_clean = model.replace("-", "_").replace(".", "_")
    return f"benchmarks/humaneval/data/{prefix}_{model_clean}_{timestamp}.jsonl"

def run_langchain_pipeline(problem_file="benchmarks/humaneval/data/example_problem.jsonl", 
                          model="gpt-4o-mini"):
    """
    运行完整的LangChain pipeline：读取HumanEval问题并生成代码补全
    """
    try:
        output_file = generate_output_filename(model)
        
        # 读取HumanEval问题
        print(f"📖 读取问题文件: {problem_file}")
        problems = read_problems(problem_file)
        print(f"✅ 成功读取 {len(problems)} 个问题")
        
        # 生成代码补全
        samples = []
        for task_id, problem in problems.items():
            print(f"🔄 处理问题: {task_id}")
            print(f"   函数签名: {problem['prompt'].strip()}")
            
            completion = generate_one_completion_langchain(problem['prompt'], model)
            print(f"   生成代码: {completion}")
            
            sample = {
                "task_id": task_id,
                "completion": completion,
                "method": "langchain",
                "model": model
            }
            samples.append(sample)
            print(f"   Request Finished\n")
        
        # 保存结果
        write_jsonl(output_file, samples)
        print(f"Result saved: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"process error: {e}")
        return None

if __name__ == "__main__":
    print("Run LangChain HumanEval Pipeline")
    print("=" * 50)
    
    output_file = run_langchain_pipeline()
    
    if output_file:
        print("\n LangChain pipeline successed")
        print(f"\n Result file name: {output_file}")
    else:
        print("\n LangChain pipeline failed")
        sys.exit(1) 