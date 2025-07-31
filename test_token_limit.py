import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from pipelines.lc_chain.prompts.humaneval import HUMANEVAL_PROMPT_TEMPLATE

def test_different_settings():
    """测试不同的token限制和temperature设置"""
    
    # 测试用的prompt（选择一个中等复杂度的题目）
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
    
    # 不同的配置组合
    configs = [
        {"max_tokens": 200, "temperature": 0.7, "name": "当前设置"},
        {"max_tokens": 400, "temperature": 0.7, "name": "增加token限制"},
        {"max_tokens": 200, "temperature": 0.2, "name": "降低temperature"},
        {"max_tokens": 400, "temperature": 0.2, "name": "最佳设置"},
        {"max_tokens": 600, "temperature": 0.1, "name": "高token低temperature"},
    ]
    
    for config in configs:
        print(f"\n=== 测试配置: {config['name']} ===")
        print(f"max_tokens: {config['max_tokens']}, temperature: {config['temperature']}")
        
        try:
            llm = OpenAI(
                model_name="gpt-4o-mini",
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                request_timeout=60
            )
            
            prompt_str = HUMANEVAL_PROMPT_TEMPLATE.format(prompt=test_prompt)
            response = llm(prompt_str)
            
            # 计算token数量（粗略估算）
            token_count = len(response.split())
            print(f"生成代码长度: {len(response)} 字符, 约 {token_count} 个token")
            print(f"代码内容:\n{response}")
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    test_different_settings() 