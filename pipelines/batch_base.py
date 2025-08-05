#!/usr/bin/env python3
"""
Base Batch Pipeline
Common functionality for batch code generation pipelines
"""

import os
import sys
import datetime
import json
from abc import ABC, abstractmethod
from tqdm import tqdm
sys.path.append('.')

from pipelines.lc_chain.generator import generate_one_completion_langchain

class BaseBatchPipeline(ABC):
    """Base class for batch code generation pipelines"""
    
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
    
    @abstractmethod
    def read_problems(self, problem_file):
        """Read problems from file, return dict of task_id -> problem"""
        pass
    
    @abstractmethod
    def get_output_filename(self, num_tasks, prefix):
        """Generate output filename"""
        pass
    
    @abstractmethod
    def create_sample(self, task_id, problem, completion, error=None):
        """Create sample dict for output"""
        pass
    
    @abstractmethod
    def save_results(self, output_file, samples):
        """Save results to file"""
        pass
    
    @abstractmethod
    def get_prompt(self, problem):
        """Get prompt for the problem"""
        pass
    
    def generate_batch_output_filename(self, num_tasks=10, prefix="langchain_batch"):
        """Generate output filename for batch processing"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        model_clean = self.model.replace("-", "_").replace(".", "_")
        return self.get_output_filename(num_tasks, prefix).format(
            prefix=prefix,
            num_tasks=num_tasks,
            model=model_clean,
            timestamp=timestamp
        )
    
    def run_batch_pipeline(self, problem_file, num_tasks=10, start_task=0):
        """Run batch pipeline on multiple tasks"""
        try:
            # Generate output filename
            output_file = self.generate_batch_output_filename(num_tasks)
            
            # Read problems
            print(f"Reading problem file: {problem_file}")
            problems = self.read_problems(problem_file)
            print(f"Total problems available: {len(problems)}")
            
            # Select tasks to process
            task_items = list(problems.items())
            end_task = min(start_task + num_tasks, len(task_items))
            selected_tasks = task_items[start_task:end_task]
            
            print(f"Processing tasks {start_task} to {end_task-1} ({len(selected_tasks)} tasks)")
            print(f"Using model: {self.model}")
            print("=" * 50)
            
            # Process tasks with progress bar
            samples = []
            for task_id, problem in tqdm(selected_tasks, desc="Generating code"):
                try:
                    # Get prompt for the problem
                    prompt = self.get_prompt(problem)
                    
                    # Generate code completion
                    completion = generate_one_completion_langchain(prompt, self.model)
                    
                    # Create sample
                    sample = self.create_sample(task_id, problem, completion)
                    samples.append(sample)
                    
                except Exception as e:
                    print(f"Error processing {task_id}: {e}")
                    # Add error sample
                    sample = self.create_sample(task_id, problem, "    pass", error=str(e))
                    samples.append(sample)
            
            # Save results
            self.save_results(output_file, samples)
               
            print(f"\nResults saved: {output_file}")
            
            # Print summary
            successful = sum(1 for s in samples if 'error' not in s)
            failed = len(samples) - successful
            print(f"Summary: {successful} successful, {failed} failed")
            
            return output_file
            
        except Exception as e:
            print(f"Batch processing failed: {e}")
            return None 