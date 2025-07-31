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

CRITICAL CONDITIONAL LOGIC RULES:
- NEVER place a return statement immediately after an if statement without proper indentation
- Each if/elif/else block should have EXACTLY ONE return statement
- If you need multiple return statements, use separate if/elif/else blocks
- WRONG: if condition: return True; return False
- CORRECT: if condition: return True; else: return False
- For loops with conditions: use if/else inside the loop, or return after the loop
- NEVER place an unconditional return inside a loop unless you want to exit immediately

CRITICAL LOOP LOGIC RULES:
- NEVER place an unconditional return statement inside a loop unless you want to exit immediately
- For loops that process all items, place the return statement AFTER the loop completes
- Common pattern: collect results in a list/accumulator, then return after the loop

Your response:
"""
)