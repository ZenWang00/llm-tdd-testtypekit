from langchain_core.prompts import PromptTemplate

HUMANEVAL_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["prompt"],
    template="""You are a professional Python programmer. Given the following function signature, generate a complete function implementation.

Function signature:
{prompt}

Please return only the function body, without the function signature. If you return a code block, make sure it contains only the function body:

"""
)