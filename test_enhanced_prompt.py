import json
import sys
sys.path.append('pipelines/lc_chain')
from generator import generate_one_completion_langchain

# 测试用的prompt（选择有循环逻辑和字符串操作问题的题目）
test_prompts = [
    # HumanEval/0 - 循环逻辑问题
    """
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
    """,
    
    # HumanEval/6 - 字符串操作问题
    """
def parse_music(music_string: str) -> List[int]:
    \"\"\" Input to this function is a string representing musical notes in a major scale.
    From lowest to highest, notes are: C, D, E, F, G, A, B. Input may begin with any note.
    The notes should be returned as a list of integers corresponding to how many semitones
    higher than the base note. For example, if the base note is C, the notes C, D, E, F, G, A, B
    should be returned as [0, 2, 4, 5, 7, 9, 11]
    >>> parse_music('C D E F G A B')
    [0, 2, 4, 5, 7, 9, 11]
    \"\"\"
    """,
    
    # HumanEval/8 - 循环逻辑问题
    """
def sum_product(numbers: List[int]) -> Tuple[int, int]:
    \"\"\" Given a list of numbers, return the sum and product of all the numbers.
    >>> sum_product([1, 2, 3, 4])
    (10, 24)
    >>> sum_product([1, 1, 1])
    (3, 1)
    \"\"\"
    """
]

print("=== 测试增强后的Prompt ===")
print("改进内容:")
print("1. 添加了CRITICAL LOOP LOGIC RULES")
print("2. 添加了CRITICAL STRING OPERATION RULES")
print("3. 提供了3个具体的循环逻辑示例")

for i, prompt in enumerate(test_prompts):
    print(f"\n--- 测试 {i+1} ---")
    try:
        completion = generate_one_completion_langchain(prompt)
        print(f"生成的代码:\n{completion}")
        
        # 检查是否有循环逻辑问题
        lines = completion.split('\n')
        has_loop = any('for ' in line or 'while ' in line for line in lines)
        has_unconditional_return_in_loop = False
        
        if has_loop:
            for j, line in enumerate(lines):
                if 'for ' in line or 'while ' in line:
                    # 检查循环内是否有无条件返回
                    for k in range(j+1, len(lines)):
                        if lines[k].strip().startswith('return ') and not any('if ' in lines[k-1] for lines[k-1] in lines[:k]):
                            has_unconditional_return_in_loop = True
                            break
                    break
        
        # 检查字符串操作问题
        has_split = any('split' in line for line in lines)
        has_join = any('join' in line for line in lines)
        
        print(f"\n代码质量检查:")
        print(f"包含循环: {has_loop}")
        print(f"循环内无条件返回: {has_unconditional_return_in_loop}")
        print(f"包含split: {has_split}")
        print(f"包含join: {has_join}")
        
        if has_split and not has_join:
            print("⚠️  警告: 使用了split但没有join")
        if has_unconditional_return_in_loop:
            print("⚠️  警告: 循环内有无条件返回")
        
    except Exception as e:
        print(f"错误: {e}") 