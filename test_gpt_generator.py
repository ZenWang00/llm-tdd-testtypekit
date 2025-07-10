import os
import openai
from human_eval.data import write_jsonl, read_problems

def generate_one_completion(prompt, model="gpt-4o-mini"):
    """
    调用GPT API生成代码补全
    使用纯函数签名作为prompt，符合HumanEval官方评测方式
    """
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200,
            timeout=60
        )
        
        completion = response.choices[0].message.content.strip()
        
        # 提取代码块中的函数体
        if "```python" in completion:
            # 找到代码块
            start = completion.find("```python") + 9
            end = completion.find("```", start)
            if end != -1:
                code_block = completion[start:end].strip()
                # 提取函数体（去掉函数签名）
                lines = code_block.split('\n')
                if len(lines) > 1 and lines[0].startswith('def '):
                    # 去掉第一行（函数签名），只保留函数体
                    function_body = '\n'.join(lines[1:]).strip()
                    return function_body
                return code_block
            else:
                # 没有找到结束标记，取开始后的所有内容
                code_block = completion[start:].strip()
                lines = code_block.split('\n')
                if len(lines) > 1 and lines[0].startswith('def '):
                    function_body = '\n'.join(lines[1:]).strip()
                    return function_body
                return code_block
        
        # 如果没有代码块，尝试直接提取函数体
        lines = completion.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # 找到函数签名，返回后面的函数体
                if i + 1 < len(lines):
                    return '\n'.join(lines[i+1:]).strip()
        
        # 如果只返回了简单的语句，添加缩进
        if completion.strip() and not completion.startswith('    '):
            return '    ' + completion.strip()
        
        return completion.strip()
        
    except Exception as e:
        print(f"API调用失败: {e}")
        return "    pass"

def test_with_example_problem():
    """
    使用example_problem.jsonl测试GPT API
    """
    # 使用read_problems()读取问题
    problems = read_problems("data/example_problem.jsonl")
    problem = problems["test/0"]  # 获取第一个问题
    
    print(f"测试问题: {problem['task_id']}")
    print(f"函数签名: {problem['prompt']}")
    print(f"标准答案: {problem['canonical_solution']}")
    print(f"测试用例: {problem['test']}")
    print("\n" + "="*50 + "\n")
    
    # 生成6个样本
    samples = []
    for i in range(6):
        print(f"生成样本 {i+1}/6...")
        completion = generate_one_completion(problem['prompt'])
        print(f"生成的代码: {completion}")
        
        sample = {
            "task_id": problem['task_id'],
            "completion": completion
        }
        samples.append(sample)
        print("-" * 30)
    
    # 保存到文件
    output_file = "data/my_gpt_samples.jsonl"
    write_jsonl(output_file, samples)
    print(f"\n样本已保存到: {output_file}")
    
    return output_file

if __name__ == "__main__":
    # 从环境变量获取API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("错误: 未找到OPENAI_API_KEY环境变量")
        exit(1)
    
    openai.api_key = api_key
    print("已从环境变量加载API密钥")
    
    # 运行测试
    output_file = test_with_example_problem()
    
    print(f"\n现在您可以运行评估:")
    print(f"evaluate_functional_correctness {output_file} --problem_file=data/example_problem.jsonl") 