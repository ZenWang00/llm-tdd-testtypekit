#!/usr/bin/env python3
"""
启发式检查器 - 智能特征识别

这个模块使用启发式方法智能识别测试代码的特征，包括异常测试、边界测试、输入多样性等。
"""

import re
import ast
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict


@dataclass
class HeuristicAnalysisResult:
    """启发式分析结果"""
    # 异常测试特征
    exception_patterns: Dict[str, Any]
    exception_score: float
    
    # 边界测试特征
    boundary_patterns: Dict[str, Any]
    boundary_score: float
    
    # 输入多样性特征
    input_diversity: Dict[str, Any]
    diversity_score: float
    
    # 测试模式特征
    test_patterns: Dict[str, Any]
    pattern_score: float
    
    # 代码质量特征
    code_quality: Dict[str, Any]
    quality_score: float
    
    # 综合评分
    overall_score: float
    insights: List[str]


class TestHeuristicChecker:
    """测试启发式检查器"""
    
    def __init__(self):
        # 异常测试模式
        self.exception_patterns = {
            'pytest_raises': {
                'patterns': [
                    r'pytest\.raises\([^)]+\)',
                    r'pytest\.raises\([^)]+,\s*[^)]+\)'
                ],
                'weight': 0.4
            },
            'try_except': {
                'patterns': [
                    r'try\s*:',
                    r'except\s+[^:]+:',
                    r'except\s*:'
                ],
                'weight': 0.3
            },
            'assert_raises': {
                'patterns': [
                    r'assertRaises\([^)]+\)',
                    r'assert_raises\([^)]+\)'
                ],
                'weight': 0.2
            },
            'exception_keywords': {
                'patterns': [
                    r'raise\s+[^#\n]+',
                    r'ValueError',
                    r'TypeError',
                    r'IndexError',
                    r'KeyError',
                    r'AttributeError',
                    r'RuntimeError',
                    r'AssertionError'
                ],
                'weight': 0.1
            }
        }
        
        # 边界测试模式
        self.boundary_patterns = {
            'empty_collections': {
                'patterns': [
                    r'\[\s*\]',  # []
                    r'{\s*}',     # {}
                    r'""',        # ""
                    r"''",        # ''
                    r'list\(\)',  # list()
                    r'dict\(\)',  # dict()
                    r'set\(\)',   # set()
                    r'tuple\(\)'  # tuple()
                ],
                'weight': 0.25
            },
            'zero_values': {
                'patterns': [
                    r'\b0\b',
                    r'\b0\.0\b',
                    r'\b0L\b'
                ],
                'weight': 0.2
            },
            'negative_values': {
                'patterns': [
                    r'\b-1\b',
                    r'\b-0\.1\b',
                    r'\b-999\b'
                ],
                'weight': 0.2
            },
            'extreme_values': {
                'patterns': [
                    r'float\("inf"\)',
                    r'float\("-inf"\)',
                    r'sys\.maxsize',
                    r'float\("nan"\)'
                ],
                'weight': 0.15
            },
            'length_checks': {
                'patterns': [
                    r'len\s*\(\s*[^)]+\s*\)\s*==\s*0',
                    r'len\s*\(\s*[^)]+\s*\)\s*==\s*1',
                    r'len\s*\(\s*[^)]+\s*\)\s*>\s*0',
                    r'len\s*\(\s*[^)]+\s*\)\s*<\s*[0-9]+'
                ],
                'weight': 0.2
            },
            'none_values': {
                'patterns': [
                    r'\bNone\b',
                    r'\bnull\b'
                ],
                'weight': 0.1
            }
        }
        
        # 输入多样性模式
        self.diversity_patterns = {
            'numeric_ranges': {
                'patterns': [
                    r'\b[0-9]+\b',
                    r'\b[0-9]+\.[0-9]+\b',
                    r'\b-[0-9]+\b'
                ],
                'weight': 0.3
            },
            'string_variations': {
                'patterns': [
                    r'"[^"]*"',
                    r"'[^']*'",
                    r'f"[^"]*"',
                    r'r"[^"]*"'
                ],
                'weight': 0.25
            },
            'list_variations': {
                'patterns': [
                    r'\[[^\]]+\]',
                    r'list\([^)]+\)'
                ],
                'weight': 0.25
            },
            'dict_variations': {
                'patterns': [
                    r'\{[^}]+\}',
                    r'dict\([^)]+\)'
                ],
                'weight': 0.2
            }
        }
        
        # 测试模式识别
        self.test_patterns = {
            'basic_tests': {
                'patterns': [
                    r'test_basic_',
                    r'test_simple_',
                    r'test_normal_'
                ],
                'weight': 0.3
            },
            'edge_tests': {
                'patterns': [
                    r'test_edge_',
                    r'test_boundary_',
                    r'test_limit_'
                ],
                'weight': 0.3
            },
            'exception_tests': {
                'patterns': [
                    r'test_exception_',
                    r'test_error_',
                    r'test_invalid_'
                ],
                'weight': 0.25
            },
            'negative_tests': {
                'patterns': [
                    r'test_negative_',
                    r'test_failure_',
                    r'test_wrong_'
                ],
                'weight': 0.15
            }
        }
    
    def analyze_test_code(self, test_code: str) -> HeuristicAnalysisResult:
        """
        分析测试代码的启发式特征
        
        Args:
            test_code: 要分析的测试代码字符串
            
        Returns:
            HeuristicAnalysisResult: 启发式分析结果
        """
        try:
            # 解析代码
            tree = ast.parse(test_code)
            
            # 执行各项分析
            exception_result = self._analyze_exception_patterns(test_code)
            boundary_result = self._analyze_boundary_patterns(test_code)
            diversity_result = self._analyze_input_diversity(test_code, tree)
            pattern_result = self._analyze_test_patterns(test_code)
            quality_result = self._analyze_code_quality(tree)
            
            # 计算综合评分
            overall_score = self._calculate_overall_score([
                exception_result['score'],
                boundary_result['score'],
                diversity_result['score'],
                pattern_result['score'],
                quality_result['score']
            ])
            
            # 生成洞察
            insights = self._generate_insights(
                exception_result, boundary_result, diversity_result, 
                pattern_result, quality_result
            )
            
            return HeuristicAnalysisResult(
                exception_patterns=exception_result,
                exception_score=exception_result['score'],
                boundary_patterns=boundary_result,
                boundary_score=boundary_result['score'],
                input_diversity=diversity_result,
                diversity_score=diversity_result['score'],
                test_patterns=pattern_result,
                pattern_score=pattern_result['score'],
                code_quality=quality_result,
                quality_score=quality_result['score'],
                overall_score=overall_score,
                insights=insights
            )
            
        except SyntaxError as e:
            # 代码语法错误
            return HeuristicAnalysisResult(
                exception_patterns={'error': f'Syntax error: {str(e)}'},
                exception_score=0.0,
                boundary_patterns={'error': f'Syntax error: {str(e)}'},
                boundary_score=0.0,
                input_diversity={'error': f'Syntax error: {str(e)}'},
                diversity_score=0.0,
                test_patterns={'error': f'Syntax error: {str(e)}'},
                pattern_score=0.0,
                code_quality={'error': f'Syntax error: {str(e)}'},
                quality_score=0.0,
                overall_score=0.0,
                insights=['Code has syntax errors']
            )
        except Exception as e:
            # 其他错误
            return HeuristicAnalysisResult(
                exception_patterns={'error': f'Analysis error: {str(e)}'},
                exception_score=0.0,
                boundary_patterns={'error': f'Analysis error: {str(e)}'},
                boundary_score=0.0,
                input_diversity={'error': f'Analysis error: {str(e)}'},
                diversity_score=0.0,
                test_patterns={'error': f'Analysis error: {str(e)}'},
                pattern_score=0.0,
                code_quality={'error': f'Analysis error: {str(e)}'},
                quality_score=0.0,
                overall_score=0.0,
                insights=['Analysis failed']
            )
    
    def _analyze_exception_patterns(self, code: str) -> Dict[str, Any]:
        """分析异常测试模式"""
        results = {}
        total_score = 0.0
        max_score = 0.0
        
        for pattern_type, config in self.exception_patterns.items():
            patterns = config['patterns']
            weight = config['weight']
            max_score += weight
            
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, code, re.MULTILINE | re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                total_score += weight
                results[pattern_type] = {
                    'found': True,
                    'matches': list(set(matches)),
                    'count': len(set(matches)),
                    'weight': weight
                }
            else:
                results[pattern_type] = {
                    'found': False,
                    'matches': [],
                    'count': 0,
                    'weight': weight
                }
        
        return {
            'patterns': results,
            'score': total_score / max_score if max_score > 0 else 0.0,
            'total_matches': sum(r['count'] for r in results.values()),
            'found_patterns': [k for k, v in results.items() if v['found']]
        }
    
    def _analyze_boundary_patterns(self, code: str) -> Dict[str, Any]:
        """分析边界测试模式"""
        results = {}
        total_score = 0.0
        max_score = 0.0
        
        for pattern_type, config in self.boundary_patterns.items():
            patterns = config['patterns']
            weight = config['weight']
            max_score += weight
            
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, code, re.MULTILINE | re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                total_score += weight
                results[pattern_type] = {
                    'found': True,
                    'matches': list(set(matches)),
                    'count': len(set(matches)),
                    'weight': weight
                }
            else:
                results[pattern_type] = {
                    'found': False,
                    'matches': [],
                    'count': 0,
                    'weight': weight
                }
        
        return {
            'patterns': results,
            'score': total_score / max_score if max_score > 0 else 0.0,
            'total_matches': sum(r['count'] for r in results.values()),
            'found_patterns': [k for k, v in results.items() if v['found']]
        }
    
    def _analyze_input_diversity(self, code: str, tree: ast.AST) -> Dict[str, Any]:
        """分析输入多样性"""
        # 提取所有字符串字面量
        string_literals = []
        numeric_literals = []
        list_literals = []
        dict_literals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    string_literals.append(node.value)
                elif isinstance(node.value, (int, float)):
                    numeric_literals.append(node.value)
            elif isinstance(node, ast.List):
                list_literals.append(str(node))
            elif isinstance(node, ast.Dict):
                dict_literals.append(str(node))
        
        # 分析多样性
        string_diversity = len(set(string_literals)) / len(string_literals) if string_literals else 0
        numeric_diversity = len(set(numeric_literals)) / len(numeric_literals) if numeric_literals else 0
        
        # 计算综合多样性分数
        diversity_score = (string_diversity + numeric_diversity) / 2 if (string_literals or numeric_literals) else 0
        
        return {
            'string_literals': string_literals,
            'numeric_literals': numeric_literals,
            'list_literals': list_literals,
            'dict_literals': dict_literals,
            'string_diversity': string_diversity,
            'numeric_diversity': numeric_diversity,
            'score': diversity_score,
            'total_inputs': len(string_literals) + len(numeric_literals) + len(list_literals) + len(dict_literals)
        }
    
    def _analyze_test_patterns(self, code: str) -> Dict[str, Any]:
        """分析测试模式"""
        results = {}
        total_score = 0.0
        max_score = 0.0
        
        for pattern_type, config in self.test_patterns.items():
            patterns = config['patterns']
            weight = config['weight']
            max_score += weight
            
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, code, re.MULTILINE | re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                total_score += weight
                results[pattern_type] = {
                    'found': True,
                    'matches': list(set(matches)),
                    'count': len(set(matches)),
                    'weight': weight
                }
            else:
                results[pattern_type] = {
                    'found': False,
                    'matches': [],
                    'count': 0,
                    'weight': weight
                }
        
        return {
            'patterns': results,
            'score': total_score / max_score if max_score > 0 else 0.0,
            'total_matches': sum(r['count'] for r in results.values()),
            'found_patterns': [k for k, v in results.items() if v['found']]
        }
    
    def _analyze_code_quality(self, tree: ast.AST) -> Dict[str, Any]:
        """分析代码质量"""
        # 统计函数数量
        function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        
        # 统计复杂度（简单的行数统计）
        total_lines = len(ast.unparse(tree).split('\n')) if hasattr(ast, 'unparse') else 0
        
        # 计算平均函数长度
        avg_function_length = total_lines / function_count if function_count > 0 else 0
        
        # 质量评分（函数数量适中，平均长度合理）
        function_score = min(1.0, function_count / 5.0)  # 5个函数为满分
        length_score = max(0.0, 1.0 - (avg_function_length - 10) / 20.0)  # 10-30行为合理范围
        
        quality_score = (function_score + length_score) / 2
        
        return {
            'function_count': function_count,
            'total_lines': total_lines,
            'avg_function_length': avg_function_length,
            'function_score': function_score,
            'length_score': length_score,
            'score': quality_score
        }
    
    def _calculate_overall_score(self, scores: List[float]) -> float:
        """计算综合评分"""
        if not scores:
            return 0.0
        
        # 使用加权平均
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # 异常、边界、多样性、模式、质量
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)
        
        return weighted_sum / total_weight
    
    def _generate_insights(self, *results) -> List[str]:
        """生成洞察和建议"""
        insights = []
        
        # 异常测试洞察
        exception_result = results[0]
        if exception_result['score'] < 0.5:
            insights.append("Consider adding more exception tests using pytest.raises()")
        elif exception_result['score'] > 0.8:
            insights.append("Excellent exception test coverage")
        
        # 边界测试洞察
        boundary_result = results[1]
        if boundary_result['score'] < 0.5:
            insights.append("Add more boundary tests (empty inputs, zero, negative values)")
        elif boundary_result['score'] > 0.8:
            insights.append("Comprehensive boundary test coverage")
        
        # 输入多样性洞察
        diversity_result = results[2]
        if diversity_result['score'] < 0.5:
            insights.append("Consider using more diverse input values")
        elif diversity_result['score'] > 0.8:
            insights.append("Good input value diversity")
        
        # 测试模式洞察
        pattern_result = results[3]
        if pattern_result['score'] < 0.5:
            insights.append("Consider organizing tests into logical groups (basic, edge, exception)")
        elif pattern_result['score'] > 0.8:
            insights.append("Well-organized test structure")
        
        # 代码质量洞察
        quality_result = results[4]
        if quality_result['function_count'] < 3:
            insights.append("Consider splitting tests into more focused functions")
        elif quality_result['avg_function_length'] > 30:
            insights.append("Consider breaking down long test functions")
        
        return insights


