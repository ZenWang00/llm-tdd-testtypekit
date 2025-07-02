# LLM-TDD TestTypeKit

This repository explores the integration of Test-Driven Development (TDD) practices with Large Language Models (LLMs) to systematically improve code generation quality, correctness, and robustness. We introduce the "TestTypeKit," a structured framework for automated, type-specific unit-test generation that guides LLMs towards generating high-quality code.

## Overview

Code generation using large language models (such as GPT-4 and LLaMA) holds immense promise, but ensuring generated code correctness and robustness remains challenging. This project applies TDD methodologies, where tests are generated first to guide the model's code generation, rather than merely validating code after generation.

The primary innovation, "TestTypeKit," provides a structured set of prompt templates categorized by unit-test types (e.g., boundary, exception, nominal, property-based), enabling clear, repeatable experiments to quantify how specific test types influence LLM-generated code.

## Workflow

The overall workflow clearly integrates LangChain for managing LLM interactions and GPT APIs provided by Professor Paolo:

1. **Benchmark Construction**: Instead of relying on existing benchmarks like MBPP or HumanEval, we define our own suite of tasks inspired by realistic code snippets. Each task includes a function signature, natural language description, optional reference solution, and test cases.

2. **Test Generation using GPT APIs and LangChain**:

   * **Type-Guided Generation**: LangChain is used to manage structured interactions with GPT models, systematically producing structured, type-specific unit tests from defined TestTypeKit templates.
   * **Zero-Shot Generation**: Leveraging GPT APIs via LangChain to automatically generate diverse unit tests directly from function signatures and descriptions without predefined test categories.

3. **Code Generation via LangChain and GPT**:

   * Generated unit tests are embedded in LangChain-managed prompts.
   * GPT models then synthesize code guided by these structured prompts and generated tests.

4. **Evaluation and Analysis**:

   * Execute the generated code against tests (both generated and embedded in task definitions).
   * Collect detailed metrics: correctness, code coverage, mutation scores, error types, stability, and efficiency.
   * Analyze results using statistical methods to identify the impact of different test-generation approaches.

## Goals

* Develop structured, reusable prompt templates for automated, type-specific test generation.
* Evaluate the impact of different unit-test types on the quality and correctness of LLM-generated code.
* Build and maintain a custom benchmark of real-world inspired function tasks for flexible, type-oriented testing.

## Benchmark Design

Inspired by frameworks such as Robust-Attack-Detectors-LLM, each task is defined with the following structured JSON schema:

```json
{
  "task_id": "unique_task_identifier",
  "source": "custom",
  "function_signature": "def function_name(args):",
  "description": "Natural language description of the function.",
  "reference_solution": "Optional reference implementation.",
  "reference_tests": [
    {"input": "input_example", "expected_output": "expected_result", "type": "test_category"}
  ],
  "generated_tests": [],
  "metadata": {
    "language": "python",
    "tags": ["tag1", "tag2"],
    "difficulty": "difficulty_level"
  }
}
```

## Experimental Setup

The project evaluates the following unit-test categories:

* Boundary Value Tests
* Exception Tests
* Nominal (Happy-Path) Tests
* Property-Based Tests
* State-Transition Tests (where applicable)

Systematic experiments are run using:

* Dozens of self-defined tasks stored in the benchmark folder.
* Automated generation of unit tests using the "TestTypeKit" prompt templates.
* Evaluation metrics including pass rate, statement coverage, mutation score, error-type distribution, stability, and efficiency.

## Repository Structure

```
llm-tdd-testtypekit/
├── benchmarks/
│   └── custom/
├── prompts/
│   └── testtypekit_templates.py
├── test_generators/
│   ├── zero_shot_generator.py
│   └── type_guided_generator.py
├── evaluation/
│   ├── execute_tests.py
│   └── collect_metrics.py
├── results/
│   └── experimental_runs/
└── notebooks/
    └── analysis.ipynb
```

## How to Use

Detailed instructions will be provided in the `evaluation` scripts. Basic workflow:

1. Add benchmark tasks to `benchmarks/custom/` using the defined JSON structure.
2. Use scripts in `test_generators/` to produce unit tests with GPT APIs via LangChain.
3. Generate code using the tests embedded in prompts.
4. Run the generated code and evaluate performance using the evaluation scripts.
5. Analyze outcomes using provided notebooks.
