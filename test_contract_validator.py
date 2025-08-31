#!/usr/bin/env python3
"""
Test Contract Validator for TDD-generated tests

This module validates that generated tests comply with pytest conventions and TDD requirements.
"""

import re
import ast
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class ContractValidationResult:
    """契约验证结果"""
    is_compliant: bool
    function_name_compliant: bool
    assertion_count_compliant: bool
    boundary_test_present: bool
    exception_test_present: bool
    pytest_format_compliant: bool
    details: Dict[str, Any]
    score: float  # 0.0 to 1.0


class TestContractValidator:
    """测试契约验证器"""
    
    def __init__(self, min_assertions: int = 3):
        self.min_assertions = min_assertions
        
    def validate_test_code(self, test_code: str) -> ContractValidationResult:
        """
        验证测试代码是否符合契约要求
        
        Args:
            test_code: 要验证的测试代码字符串
            
        Returns:
            ContractValidationResult: 验证结果
        """
        try:
            # 解析代码
            tree = ast.parse(test_code)
            
            # 执行各项检查
            function_name_check = self._check_function_names(tree)
            assertion_check = self._check_assertion_count(tree)
            boundary_check = self._check_boundary_tests(tree)
            exception_check = self._check_exception_tests(tree)
            pytest_format_check = self._check_pytest_format(tree)
            
            # 计算合规性
            checks = [
                function_name_check,
                assertion_check,
                boundary_check,
                exception_check,
                pytest_format_check
            ]
            
            compliant_checks = sum(checks)
            total_checks = len(checks)
            compliance_rate = compliant_checks / total_checks
            
            # 构建详细结果
            details = {
                'function_names': self._extract_function_names(tree),
                'assertion_count': self._count_assertions(tree),
                'boundary_test_details': self._analyze_boundary_tests(tree),
                'exception_test_details': self._analyze_exception_tests(tree),
                'pytest_format_details': self._analyze_pytest_format(tree)
            }
            
            return ContractValidationResult(
                is_compliant=compliance_rate >= 0.8,  # 80%以上算合规
                function_name_compliant=function_name_check,
                assertion_count_compliant=assertion_check,
                boundary_test_present=boundary_check,
                exception_test_present=exception_check,
                pytest_format_compliant=pytest_format_check,
                details=details,
                score=compliance_rate
            )
            
        except SyntaxError as e:
            # 代码语法错误
            return ContractValidationResult(
                is_compliant=False,
                function_name_compliant=False,
                assertion_count_compliant=False,
                boundary_test_present=False,
                exception_test_present=False,
                pytest_format_compliant=False,
                details={'error': f'Syntax error: {str(e)}'},
                score=0.0
            )
        except Exception as e:
            # 其他错误
            return ContractValidationResult(
                is_compliant=False,
                function_name_compliant=False,
                assertion_count_compliant=False,
                boundary_test_present=False,
                exception_test_present=False,
                pytest_format_compliant=False,
                details={'error': f'Validation error: {str(e)}'},
                score=0.0
            )
    
    def _check_function_names(self, tree: ast.AST) -> bool:
        """检查函数名是否符合pytest规范"""
        function_names = self._extract_function_names(tree)
        if not function_names:
            return False
            
        # 检查所有函数名都以test_开头并使用snake_case
        for name in function_names:
            if not name.startswith('test_'):
                return False
            if not self._is_snake_case(name):
                return False
                
        return True
    
    def _check_assertion_count(self, tree: ast.AST) -> bool:
        """检查断言数量是否满足要求"""
        assertion_count = self._count_assertions(tree)
        return assertion_count >= self.min_assertions
    
    def _check_boundary_tests(self, tree: ast.AST) -> bool:
        """检查是否包含边界测试"""
        boundary_details = self._analyze_boundary_tests(tree)
        return boundary_details['has_boundary_tests']
    
    def _check_exception_tests(self, tree: ast.AST) -> bool:
        """检查是否包含异常测试"""
        exception_details = self._analyze_exception_tests(tree)
        return exception_details['has_exception_tests']
    
    def _check_pytest_format(self, tree: ast.AST) -> bool:
        """检查pytest格式合规性"""
        format_details = self._analyze_pytest_format(tree)
        return format_details['is_pytest_compliant']
    
    def _extract_function_names(self, tree: ast.AST) -> List[str]:
        """提取所有函数名"""
        function_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)
        return function_names
    
    def _count_assertions(self, tree: ast.AST) -> int:
        """统计断言数量"""
        assertion_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                assertion_count += 1
        return assertion_count
    
    def _is_snake_case(self, name: str) -> bool:
        """检查是否为snake_case格式"""
        # 移除test_前缀
        if name.startswith('test_'):
            name = name[5:]
        
        # 检查是否为snake_case
        if not name:
            return True  # test_ 本身是有效的
            
        # 不能以数字开头，只能包含字母、数字和下划线
        if name[0].isdigit():
            return False
            
        # 检查格式：小写字母、数字、下划线，单词间用下划线分隔
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name))
    
    def _analyze_boundary_tests(self, tree: ast.AST) -> Dict[str, Any]:
        """分析边界测试"""
        boundary_patterns = {
            'empty_list': ['[]', 'list()'],
            'empty_string': ['""', "''", 'str()'],
            'empty_dict': ['{}', 'dict()'],
            'zero': ['0', '0.0'],
            'negative_one': ['-1', '-1.0'],
            'none': ['None'],
            'max_values': ['float("inf")', 'float("-inf")', 'sys.maxsize'],
            'length_checks': ['len(', 'len() == 0', 'len() == 1']
        }
        
        try:
            code_str = ast.unparse(tree)
        except AttributeError:
            code_str = str(tree)
        
        boundary_detected = False
        boundary_types = []
        
        for boundary_type, patterns in boundary_patterns.items():
            for pattern in patterns:
                if pattern in code_str:
                    boundary_detected = True
                    boundary_types.append(boundary_type)
                    break
        
        return {
            'has_boundary_tests': boundary_detected,
            'boundary_types': list(set(boundary_types)),
            'boundary_count': len(set(boundary_types))
        }
    
    def _analyze_exception_tests(self, tree: ast.AST) -> Dict[str, Any]:
        """分析异常测试"""
        exception_patterns = {
            'pytest_raises': 'pytest.raises(',
            'try_except': 'try:',
            'assert_raises': 'assertRaises',
            'exception_keywords': ['raise', 'Exception', 'Error', 'ValueError', 'TypeError']
        }
        
        try:
            code_str = ast.unparse(tree)
        except AttributeError:
            code_str = str(tree)
        
        exception_detected = False
        exception_types = []
        
        for exception_type, pattern in exception_patterns.items():
            if isinstance(pattern, str):
                if pattern in code_str:
                    exception_detected = True
                    exception_types.append(exception_type)
            elif isinstance(pattern, list):
                for p in pattern:
                    if p in code_str:
                        exception_detected = True
                        exception_types.append(exception_type)
                        break
        
        return {
            'has_exception_tests': exception_detected,
            'exception_types': exception_types,
            'exception_count': len(exception_types)
        }
    
    def _analyze_pytest_format(self, tree: ast.AST) -> Dict[str, Any]:
        """分析pytest格式合规性"""
        function_names = self._extract_function_names(tree)
        assertion_count = self._count_assertions(tree)
        
        # 检查基本pytest要求
        has_test_functions = len(function_names) > 0
        all_start_with_test = all(name.startswith('test_') for name in function_names)
        has_assertions = assertion_count > 0
        
        # 检查函数结构
        function_structure_ok = True
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数是否有文档字符串或注释
                if not node.body:
                    function_structure_ok = False
                    break
        
        is_pytest_compliant = (
            has_test_functions and 
            all_start_with_test and 
            has_assertions and 
            function_structure_ok
        )
        
        return {
            'is_pytest_compliant': is_pytest_compliant,
            'has_test_functions': has_test_functions,
            'all_start_with_test': all_start_with_test,
            'has_assertions': has_assertions,
            'function_structure_ok': function_structure_ok
        }


