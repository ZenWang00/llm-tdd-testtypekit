#!/usr/bin/env python3
"""
Environment setup script for LLM-TDD project.
This script helps users configure their environment variables.
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables."""
    # First check system environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✅ OPENAI_API_KEY found in system environment")
        return True
    
    # Fallback to .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found and OPENAI_API_KEY not in system environment!")
        print("Please either:")
        print("1. Set OPENAI_API_KEY in your system environment, or")
        print("2. Copy env.example to .env and configure your API keys:")
        print("   cp env.example .env")
        return False
    
    # Read .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check for required variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if f'{var}=' not in content or f'{var}=your_' in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or not configured variables: {', '.join(missing_vars)}")
        print("Please update your .env file with actual values.")
        return False
    
    print("✅ .env file is properly configured")
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import openai
        import langchain_core
        import langchain_openai
        import numpy
        import tqdm
        import fire
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_humaneval():
    """Check if HumanEval benchmark is properly installed."""
    try:
        from human_eval.data import read_problems
        print("✅ HumanEval benchmark is properly installed")
        return True
    except ImportError:
        print("❌ HumanEval benchmark not found")
        print("Please install it with: pip install -e benchmarks/humaneval/")
        return False

def main():
    """Main setup function."""
    print("🔧 LLM-TDD Environment Setup")
    print("=" * 40)
    
    checks = [
        ("Environment Variables", check_env_file),
        ("Dependencies", check_dependencies),
        ("HumanEval Benchmark", check_humaneval),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("1. Run the test generator: python benchmarks/humaneval/test_gpt_generator.py")
        print("2. Or use Docker: docker-compose up llm-tdd")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 