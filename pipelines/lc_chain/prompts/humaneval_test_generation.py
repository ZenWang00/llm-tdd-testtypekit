from langchain_core.prompts import PromptTemplate

HUMANEVAL_TEST_GENERATION_TEMPLATE = PromptTemplate(
    input_variables=["prompt", "canonical_solution"],
    template="""You are a test-driven development expert. Generate comprehensive unit tests for the following function.

Function Signature:
{prompt}

Reference Solution:
{canonical_solution}

Generate Python unit tests that:
1. Use the EXACT function name from the function signature above
2. Cover the main functionality described in the function
3. Include edge cases and boundary conditions
4. Are executable and well-structured
5. Use pytest format with clear assertions

IMPORTANT REQUIREMENTS:
- The function name in your tests MUST match the function name in the function signature exactly
- Write tests that would help guide the implementation
- Include both positive and negative test cases
- Test edge cases like empty inputs, invalid inputs, etc.
- Make test names descriptive of what they test

Return ONLY the test code in pytest format. Do not include any explanations or comments outside the test functions.

Example format:
def test_basic_functionality():
    # test code here

def test_edge_cases():
    # test code here
"""
)
