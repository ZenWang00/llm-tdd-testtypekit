# LLM-TDD: Test-Driven Code Generation with LangChain

This repository explores the integration of Test-Driven Development (TDD) with Large Language Models (LLMs), aiming to systematically improve code generation quality and robustness. The project begins by reproducing HumanEval results using LangChain pipelines and gradually extends into TDD-style prompt strategies, structured test generation, and benchmark design.

## Overview

Large Language Models such as GPT-4 and LLaMA are capable of generating functional code from natural language descriptions. However, ensuring correctness, robustness, and coverage remains a major challenge. This project follows a **test-driven philosophy**, exploring how structured testing—either as input or as evaluation—can guide LLMs towards more reliable code.

Our initial goal is to **reproduce HumanEval results using LangChain**, serving as a baseline. Building on this, we will experiment with embedding various types of tests into prompts, including both user-written and LLM-generated tests.

## Current Status

The project has successfully implemented Phase 1: HumanEval Baseline Reproduction using LangChain. The system can:

- Read HumanEval benchmark problems
- Generate code completions using LangChain and OpenAI APIs
- Save results with timestamped filenames
- Run evaluations using HumanEval's functional correctness metrics

## Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenAI API key

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-tdd-testtypekit
   ```

2. **Set up environment variables**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Set your OpenAI API key
   export OPENAI_API_KEY=your_api_key_here
   ```

3. **Build and run with Docker**
   ```bash
   # Build the container
   docker-compose build
   
   # Start the development environment
   docker-compose up llm-tdd
   ```

### Alternative: Local Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install HumanEval benchmark**
   ```bash
   pip install -e benchmarks/humaneval/
   ```

## Usage

### Running the LangChain Pipeline

The main pipeline reads HumanEval problems and generates code completions:

```bash
# Run the complete pipeline
docker exec -it llm-tdd python pipelines/test_langchain.py

# Or run as a module
docker exec -it llm-tdd python -c "from pipelines.test_langchain import run_langchain_pipeline; run_langchain_pipeline()"

# Specify a different model
docker exec -it llm-tdd python -c "from pipelines.test_langchain import run_langchain_pipeline; run_langchain_pipeline(model='gpt-4')"
```

### Individual Code Generation

For testing individual function generation:

```bash
# Test single function generation
docker exec -it llm-tdd python -c "from pipelines.langchain.generator import generate_one_completion_langchain; print(generate_one_completion_langchain('def add(a, b):'))"
```

### Evaluation

After running the pipeline, evaluate the results:

```bash
# Run HumanEval evaluation
docker exec -it llm-tdd evaluate_functional_correctness benchmarks/humaneval/data/langchain_results_gpt_4o_mini_YYYYMMDD_HHMMSS.jsonl --problem_file=benchmarks/humaneval/data/example_problem.jsonl

# View generated results
docker exec -it llm-tdd cat benchmarks/humaneval/data/langchain_results_gpt_4o_mini_YYYYMMDD_HHMMSS.jsonl
```

## Project Structure

```
llm-tdd-testtypekit/
├── pipelines/
│   ├── langchain/
│   │   ├── generator.py          # Core LangChain generation logic
│   │   └── prompts/
│   │       └── humaneval.py      # HumanEval prompt templates
│   ├── openai_direct/
│   │   └── generator.py          # Direct OpenAI API calls
│   └── test_langchain.py         # Main pipeline runner
├── benchmarks/
│   └── humaneval/
│       └── data/
│           ├── example_problem.jsonl
│           └── langchain_results_*.jsonl
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Project Phases

### Phase 1: HumanEval Baseline Reproduction [COMPLETED]

- Use LangChain and GPT APIs to reproduce HumanEval pass@k scores.
- No test-augmented prompts in this stage; only task descriptions and function signatures are used.

### Phase 2: Prompt-Augmented Code Generation [PLANNED]

- Include human-written test cases in prompts to guide generation.
- Analyze improvements due to test guidance (acknowledging possible leakage).

### Phase 3: LLM-Generated Test Injection [PLANNED]

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

## Configuration

The system supports various configuration options through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `DEFAULT_MODEL`: Model to use (default: gpt-4o-mini)
- `TEMPERATURE`: Generation temperature (default: 0.7)
- `MAX_TOKENS`: Maximum tokens per generation (default: 200)
- `TIMEOUT`: API timeout in seconds (default: 60)

## Troubleshooting

### Network Issues
If you encounter network connectivity issues, the Docker setup includes proxy configuration for VPN users. Update the proxy settings in `docker-compose.yml` if needed.

### API Errors
Ensure your OpenAI API key is correctly set and has sufficient credits for the model you're using.

### File Permissions
If running locally, ensure the `benchmarks/humaneval/data/` directory is writable for saving results.