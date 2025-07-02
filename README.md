# LLM-TDD TestTypeKit

This repository explores the integration of Test-Driven Development (TDD) practices with Large Language Models (LLMs) to systematically improve code generation quality, correctness, and robustness. We introduce the "TestTypeKit," a structured framework for automated, type-specific unit-test generation that guides LLMs towards generating high-quality code.

## Overview

Code generation using large language models (such as GPT-4 and LLaMA) holds immense promise, but ensuring generated code correctness and robustness remains challenging. This project applies TDD methodologies, where tests are generated first to guide the model's code generation, rather than merely validating code after generation.

The primary innovation, "TestTypeKit," provides a structured set of prompt templates categorized by unit-test types (e.g., boundary, exception, nominal, property-based), enabling clear, repeatable experiments to quantify how specific test types influence LLM-generated code.

## Workflow

The overall workflow consists of the following clear steps:

1. **Benchmark Preparation**: Tasks from established benchmarks (MBPP, HumanEval, real-world code snippets) are structured into standardized JSON format.
2. **Test Generation**:

   * **Type-Guided Generation**: Using TestTypeKit templates to systematically produce structured, type-specific unit tests.
   * **Zero-Shot Generation**: Generating unit tests from function signatures and descriptions without predefined categories.
3. **Code Generation**: Using the generated tests embedded within LLM prompts to guide code synthesis.
4. **Evaluation and Analysis**:

   * Execute the generated code against tests.
   * Measure detailed metrics including correctness, code coverage, mutation scores, error types, stability, and efficiency.
   * Analyze results using statistical methods to determine the impact of different test-generation approaches.

## Goals

* Develop structured, reusable prompt templates for automated, type-specific test generation.
* Evaluate the impact of different unit-test types on the quality and correctness of LLM-generated code.
* Benchmark LLM performance systematically using standard code-generation tasks (MBPP, HumanEval) and real-world code scenarios.

## Benchmark Design

Inspired by existing robust benchmark frameworks, each task is defined with the following structured JSON schema:

```json
{
  "task_id": "unique_task_identifier",
  "source": "benchmark_name",
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

* Multiple benchmark tasks (MBPP, HumanEval, and custom-curated real-world scenarios).
* Automated generation of unit tests using the "TestTypeKit" prompt templates.
* Evaluation metrics including pass rate, statement coverage, mutation score, error-type distribution, stability, and efficiency.

## Integration with LangChain

The project leverages LangChain, an advanced framework designed to simplify the interaction with large language models. LangChain provides:

* Efficient prompt management and execution.
* Robust mechanisms for chaining model interactions.
* Simplified integration with various LLM APIs.

## GPT API Access

Professor Paolo has kindly provided access to GPT APIs for conducting experiments within this project. This access enables us to perform extensive, controlled experiments with GPT models, ensuring reproducibility and scalability.

## Repository Structure

```
llm-tdd-testtypekit/
├── benchmarks/
│   ├── mbpp/
│   ├── humaneval/
│   └── realworld/
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

1. Select or add benchmark tasks to `benchmarks/`.
2. Use scripts in `test_generators/` to produce unit tests.
3. Generate code using tests embedded in prompt templates.
4. Run the generated code and measure performance with evaluation scripts.
5. Analyze outcomes using provided notebooks.

## Contributing

Contributions are highly encouraged! Feel free to:

* Submit pull requests with improvements or new benchmarks.
* Open issues to discuss new features, tests, or improvements.

## License

This project is licensed under the MIT License.
