# LLM-TDD: Test-Driven Code Generation with LangChain

This repository explores the integration of Test-Driven Development (TDD) with Large Language Models (LLMs), aiming to systematically improve code generation quality and robustness. The project begins by reproducing HumanEval results using LangChain pipelines and gradually extends into TDD-style prompt strategies, structured test generation, and benchmark design.

## Overview

Large Language Models such as GPT-4 and LLaMA are capable of generating functional code from natural language descriptions. However, ensuring correctness, robustness, and coverage remains a major challenge. This project follows a **test-driven philosophy**, exploring how structured testing—either as input or as evaluation—can guide LLMs towards more reliable code.

Our initial goal is to **reproduce HumanEval results using LangChain**, serving as a baseline. Building on this, we will experiment with embedding various types of tests into prompts, including both user-written and LLM-generated tests.

## Project Phases

### Phase 1: HumanEval Baseline Reproduction

- Use LangChain and GPT APIs to reproduce HumanEval pass@k scores.
- No test-augmented prompts in this stage; only task descriptions and function signatures are used.

### Phase 2: Prompt-Augmented Code Generation

- Include human-written test cases in prompts to guide generation.
- Analyze improvements due to test guidance (acknowledging possible leakage).

### Phase 3: LLM-Generated Test Injection

- Generate test cases from descriptions using GPT.
- Feed both tests and signatures into the prompt, and compare to previous phases.

## Workflow Summary

1. **Benchmark Loading**: Start with HumanEval as the benchmark task suite.
2. **Prompting via LangChain**: Use function signature (+ optional test cases) as structured prompt.
3. **Code Generation**: GPT model generates Python code.
4. **Evaluation**:
   - Execute generated code against HumanEval test suites.
   - Measure pass@k, error types, and performance statistics.
5. **Extension (optional)**: Inject LLM-generated test cases to observe improvement or degradation.