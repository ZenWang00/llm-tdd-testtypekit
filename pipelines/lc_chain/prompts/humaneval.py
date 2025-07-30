from langchain_core.prompts import PromptTemplate

HUMANEVAL_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["prompt"],
    template="""You are a professional Python programmer. Given the following function signature, generate a complete function implementation.

Function signature:
{prompt}

IMPORTANT: Return ONLY the function body (the code inside the function), NOT the function signature.

CRITICAL FORMATTING REQUIREMENTS:
- Every single line must start with exactly 4 spaces (no more, no less)
- Do not include the function signature (def line)
- Do not include any comments, explanations, or code block markers
- Do not include empty lines

Example of correct format:
    if condition:
        result = some_calculation()
        return result
    return default_value

Your response:
"""
)