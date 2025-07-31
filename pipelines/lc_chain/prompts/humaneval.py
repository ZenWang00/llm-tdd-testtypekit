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
- All nested statements must strictly follow Python indentation rules:
  - Each new block must be indented exactly 4 spaces deeper than its parent.
  - Sibling blocks (such as elif/else/except/finally) must align with their corresponding parent block.
  - Do not over-indent or under-indent any line.
  - Every control flow statement must be followed by a properly indented code block (never leave a block empty; use 'pass' if needed).

INDENTATION RULES FOR NESTED LOGIC:
- Base level: 4 spaces (all lines start here)
- Inside if/for/while/try blocks: 8 spaces (4 + 4)
- Inside nested if/for/while/try blocks: 12 spaces (4 + 4 + 4)
- elif/else/except/finally must align with their corresponding if/for/while/try
- Every control structure (if/for/while/try) must have at least one indented line after it

CRITICAL ELSE/ELIF RULES:
- else: and elif: must ALWAYS have a corresponding if: statement above them
- else: and elif: must be at the SAME indentation level as their corresponding if:
- NEVER place else: or elif: without a matching if: statement
- Each if: block must be complete before starting elif: or else:

Your response:
"""
)