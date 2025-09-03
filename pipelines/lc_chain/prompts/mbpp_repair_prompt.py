#!/usr/bin/env python3
"""
MBPP修复提示词模板

用于迭代修复过程中，向LLM提供详细的测试失败信息。
"""

REPAIR_PROMPT_TEMPLATE = """Fix the implementation to pass ALL tests.

Description:
{description}

Reference Implementation (use as the source of truth for signature and needed imports):
{reference_code}

Generated Tests (context):
{all_tests}

Failed Tests ({failed_count}) and Error Details:
{failed_tests}
{traceback}

Return requirements:
- Output only complete, runnable Python code
- Include any required imports (match the reference)
- Keep the exact function signature from the reference
- No explanations or comments, just code
"""


def build_repair_prompt(
    description: str,
    reference_code: str,
    all_tests: str,
    passed_tests: list,
    failed_tests: list,
    traceback: str
) -> str:
    """构建修复提示词（包含参考实现）"""
    
    # 格式化通过的测试
    passed_tests_formatted = ""
    for test in passed_tests:
        test_name = test.get('test_name', 'Unknown')
        assertion = test.get('assertion', 'Test passed')
        passed_tests_formatted += f"- {test_name}: {assertion}\n"
    
    # 格式化失败的测试
    failed_tests_formatted = ""
    for test in failed_tests:
        test_name = test.get('test_name', 'Unknown')
        assertion = test.get('assertion', 'Test failed')
        expected = test.get('expected', 'Unknown')
        actual = test.get('actual', 'Unknown')
        error_type = test.get('error_type', 'Unknown')
        error_message = test.get('error_message', 'Unknown')
        
        failed_tests_formatted += f"- {test_name}:\n"
        failed_tests_formatted += f"  Assertion: {assertion}\n"
        failed_tests_formatted += f"  Expected: {expected}\n"
        failed_tests_formatted += f"  Actual: {actual}\n"
        failed_tests_formatted += f"  Error: {error_type} - {error_message}\n\n"
    
    # 构建完整提示词
    prompt = REPAIR_PROMPT_TEMPLATE.format(
        description=description,
        reference_code=reference_code,
        all_tests=all_tests,
        passed_count=len(passed_tests),
        failed_count=len(failed_tests),
        passed_tests=passed_tests_formatted.strip(),
        failed_tests=failed_tests_formatted.strip(),
        traceback=traceback
    )
    
    return prompt


