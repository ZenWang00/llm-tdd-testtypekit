from langchain_core.prompts import PromptTemplate

MBPP_TDD_IMPLEMENTATION_TEMPLATE = PromptTemplate(
    input_variables=["description", "generated_tests", "reference_code"],
    template="""You are a Python programmer. Write a function that passes all the given tests.

Problem Description:
{description}

Reference Implementation:
{reference_code}

Generated Tests:
{generated_tests}

Write a complete function that passes ALL the above tests. Your implementation must:
1. Use the SAME function name as in the reference code
2. Start with 'def ' and include the full function definition
3. Pass all the provided test cases
4. Handle all edge cases mentioned in the tests
5. Be efficient and well-structured
6. Follow Python best practices

IMPORTANT: Your function must be able to run the tests successfully. Make sure:
- The function name matches what the tests expect (use the name from reference code)
- The function signature matches the test calls
- The function handles all the test scenarios

Return ONLY the function code, no explanations or comments outside the function definition."""
)
