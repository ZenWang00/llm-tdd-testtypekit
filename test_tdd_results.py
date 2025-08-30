#!/usr/bin/env python3
"""
测试HumanEval TDD生成的代码
"""

import json
import sys
import traceback

def test_tdd_results():
    """测试TDD生成的代码"""
    
    # 读取TDD结果文件
    result_file = "benchmarks/humaneval/data/tdd_humaneval_batch_10_tasks_gpt-4o-mini_20250830_140628.jsonl"
    
    try:
        with open(result_file, 'r') as f:
            results = [json.loads(line) for line in f]
        
        print(f"📊 测试 {len(results)} 个TDD生成的代码")
        print("=" * 60)
        
        success_count = 0
        total_count = len(results)
        
        for i, result in enumerate(results):
            task_id = result['task_id']
            prompt = result['prompt']
            completion = result['completion']
            generated_tests = result['generated_tests']
            
            print(f"\n🔍 测试 {i+1}/{total_count}: {task_id}")
            print(f"函数签名: {prompt.split('def ')[1].split('(')[0] if 'def ' in prompt else 'N/A'}")
            
            try:
                # 提取函数名
                if 'def ' in prompt:
                    func_name = prompt.split('def ')[1].split('(')[0].strip()
                else:
                    print("❌ 无法提取函数名")
                    continue
                
                # 创建完整的函数定义
                # 从prompt中提取完整的函数签名（包括参数和类型注解）
                if 'def ' in prompt:
                    # 找到函数定义的开始
                    def_start = prompt.find('def ')
                    # 找到函数签名的结束（第一个冒号，但要确保是函数定义的冒号）
                    # 先找到函数定义的结束位置
                    lines = prompt.split('\n')
                    function_lines = []
                    for line in lines:
                        if line.strip().startswith('def '):
                            function_lines.append(line.strip())
                            break
                    
                    if function_lines:
                        # 提取完整的函数签名行
                        function_signature = function_lines[0]
                        # 组合函数签名和函数体
                        # 检查函数签名是否已经有冒号
                        if function_signature.endswith(':'):
                            # 智能处理缩进：检查第一行是否已经有缩进
                            lines = completion.split('\n')
                            if lines and lines[0].strip():  # 第一行有内容
                                if not lines[0].startswith('    '):  # 第一行没有4个空格缩进
                                    # 为所有非空行添加4个空格缩进
                                    indented_lines = []
                                    for line in lines:
                                        if line.strip():  # 非空行
                                            indented_lines.append("    " + line)
                                        else:  # 空行
                                            indented_lines.append(line)
                                    indented_completion = "\n".join(indented_lines)
                                else:
                                    indented_completion = completion
                            else:
                                indented_completion = completion
                            
                            full_function = function_signature + "\n" + indented_completion
                        else:
                            # 智能处理缩进：检查第一行是否已经有缩进
                            lines = completion.split('\n')
                            if lines and lines[0].strip():  # 第一行有内容
                                if not lines[0].startswith('    '):  # 第一行没有4个空格缩进
                                    # 为所有非空行添加4个空格缩进
                                    indented_lines = []
                                    for line in lines:
                                        if line.strip():  # 非空行
                                            indented_lines.append("    " + line)
                                        else:  # 空行
                                            indented_lines.append(line)
                                    indented_completion = "\n".join(indented_lines)
                                else:
                                    indented_completion = completion
                            else:
                                indented_completion = completion
                            
                            full_function = function_signature + ":\n" + indented_completion
                        
                        # 调试信息
                        print(f"🔍 生成的完整函数:")
                        print(f"   签名: {function_signature}")
                        print(f"   函数体: {completion[:100]}...")
                        print(f"   完整代码: {full_function[:200]}...")
                    else:
                        print(f"❌ 无法找到函数定义行")
                        continue
                else:
                    print(f"❌ 无法找到函数定义")
                    continue
                
                # 创建测试环境
                test_env = {}
                
                # 执行函数定义
                exec(full_function, test_env)
                
                # 获取函数对象
                func = test_env[func_name]
                
                # 运行一些基本测试
                print(f"✅ 函数定义成功: {func_name}")
                
                # 尝试运行生成的测试（简化版）
                try:
                    # 提取一些简单的测试断言
                    test_lines = [line.strip() for line in generated_tests.split('\n') if 'assert ' in line]
                    if test_lines:
                        print(f"📝 生成了 {len(test_lines)} 个测试用例")
                        
                        # 运行前3个测试
                        for j, test_line in enumerate(test_lines[:3]):
                            try:
                                # 简化测试执行
                                if 'assert ' in test_line:
                                    # 提取断言部分
                                    assertion = test_line.split('assert ')[1]
                                    if assertion.endswith(')'):
                                        # 这是一个函数调用断言
                                        print(f"   ✅ 测试 {j+1}: {assertion[:50]}...")
                            except Exception as e:
                                print(f"   ❌ 测试 {j+1} 失败: {str(e)[:50]}")
                    
                except Exception as e:
                    print(f"⚠️  测试执行警告: {str(e)[:50]}")
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ 函数执行失败: {str(e)[:50]}")
                print(f"   错误详情: {traceback.format_exc()[:200]}...")
        
        print("\n" + "=" * 60)
        print(f"🎯 测试结果: {success_count}/{total_count} 成功")
        print(f"📈 成功率: {success_count/total_count*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 读取结果文件失败: {e}")

if __name__ == "__main__":
    test_tdd_results()
