import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from .prompts.humaneval import HUMANEVAL_PROMPT_TEMPLATE
from .prompts.mbpp_test_generation import MBPP_TEST_GENERATION_TEMPLATE
from .prompts.mbpp_tdd_implementation import MBPP_TDD_IMPLEMENTATION_TEMPLATE
from .prompts.humaneval_test_generation import HUMANEVAL_TEST_GENERATION_TEMPLATE
from .prompts.humaneval_tdd_implementation import HUMANEVAL_TDD_IMPLEMENTATION_TEMPLATE

def generate_one_completion_langchain(prompt, model="gpt-4o-mini", prompt_template=None, **kwargs):
    """
    使用LangChain生成单个代码补全
    """
    try:
        llm = OpenAI(
            model_name=model,
            temperature=0.0,  # 设置为0.0，最大化确定性
            max_tokens=600,   # 增加token限制，给LLM更多思考空间
            request_timeout=60
        )
        
        # 使用传入的prompt_template，如果没有则使用默认的HUMANEVAL模板
        if prompt_template is None:
            prompt_template = HUMANEVAL_PROMPT_TEMPLATE
        
        # 构造 prompt
        if isinstance(prompt_template, str):
            # 如果传入的是已经格式化的字符串，直接使用
            prompt_str = prompt_template
        elif hasattr(prompt_template, 'input_variables'):
            # 根据模板的input_variables决定如何格式化
            if 'prompt' in prompt_template.input_variables and 'canonical_solution' in prompt_template.input_variables:
                # HumanEval测试生成模板需要prompt和canonical_solution
                canonical_solution = kwargs.get('canonical_solution', '')
                prompt_str = prompt_template.format(prompt=prompt, canonical_solution=canonical_solution)
            elif 'prompt' in prompt_template.input_variables and 'generated_tests' in prompt_template.input_variables:
                # HumanEval TDD实现模板需要prompt和generated_tests
                generated_tests = kwargs.get('generated_tests', '')
                prompt_str = prompt_template.format(prompt=prompt, generated_tests=generated_tests)
            elif 'prompt' in prompt_template.input_variables:
                prompt_str = prompt_template.format(prompt=prompt)
            elif 'description' in prompt_template.input_variables and 'test_list' in prompt_template.input_variables:
                # MBPP模板需要description和test_list
                test_list = kwargs.get('test_list', '')
                prompt_str = prompt_template.format(description=prompt, test_list=test_list)
            elif 'description' in prompt_template.input_variables and 'generated_tests' in prompt_template.input_variables and 'reference_code' in prompt_template.input_variables:
                # TDD实现模板需要description、generated_tests和reference_code
                generated_tests = kwargs.get('generated_tests', '')
                reference_code = kwargs.get('reference_code', '')
                prompt_str = prompt_template.format(description=prompt, generated_tests=generated_tests, reference_code=reference_code)
            elif 'description' in prompt_template.input_variables and 'reference_code' in prompt_template.input_variables:
                # TDD测试生成模板需要description和reference_code
                reference_code = kwargs.get('reference_code', '')
                prompt_str = prompt_template.format(description=prompt, reference_code=reference_code)
            elif 'description' in prompt_template.input_variables and 'generated_tests' in prompt_template.input_variables:
                # TDD实现模板需要description和generated_tests
                generated_tests = kwargs.get('generated_tests', '')
                prompt_str = prompt_template.format(description=prompt, generated_tests=generated_tests)
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
        # 通过检查prompt内容来区分HumanEval和MBPP
        if isinstance(prompt_template, str):
            # 如果是字符串，检查是否包含HumanEval的特征
            if "Function signature:" in prompt_template and "Return ONLY the function body" in prompt_template:
                # 这是HumanEval，需要去掉def行
                lines = completion.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        # 找到函数签名，返回后面的函数体
                        if i + 1 < len(lines):
                            completion = '\n'.join(lines[i+1:]).strip()
                        break
        elif prompt_template == HUMANEVAL_PROMPT_TEMPLATE:
            # 直接比较对象的情况
            lines = completion.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    # 找到函数签名，返回后面的函数体
                    if i + 1 < len(lines):
                        completion = '\n'.join(lines[i+1:]).strip()
                    break
        
        return completion.strip()
        
    except Exception as e:
        print(f"LangChain API调用失败: {e}")
        return "    pass"

def generate_tests_for_mbpp(description, reference_code, model="gpt-4o-mini"):
    """阶段1：为MBPP问题生成测试用例"""
    return generate_one_completion_langchain(
        description, 
        model, 
        MBPP_TEST_GENERATION_TEMPLATE,
        reference_code=reference_code
    )

def generate_implementation_with_tests(description, generated_tests, reference_code, model="gpt-4o-mini"):
    """阶段2：根据生成的测试生成实现"""
    return generate_one_completion_langchain(
        description, 
        model, 
        MBPP_TDD_IMPLEMENTATION_TEMPLATE,
        generated_tests=generated_tests,
        reference_code=reference_code
    )

def generate_tests_for_humaneval(prompt, canonical_solution, model="gpt-4o-mini"):
    """阶段1：为HumanEval生成测试用例"""
    return generate_one_completion_langchain(
        prompt, 
        model, 
        HUMANEVAL_TEST_GENERATION_TEMPLATE,
        canonical_solution=canonical_solution
    )

def generate_implementation_with_tests_humaneval(prompt, generated_tests, model="gpt-4o-mini"):
    """阶段2：根据测试生成HumanEval实现"""
    return generate_one_completion_langchain(
        prompt, 
        model, 
        HUMANEVAL_TDD_IMPLEMENTATION_TEMPLATE,
        generated_tests=generated_tests
    ) 

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