def validate_multiple_tests(test_codes: List[str], min_assertions: int = 3) -> List[ContractValidationResult]:
    """
    批量验证多个测试代码
    
    Args:
        test_codes: 测试代码列表
        min_assertions: 最小断言数量要求
        
    Returns:
        List[ContractValidationResult]: 验证结果列表
    """
    validator = TestContractValidator(min_assertions)
    results = []
    
    for i, test_code in enumerate(test_codes):
        print(f"Validating test {i+1}/{len(test_codes)}...")
        result = validator.validate_test_code(test_code)
        results.append(result)
    
    return results


def print_validation_summary(results: List[ContractValidationResult]) -> None:
    """打印验证结果摘要"""
    if not results:
        print("No validation results to display.")
        return
    
    total_tests = len(results)
    compliant_tests = sum(1 for r in results if r.is_compliant)
    avg_score = sum(r.score for r in results) / total_tests
    
    print("\n" + "="*60)
    print("TEST CONTRACT VALIDATION SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Compliant Tests: {compliant_tests} ({compliant_tests/total_tests*100:.1f}%)")
    print(f"Average Score: {avg_score:.2f}")
    print()
    
    # 各项指标的统计
    metrics = {
        'Function Names': 'function_name_compliant',
        'Assertion Count': 'assertion_count_compliant', 
        'Boundary Tests': 'boundary_test_present',
        'Exception Tests': 'exception_test_present',
        'Pytest Format': 'pytest_format_compliant'
    }
    
    print("Compliance by Category:")
    print("-" * 40)
    for metric_name, attr_name in metrics.items():
        compliant_count = sum(1 for r in results if getattr(r, attr_name))
        percentage = compliant_count / total_tests * 100
        print(f"{metric_name:20} {compliant_count:3d}/{total_tests} ({percentage:5.1f}%)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # 测试示例
    sample_test = '''
def test_basic_functionality():
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, 1) == 0

def test_edge_cases():
    assert add([], []) == []
    assert add([1], []) == [1]
    assert add([], [1]) == [1]

def test_exceptions():
    with pytest.raises(TypeError):
        add("string", 1)
    with pytest.raises(ValueError):
        add(None, 1)
'''
    
    print("Testing Contract Validator...")
    validator = TestContractValidator(min_assertions=3)
    result = validator.validate_test_code(sample_test)
    
    print(f"Compliance: {result.is_compliant}")
    print(f"Score: {result.score:.2f}")
    print(f"Details: {result.details}")
