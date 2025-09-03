#!/usr/bin/env python3
"""
Pytest执行框架

安全执行LLM生成的代码和测试，返回详细的执行结果。
"""

import os
import sys
import json
import tempfile
import subprocess
import time
import traceback
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class TestResult:
    """测试执行结果"""
    task_id: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    passed_test_details: List[Dict[str, Any]]
    failed_test_details: List[Dict[str, Any]]
    execution_time: float
    memory_usage: str
    python_version: str
    pytest_version: str
    ready_for_repair: bool
    can_stop_iteration: bool
    error_summary: str


@dataclass
class FailedTest:
    """失败的测试详情"""
    test_name: str
    assertion: str
    expected: str
    actual: str
    error_type: str
    error_message: str
    line_number: Optional[int]
    traceback: str


class PytestExecutor:
    """Pytest执行器"""
    
    def __init__(self, timeout: int = 30, max_memory: str = "100MB"):
        self.timeout = timeout
        self.max_memory = max_memory
        self.python_version = sys.version
        self.pytest_version = self._get_pytest_version()
    
    def _get_pytest_version(self) -> str:
        """获取pytest版本"""
        try:
            result = subprocess.run(
                ["pytest", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def _combine_code_and_tests(self, code: str, tests: str) -> str:
        """合并代码和测试，解决MBPP上下文问题"""
        # 清理代码和测试
        code = code.strip()
        tests = tests.strip()
        
        # 检查测试中是否已经包含函数定义
        if self._tests_contain_function_definition(tests):
            # 如果测试中已经包含函数定义，需要修复import语句
            tests = self._fix_import_statements(tests)
            return tests
        
        # 否则，将代码和测试合并
        combined = []
        
        # 添加必要的导入
        combined.append("import pytest")
        combined.append("import sys")
        combined.append("import os")
        combined.append("")
        
        # 添加代码
        combined.append("# Generated code")
        combined.append(code)
        combined.append("")
        
        # 修复测试中的import语句
        tests = self._fix_import_statements(tests)
        
        # 添加测试
        combined.append("# Generated tests")
        combined.append(tests)
        
        return "\n".join(combined)
    
    def _fix_import_statements(self, tests: str) -> str:
        """修复测试中的错误import语句"""
        lines = tests.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复常见的错误import模式
            if 'from your_module import' in line:
                # 移除错误的import语句
                continue
            elif 'import your_module' in line:
                # 移除错误的import语句
                continue
            elif line.strip().startswith('from ') and 'import' in line and 'your_module' in line:
                # 移除其他错误的import语句
                continue
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _tests_contain_function_definition(self, tests: str) -> bool:
        """检查测试中是否包含函数定义"""
        lines = tests.split('\n')
        for line in lines:
            line = line.strip()
            # 检查是否包含函数定义（排除测试函数）
            if line.startswith('def ') and not line.startswith('def test_'):
                return True
        return False
    
    def execute_tests(self, code: str, tests: str, task_id: str = "unknown") -> TestResult:
        """执行测试并返回详细结果"""
        start_time = time.time()
        
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 创建合并的测试文件
                test_file = os.path.join(temp_dir, "test_file.py")
                
                # 合并代码和测试
                combined_content = self._combine_code_and_tests(code, tests)
                
                # 写入合并后的测试文件
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(combined_content)
                
                # 执行pytest
                result = self._run_pytest(temp_dir, test_file)
                
                # 解析结果
                execution_time = time.time() - start_time
                test_result = self._parse_pytest_output(result, task_id, execution_time)
                
                return test_result
                
        except Exception as e:
            # 处理执行异常
            execution_time = time.time() - start_time
            return self._create_error_result(task_id, str(e), execution_time)
    
    def _run_pytest(self, temp_dir: str, test_file: str) -> subprocess.CompletedProcess:
        """运行pytest命令"""
        cmd = [
            "pytest", 
            test_file, 
            "-v", 
            "--tb=short", 
            "--capture=no"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "PYTHONPATH": temp_dir}
            )
            return result
        except subprocess.TimeoutExpired:
            # 超时处理
            return subprocess.CompletedProcess(
                cmd, -1, "", "Test execution timed out"
            )
    
    def _parse_pytest_output(self, result: subprocess.CompletedProcess, task_id: str, execution_time: float) -> TestResult:
        """解析pytest输出"""
        stdout = result.stdout
        stderr = result.stderr
        
        # 统计测试结果
        passed_tests = []
        failed_tests = []
        
        # 改进的测试结果解析
        lines = stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 解析通过的测试
            if "PASSED" in line and "test_" in line:
                # 提取测试名称
                test_name = self._extract_test_name(line)
                if test_name:
                    passed_tests.append({
                        "test_name": test_name,
                        "assertion": f"Test {test_name} passed",
                        "status": "PASS"
                    })
            
            # 解析失败的测试
            elif "FAILED" in line and "test_" in line:
                test_name = self._extract_test_name(line)
                if test_name:
                    failed_test = self._extract_failed_test_details(test_name, stdout, stderr)
                    failed_tests.append(failed_test)
        
        # 如果没有找到测试结果，检查是否有其他错误
        if not passed_tests and not failed_tests:
            # 检查是否有测试收集错误
            if "collected 0 items" in stdout or "no tests ran" in stdout:
                # 尝试从stderr中获取更多信息
                error_message = stderr if stderr else "No tests were collected"
                return self._create_error_result(task_id, error_message, execution_time)
        
        # 计算统计信息
        total_tests = len(passed_tests) + len(failed_tests)
        passed_count = len(passed_tests)
        failed_count = len(failed_tests)
        success_rate = passed_count / total_tests if total_tests > 0 else 0.0
        
        # 判断是否需要修复
        ready_for_repair = failed_count > 0
        can_stop_iteration = failed_count == 0
        
        return TestResult(
            task_id=task_id,
            total_tests=total_tests,
            passed_tests=passed_count,
            failed_tests=failed_count,
            success_rate=success_rate,
            passed_test_details=passed_tests,
            failed_test_details=[self._failed_test_to_dict(ft) for ft in failed_tests],
            execution_time=execution_time,
            memory_usage="N/A",  # 简化处理
            python_version=self.python_version,
            pytest_version=self.pytest_version,
            ready_for_repair=ready_for_repair,
            can_stop_iteration=can_stop_iteration,
            error_summary=self._generate_error_summary(failed_tests)
        )
    
    def _extract_test_name(self, line: str) -> str:
        """从pytest输出行中提取测试名称"""
        # 匹配各种pytest输出格式
        patterns = [
            r"test_file\.py::test_\w+",
            r"test_\w+",
            r"::test_\w+"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_failed_test_details(self, test_name: str, stdout: str, stderr: str) -> FailedTest:
        """提取失败测试的详细信息"""
        # 查找测试失败的具体信息
        test_section = self._find_test_section(stdout, test_name)
        
        # 提取断言信息
        assertion = self._extract_assertion(test_section)
        
        # 提取错误信息
        error_type, error_message = self._extract_error_info(test_section)
        
        # 提取行号
        line_number = self._extract_line_number(test_section)
        
        # 构建traceback
        traceback_info = self._build_traceback(test_section)
        
        return FailedTest(
            test_name=test_name,
            assertion=assertion,
            expected="Test should pass",
            actual=f"Failed with {error_type}",
            error_type=error_type,
            error_message=error_message,
            line_number=line_number,
            traceback=traceback_info
        )
    
    def _find_test_section(self, stdout: str, test_name: str) -> str:
        """查找特定测试的输出部分"""
        lines = stdout.split('\n')
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            if test_name in line and "FAILED" in line:
                start_idx = i
                break
        
        if start_idx != -1:
            # 查找下一个测试或结束
            for i in range(start_idx + 1, len(lines)):
                if lines[i].startswith("test_") and ("PASSED" in lines[i] or "FAILED" in lines[i]):
                    end_idx = i
                    break
            
            if end_idx == -1:
                end_idx = len(lines)
            
            return '\n'.join(lines[start_idx:end_idx])
        
        return ""
    
    def _extract_assertion(self, test_section: str) -> str:
        """提取断言信息"""
        # 简化处理，返回测试名称
        return "Test assertion"
    
    def _extract_error_info(self, test_section: str) -> tuple:
        """提取错误类型和消息"""
        if "AssertionError" in test_section:
            return "AssertionError", "Assertion failed"
        elif "IndexError" in test_section:
            return "IndexError", "Index out of range"
        elif "TypeError" in test_section:
            return "TypeError", "Type error occurred"
        elif "ValueError" in test_section:
            return "ValueError", "Value error occurred"
        else:
            return "RuntimeError", "Test execution failed"
    
    def _extract_line_number(self, test_section: str) -> Optional[int]:
        """提取行号"""
        # 简化处理
        return None
    
    def _build_traceback(self, test_section: str) -> str:
        """构建traceback信息"""
        return test_section
    
    def _failed_test_to_dict(self, failed_test: FailedTest) -> Dict[str, Any]:
        """将FailedTest转换为字典"""
        return {
            "test_name": failed_test.test_name,
            "assertion": failed_test.assertion,
            "expected": failed_test.expected,
            "actual": failed_test.actual,
            "error_type": failed_test.error_type,
            "error_message": failed_test.error_message,
            "line_number": failed_test.line_number,
            "traceback": failed_test.traceback
        }
    
    def _create_error_result(self, task_id: str, error_message: str, execution_time: float) -> TestResult:
        """创建错误结果"""
        return TestResult(
            task_id=task_id,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            success_rate=0.0,
            passed_test_details=[],
            failed_test_details=[],
            execution_time=execution_time,
            memory_usage="N/A",
            python_version=self.python_version,
            pytest_version=self.pytest_version,
            ready_for_repair=False,
            can_stop_iteration=True,
            error_summary=f"Execution error: {error_message}"
        )
    
    def _generate_error_summary(self, failed_tests: List[FailedTest]) -> str:
        """生成错误摘要"""
        if not failed_tests:
            return "All tests passed"
        
        error_types = {}
        for test in failed_tests:
            error_type = test.error_type
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        summary_parts = []
        for error_type, count in error_types.items():
            summary_parts.append(f"{error_type}: {count}")
        
        return f"Failed tests: {', '.join(summary_parts)}"


def main():
    """测试主函数"""
    # 示例代码和测试
    code = """
def add_numbers(a, b):
    return a + b
"""
    
    tests = """
import pytest

def test_add_positive():
    assert add_numbers(2, 3) == 5

def test_add_negative():
    assert add_numbers(-1, -2) == -3

def test_add_zero():
    assert add_numbers(5, 0) == 5
"""
    
    executor = PytestExecutor()
    result = executor.execute_tests(code, tests, "test_task")
    
    print("Test Execution Result:")
    print(f"Total Tests: {result.total_tests}")
    print(f"Passed: {result.passed_tests}")
    print(f"Failed: {result.failed_tests}")
    print(f"Success Rate: {result.success_rate:.2%}")
    print(f"Ready for Repair: {result.ready_for_repair}")
    print(f"Can Stop Iteration: {result.can_stop_iteration}")


if __name__ == "__main__":
    main()
