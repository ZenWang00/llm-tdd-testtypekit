from langchain_core.prompts import PromptTemplate

HUMANEVAL_TEST_GENERATION_TEMPLATE = PromptTemplate(
    input_variables=["prompt", "canonical_solution"],
    template="""You are a test-driven development expert. Generate comprehensive unit tests for the following function.

Function Signature:
{prompt}

Reference Solution:
{canonical_solution}

Generate Python unit tests that strictly follow pytest conventions:

1. Use the EXACT function name from the function signature above
2. Cover the main functionality described in the function
3. Include edge cases and boundary conditions
4. Are executable and well-structured
5. Follow pytest naming conventions and best practices

PYTEST REQUIREMENTS:
- Function names MUST start with "test_" and use snake_case
- Use descriptive test names that clearly indicate what is being tested
- Each test function should test ONE specific behavior or scenario
- Use pytest.raises() for testing exceptions
- Use pytest.approx() for floating point comparisons
- Use clear, specific assertions with meaningful error messages
- Group related tests logically (basic, edge cases, exceptions, etc.)

TEST COVERAGE REQUIREMENTS:
- The function name in your tests MUST match the function name in the function signature exactly
- Include at least 3-5 test cases covering different scenarios
- Include at least ONE boundary test (empty inputs, edge values, limits)
- Include at least ONE exception test (invalid inputs, error conditions)
- Include positive test cases (normal operation)
- Include negative test cases (edge cases, invalid inputs)

Return ONLY the test code in pytest format. Do not include any explanations or comments outside the test functions.

Example format:
def test_basic_functionality():
    # test code here

def test_edge_cases():
    # test code here

def test_exceptions():
    # test code here
"""
)
