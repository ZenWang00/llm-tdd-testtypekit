# Use local python 3.11 image as base
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 配置国内pip源加速
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# 可选：如需 HumanEval，仅在 requirements.txt 里注明或手动安装
# RUN pip install -e benchmarks/humaneval/

# Create necessary directories
RUN mkdir -p outputs

# Set default command
CMD ["python", "-c", "print('LLM-TDD environment ready. Use docker run -it <image> bash to enter container.')"] 