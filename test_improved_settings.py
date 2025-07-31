import json
import sys
sys.path.append('pipelines/lc_chain')
from generator import generate_one_completion_langchain

# 测试用的prompt
test_prompt = """
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
    """

print("=== 测试改进后的设置 ===")
print("temperature: 0.2 (降低，提高确定性)")
print("max_tokens: 400 (增加，给LLM更多思考空间)")

try:
    completion = generate_one_completion_langchain(test_prompt)
    print(f"\n生成的代码:\n{completion}")
    
    # 检查代码质量
    lines = completion.split('\n')
    print(f"\n代码统计:")
    print(f"行数: {len(lines)}")
    print(f"字符数: {len(completion)}")
    print(f"是否有return: {'return' in completion}")
    print(f"是否有if: {'if ' in completion}")
    print(f"是否有for: {'for ' in completion}")
    
except Exception as e:
    print(f"错误: {e}") 