def analyze_multiple_tests_heuristic(test_codes: List[str]) -> List[HeuristicAnalysisResult]:
    """
    批量分析多个测试代码的启发式特征
    
    Args:
        test_codes: 测试代码列表
        
    Returns:
        List[HeuristicAnalysisResult]: 启发式分析结果列表
    """
    checker = TestHeuristicChecker()
    results = []
    
    for i, test_code in enumerate(test_codes):
        print(f"Analyzing test {i+1}/{len(test_codes)} with heuristic checker...")
        result = checker.analyze_test_code(test_code)
        results.append(result)
    
    return results


def print_heuristic_summary(results: List[HeuristicAnalysisResult]) -> None:
    """打印启发式分析摘要"""
    if not results:
        print("No heuristic analysis results to display.")
        return
    
    total_tests = len(results)
    avg_overall_score = sum(r.overall_score for r in results) / total_tests
    
    print("\n" + "="*80)
    print("HEURISTIC ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total Tests Analyzed: {total_tests}")
    print(f"Average Overall Score: {avg_overall_score:.3f}")
    print()
    
    # 各项指标的统计
    categories = [
        ('Exception Tests', 'exception_score'),
        ('Boundary Tests', 'boundary_score'),
        ('Input Diversity', 'diversity_score'),
        ('Test Patterns', 'pattern_score'),
        ('Code Quality', 'quality_score')
    ]
    
    print("Average Scores by Category:")
    print("-" * 50)
    for category_name, attr_name in categories:
        avg_score = sum(getattr(r, attr_name) for r in results) / total_tests
        print(f"{category_name:20} {avg_score:.3f}")
    
    print("\n" + "="*80)


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
    
    print("Testing Heuristic Checker...")
    checker = TestHeuristicChecker()
    result = checker.analyze_test_code(sample_test)
    
    print(f"Overall Score: {result.overall_score:.3f}")
    print(f"Exception Score: {result.exception_score:.3f}")
    print(f"Boundary Score: {result.boundary_score:.3f}")
    print(f"Diversity Score: {result.diversity_score:.3f}")
    print(f"Pattern Score: {result.pattern_score:.3f}")
    print(f"Quality Score: {result.quality_score:.3f}")
    print(f"Insights: {result.insights}")
