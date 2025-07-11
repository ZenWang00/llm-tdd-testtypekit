"""
OpenAI Direct Pipeline

Direct OpenAI API calls for code generation.
"""

from .generator import generate_one_completion

__all__ = ["generate_one_completion"] 