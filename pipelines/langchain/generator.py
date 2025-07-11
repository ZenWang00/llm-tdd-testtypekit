import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from .prompts.humaneval import HUMANEVAL_PROMPT_TEMPLATE

def generate_one_completion_langchain(prompt, model="gpt-4o-mini"):
    """
    使用LangChain生成单个代码补全
    """
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            max_tokens=200,
            timeout=60
        )
        
        chain = (
            {"prompt": RunnablePassthrough()} 
            | HUMANEVAL_PROMPT_TEMPLATE 
            | llm 
            | StrOutputParser()
        )
        
        response = chain.invoke({"prompt": prompt})
        completion = response.strip()
        
        if "```python" in completion:
            start = completion.find("```python") + 9
            end = completion.find("```", start)
            if end != -1:
                code_block = completion[start:end].strip()
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
        print(f"LangChain API调用失败: {e}")
        return "    pass" 