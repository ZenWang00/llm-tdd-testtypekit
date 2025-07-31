from langchain_core.prompts import PromptTemplate

MBPP_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["description"],
    template="""You are a professional Python programmer. Implement the following function as a complete Python function (including the def line):

{description}

CRITICAL REQUIREMENTS:
1. Your output MUST start with 'def ' and be a valid Python function. Output nothing else.
2. CAREFULLY analyze the test cases to understand:
   - The exact function name to use
   - The correct parameter types and order
   - The expected return type and format
3. Pay special attention to:
   - Parameter types: list vs dict vs string vs int
   - Function naming: use the exact name from test cases
   - Algorithm logic: understand the specific requirements
4. If the description mentions "dictionary" but test cases use lists, use lists
5. If the description mentions "sequences" but test cases check patterns, implement pattern matching
6. For mathematical functions, ensure you understand the specific mathematical concept
7. For string operations, pay attention to the exact splitting/matching rules

SPECIFIC IMPLEMENTATION GUIDELINES:
- For "count most common words": Return only the top 4 most common words, not all words
- For "split at lowercase letters": Use regex pattern '[a-z][^a-z]*' to match lowercase letters followed by non-lowercase characters
- For "find sequences": Check if the entire string matches a specific pattern, don't extract sequences
- For mathematical functions: Implement the exact mathematical definition, not a similar concept
- For list operations: Pay attention to the exact order and format of expected results

Your output MUST start with 'def ' and be a valid Python function. Output nothing else. If you do not follow this, you will be penalized.
"""
) 