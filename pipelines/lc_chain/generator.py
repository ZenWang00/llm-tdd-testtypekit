import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from .prompts.humaneval import HUMANEVAL_PROMPT_TEMPLATE

def generate_one_completion_langchain(prompt, model="gpt-4o-mini"):
    """
    使用LangChain生成单个代码补全
    """
    try:
        llm = OpenAI(
            model_name=model,
            temperature=0.7,
            max_tokens=200,
            request_timeout=60
        )
        
        # 构造 prompt
        prompt_str = HUMANEVAL_PROMPT_TEMPLATE.format(prompt=prompt)
        response = llm(prompt_str)
        completion = response.strip()
        
        # 提取代码块
        if "```python" in completion:
            start = completion.find("```python") + 9
            end = completion.find("```", start)
            if end != -1:
                completion = completion[start:end].strip()
            else:
                completion = completion[start:].strip()
        
        # 如果包含函数签名，去掉函数签名
        lines = completion.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # 找到函数签名，返回后面的函数体
                if i + 1 < len(lines):
                    completion = '\n'.join(lines[i+1:]).strip()
                break
        
        # 强制给所有行添加缩进
        lines = completion.strip().split('\n')
        if lines:
            # 移除所有行的前导空格，然后重新添加缩进
            cleaned_lines = []
            indent_level = 0  # 缩进级别：0=4空格，1=8空格，2=12空格，3=16空格
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if stripped_line:  # 跳过空行
                    if i == 0:
                        # 第一行：4个空格
                        cleaned_lines.append('    ' + stripped_line)
                        if stripped_line.endswith(':'):
                            indent_level += 1
                    else:
                        if stripped_line.startswith(('return ', 'break', 'continue', 'pass')):
                            # 简单语句：根据缩进级别
                            indent = '    ' * (indent_level + 1)
                            cleaned_lines.append(indent + stripped_line)
                            # 如果是return语句，可能需要减少缩进级别
                            if indent_level > 0 and stripped_line.startswith('return '):
                                indent_level -= 1
                        elif stripped_line.startswith(('for ', 'if ', 'while ', 'try:', 'except:', 'else:', 'elif ')):
                            # 控制流语句：根据缩进级别
                            indent = '    ' * (indent_level + 1)
                            cleaned_lines.append(indent + stripped_line)
                            if stripped_line.endswith(':'):
                                indent_level += 1
                        else:
                            # 其他语句：根据缩进级别
                            indent = '    ' * (indent_level + 1)
                            cleaned_lines.append(indent + stripped_line)
            return '\n'.join(cleaned_lines)
        
        return completion.strip()
        
    except Exception as e:
        print(f"LangChain API调用失败: {e}")
        return "    pass" 