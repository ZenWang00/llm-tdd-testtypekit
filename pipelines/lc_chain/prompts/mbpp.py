from langchain_core.prompts import PromptTemplate

MBPP_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["description", "test_list"],
    template="""You are a Python programmer. Write a COMPLETE function definition.

{description}

Test cases:
{test_list}

CRITICAL: Your output MUST start with 'def ' and be a complete function.

Output format:
def function_name(parameters):
    # function body
    return result

DO NOT output anything else. Start with 'def '.
"""
) 