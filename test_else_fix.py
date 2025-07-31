import json
import sys
sys.path.append('pipelines/lc_chain')
from generator import generate_one_completion_langchain

# 测试用的prompt（选择有else问题的题目）
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

print("=== 测试else问题修复 ===")
print("改进内容:")
print("1. Prompt中增加了CRITICAL ELSE/ELIF RULES")
print("2. 后处理逻辑分离了else/elif的处理")

try:
    completion = generate_one_completion_langchain(test_prompt)
    print(f"\n生成的代码:\n{completion}")
    
    # 检查是否有else问题
    lines = completion.split('\n')
    if_count = 0
    else_count = 0
    elif_count = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('if '):
            if_count += 1
        elif stripped.startswith('else:'):
            else_count += 1
        elif stripped.startswith('elif '):
            elif_count += 1
    
    print(f"\n控制流统计:")
    print(f"if语句: {if_count}")
    print(f"else语句: {else_count}")
    print(f"elif语句: {elif_count}")
    
    # 检查else/elif是否与if匹配
    if else_count + elif_count > if_count:
        print("⚠️  警告: else/elif数量超过if数量，可能存在结构问题")
    else:
        print("✅ else/elif数量合理")
        
except Exception as e:
    print(f"错误: {e}") 