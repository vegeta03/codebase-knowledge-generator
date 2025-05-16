#!/usr/bin/env python
"""
Test script for the hierarchical AST-aware chunking system.
This script helps validate that the chunking system:
1. Correctly reserves 20% of model context for responses
2. Uses tree-sitter for AST-aware chunking
3. Handles multiple languages properly
"""

import os
import sys
import logging
import argparse
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_chunking")

# Import our chunking utilities
from utils.code_chunking import chunk_codebase, MODEL_CONTEXT_LENGTH, MAX_INPUT_TOKENS
from utils.chunk_processor import process_code_for_llm, estimate_model_calls

def parse_args():
    parser = argparse.ArgumentParser(description="Test the hierarchical AST-aware chunking system")
    parser.add_argument("--file", help="Path to a single file to test chunking on")
    parser.add_argument("--dir", help="Path to a directory to test chunking on")
    parser.add_argument("--lang", help="Force a specific language (default: auto-detect from file extension)")
    parser.add_argument("--context-length", type=int, default=MODEL_CONTEXT_LENGTH, 
                       help=f"Override the model context length (default: {MODEL_CONTEXT_LENGTH})")
    return parser.parse_args()

def read_file(file_path: str) -> str:
    """Read a file and return its content."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def scan_directory(dir_path: str) -> Dict[str, str]:
    """Scan a directory for files and return a map of file paths to contents."""
    file_contents = {}
    file_paths = []
    
    print(f"Scanning directory: {dir_path}")
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) < 1024 * 1024:  # Skip files larger than 1MB
                try:
                    content = read_file(file_path)
                    file_contents[file_path] = content
                    file_paths.append(file_path)
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
    
    return file_paths, file_contents

def display_chunk_info(chunks: List):
    """Display information about the chunks."""
    total_tokens = sum(chunk['token_count'] for chunk in chunks)
    
    print("\n===== Chunk Information =====")
    print(f"Total chunks: {len(chunks)}")
    print(f"Total tokens: {total_tokens}")
    print(f"Model context length: {MODEL_CONTEXT_LENGTH}")
    print(f"Maximum input tokens (80%): {MAX_INPUT_TOKENS}")
    print(f"Reserved tokens for response (20%): {int(MODEL_CONTEXT_LENGTH * 0.2)}")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}/{len(chunks)} - {chunk['token_count']} tokens")
        print(f"Files: {', '.join(os.path.basename(f) for f in chunk['files'])}")
        print(f"Token usage: {chunk['token_count']/MODEL_CONTEXT_LENGTH*100:.1f}% of context")

def main():
    args = parse_args()
    
    # Override model context length if specified
    if args.context_length:
        global MODEL_CONTEXT_LENGTH, MAX_INPUT_TOKENS
        MODEL_CONTEXT_LENGTH = args.context_length
        MAX_INPUT_TOKENS = int(MODEL_CONTEXT_LENGTH * 0.8)
        print(f"Using custom model context length: {MODEL_CONTEXT_LENGTH}")
        print(f"Reserved 20% ({int(MODEL_CONTEXT_LENGTH * 0.2)} tokens) for model response")
    
    if args.file:
        # Test chunking on a single file
        file_path = os.path.abspath(args.file)
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found")
            return
        
        print(f"Testing chunking on file: {file_path}")
        content = read_file(file_path)
        base_dir = os.path.dirname(file_path)
        
        # Create a simple prompt template for testing
        prompt_template = "Analyze this code:\n\n{code}\n\nProvide insights."
        
        # Process the file
        prepared_prompts = process_code_for_llm(
            base_dir=base_dir,
            file_paths=[file_path],
            file_contents={file_path: content},
            prompt_template=prompt_template
        )
        
        # Display the results
        display_chunk_info(prepared_prompts)
        
    elif args.dir:
        # Test chunking on a directory
        dir_path = os.path.abspath(args.dir)
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            print(f"Error: Directory {dir_path} not found")
            return
        
        # Scan the directory for files
        file_paths, file_contents = scan_directory(dir_path)
        print(f"Found {len(file_paths)} files")
        
        # Create a simple prompt template for testing
        prompt_template = "Analyze this code:\n\n{code}\n\nProvide insights."
        
        # First, show estimation
        estimation = estimate_model_calls(file_paths, file_contents)
        print("\n===== Estimation =====")
        print(f"Files: {estimation['files']}")
        print(f"Estimated code tokens: {estimation['estimated_code_tokens']}")
        print(f"Estimated chunks: {estimation['estimated_chunks']}")
        print(f"Estimated input tokens: {estimation['estimated_input_tokens']}")
        print(f"Estimated response tokens: {estimation['estimated_response_tokens']}")
        print(f"Estimated total tokens: {estimation['total_tokens']}")
        
        # Process the directory
        prepared_prompts = process_code_for_llm(
            base_dir=dir_path,
            file_paths=file_paths,
            file_contents=file_contents,
            prompt_template=prompt_template
        )
        
        # Display the results
        display_chunk_info(prepared_prompts)
    
    else:
        print("Please specify either --file or --dir")
        return

if __name__ == "__main__":
    main()
