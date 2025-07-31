import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from .prompts.humaneval import HUMANEVAL_PROMPT_TEMPLATE

def generate_one_completion_langchain(prompt, model="gpt-4o-mini", prompt_template=None):
    """
    使用LangChain生成单个代码补全
    """
    try:
        llm = OpenAI(
            model_name=model,
            temperature=0.2,  # 降低temperature，提高确定性
            max_tokens=400,   # 增加token限制，给LLM更多思考空间
            request_timeout=60
        )
        
        # 使用传入的prompt_template，如果没有则使用默认的HUMANEVAL模板
        if prompt_template is None:
            prompt_template = HUMANEVAL_PROMPT_TEMPLATE
        
        # 构造 prompt
        if hasattr(prompt_template, 'input_variables'):
            # 根据模板的input_variables决定如何格式化
            if 'prompt' in prompt_template.input_variables:
                prompt_str = prompt_template.format(prompt=prompt)
            elif 'description' in prompt_template.input_variables:
                prompt_str = prompt_template.format(description=prompt)
            else:
                # 默认使用prompt参数
                prompt_str = prompt_template.format(prompt=prompt)
        else:
            prompt_str = prompt_template.format(prompt=prompt)
            
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
        elif "```" in completion:
            start = completion.find("```") + 3
            end = completion.find("```", start)
            if end != -1:
                completion = completion[start:end].strip()
            else:
                completion = completion[start:].strip()
        
        # 如果包含函数签名，去掉函数签名（仅对HumanEval，MBPP需要保留def行）
        if prompt_template == HUMANEVAL_PROMPT_TEMPLATE:
        lines = completion.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # 找到函数签名，返回后面的函数体
                if i + 1 < len(lines):
                        completion = '\n'.join(lines[i+1:]).strip()
                    break
        
        # 强制给所有行添加缩进（仅对HumanEval，MBPP保持原样）
        if prompt_template == HUMANEVAL_PROMPT_TEMPLATE:
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
                            elif stripped_line.startswith(('for ', 'if ', 'while ', 'try:', 'except:')):
                                # 控制流语句：根据缩进级别
                                indent = '    ' * (indent_level + 1)
                                cleaned_lines.append(indent + stripped_line)
                                if stripped_line.endswith(':'):
                                    indent_level += 1
                            elif stripped_line.startswith(('else:', 'elif ')):
                                # else/elif语句：与对应的if对齐（相同缩进级别）
                                indent = '    ' * (indent_level + 1)
                                cleaned_lines.append(indent + stripped_line)
                                if stripped_line.endswith(':'):
                                    indent_level += 1
                            else:
                                # 其他语句：根据缩进级别
                                indent = '    ' * (indent_level + 1)
                                cleaned_lines.append(indent + stripped_line)
                
                processed_code = '\n'.join(cleaned_lines)
                
                # 添加语法检查和修复
                processed_code = _fix_syntax_issues(processed_code)
                
                return processed_code
        
        return completion.strip()
        
    except Exception as e:
        print(f"LangChain API调用失败: {e}")
        return "    pass" 

def _fix_syntax_issues(code):
        """修复常见的语法问题 - 递归处理控制流缩进"""
        import ast
        
        # 首先检查语法是否正确
        try:
            # 将代码包装在一个函数中以便AST解析
            wrapped_code = f"def test_function():\n{code}"
            ast.parse(wrapped_code)
            return code  # 语法正确，直接返回
        except SyntaxError:
            # 语法错误，尝试修复
            pass
        
        lines = code.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            
            # 跳过空行
            if not stripped_line:
                fixed_lines.append(line)
                i += 1
                continue
            
            # 递归修复控制流语句的缩进
            if stripped_line.startswith(('elif ', 'else:', 'except:', 'finally:')):
                # 找到对应的控制流语句（if/for/while/try）
                control_indent = _find_control_statement_indent(lines, i)
                if control_indent is not None:
                    # 修正缩进
                    fixed_line = ' ' * control_indent + stripped_line
                    fixed_lines.append(fixed_line)
                    i += 1
                    continue
            
            # 修复if/for/while后缺少缩进块的问题
            if stripped_line.endswith(':') and stripped_line.startswith(('if ', 'for ', 'while ', 'try:', 'except:', 'else:', 'elif ')):
                fixed_lines.append(line)
                i += 1
                
                # 检查下一行是否有缩进
                if i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    current_indent = len(line) - len(line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # 如果下一行没有缩进或缩进不够，需要处理
                    if next_stripped and next_indent <= current_indent:
                        # 如果下一行不是控制流语句，需要添加缩进
                        if not next_stripped.startswith(('if ', 'for ', 'while ', 'try:', 'except:', 'else:', 'elif ', 'return ', 'break', 'continue', 'pass')):
                            # 给下一行添加正确的缩进
                            fixed_next_line = ' ' * (current_indent + 4) + next_stripped
                            fixed_lines.append(fixed_next_line)
                            i += 1
                            continue
                        else:
                            # 下一行是控制流语句，需要添加pass
                            pass_line = ' ' * (current_indent + 4) + 'pass'
                            fixed_lines.append(pass_line)
                            continue
                    # 如果下一行缩进等于当前行，但当前行是控制流语句，需要给下一行增加缩进
                    elif next_stripped and next_indent == current_indent and stripped_line.endswith(':'):
                        # 给下一行添加正确的缩进
                        fixed_next_line = ' ' * (current_indent + 4) + next_stripped
                        fixed_lines.append(fixed_next_line)
                        i += 1
                        continue
                    # 如果下一行缩进大于当前行，但当前行是控制流语句，检查是否需要进一步缩进
                    elif next_stripped and next_indent > current_indent and stripped_line.endswith(':'):
                        # 检查下一行是否应该在当前控制流块内
                        expected_indent = current_indent + 4
                        if next_indent != expected_indent:
                            # 给下一行添加正确的缩进
                            fixed_next_line = ' ' * expected_indent + next_stripped
                            fixed_lines.append(fixed_next_line)
                            i += 1
                            continue
                
                continue
            
            # 修复括号不匹配问题
            if '[' in stripped_line and stripped_line.count('[') > stripped_line.count(']'):
                # 检查是否是列表推导式
                if 'for' in stripped_line and 'in' in stripped_line:
                    # 尝试修复列表推导式
                    if not stripped_line.endswith(']'):
                        fixed_line = line.rstrip() + ']'
                        fixed_lines.append(fixed_line)
                        i += 1
                        continue
            
            # 其他情况，保持原样
            fixed_lines.append(line)
            i += 1
        
        fixed_code = '\n'.join(fixed_lines)
        
        # 再次检查语法
        try:
            wrapped_fixed_code = f"def test_function():\n{fixed_code}"
            ast.parse(wrapped_fixed_code)
            return fixed_code  # 修复成功
        except SyntaxError:
            return code  # 修复失败，返回原始代码

def _find_control_statement_indent(lines, current_index):
    """递归查找控制流语句的缩进级别"""
    # 控制流语句关键字
    control_keywords = ('if ', 'for ', 'while ', 'try:')
    
    # 从当前行向上查找
    for i in range(current_index - 1, -1, -1):
        line = lines[i]
        stripped = line.strip()
        
        # 跳过空行
        if not stripped:
            continue
        
        # 如果找到控制流语句
        if any(stripped.startswith(keyword) for keyword in control_keywords):
            return len(line) - len(line.lstrip())
        
        # 如果遇到其他控制流语句，继续向上查找
        if stripped.startswith(('elif ', 'else:', 'except:', 'finally:')):
            continue
    
    return None 