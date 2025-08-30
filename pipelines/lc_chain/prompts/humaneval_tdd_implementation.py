from langchain_core.prompts import PromptTemplate

HUMANEVAL_TDD_IMPLEMENTATION_TEMPLATE = PromptTemplate(
    input_variables=["prompt", "generated_tests"],
    template="""You are a Python programmer. Write a function body that passes all the given tests.

Function Signature:
{prompt}

Generated Tests:
{generated_tests}

Write a function body that passes ALL the above tests. Your implementation must:
1. Use the EXACT function name from the function signature above
2. Return ONLY the function body (no def line), starting with proper indentation
3. Pass all the provided test cases
4. Handle all edge cases mentioned in the tests
5. Be efficient and well-structured
6. Follow Python best practices

IMPORTANT: Your function body must be able to run the tests successfully. Make sure:
- The function name matches what the tests expect (use the name from function signature)
- The function body starts with proper indentation (4 spaces)
- The function handles all the test scenarios
- Return ONLY the function body, NOT the complete function definition

Return ONLY the function body code, no explanations or comments outside the function body."""
)
