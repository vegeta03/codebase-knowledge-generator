"""
Chunk processor for integrating the AST-aware chunking system with LLM calls.

This module provides an adapter between the AST-aware code chunking system and 
the existing LLM call functionality, ensuring that:
1. 20% of model context length is reserved for responses
2. Input chunks are never more than 80% of the context length
3. The hierarchical chunking strategy is properly utilized
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import re

# Set up logging
logger = logging.getLogger("chunk_processor")

# Import the code chunking system
from utils.code_chunking import chunk_codebase, DEFAULT_MODEL_CONTEXT_LENGTH

# Get model context length from environment or default
MODEL_CONTEXT_LENGTH = int(os.getenv("CURRENT_MODEL_CONTEXT_LENGTH", DEFAULT_MODEL_CONTEXT_LENGTH))
MAX_INPUT_TOKENS = int(MODEL_CONTEXT_LENGTH * 0.8)

def process_code_for_llm(base_dir: str, 
                        file_paths: List[str], 
                        file_contents: Dict[str, str],
                        prompt_template: str,
                        prompt_token_estimate: int = 200) -> List[Dict[str, Any]]:
    """
    Process codebase files into chunks suitable for LLM processing,
    prepared with the given prompt template.
    
    Args:
        base_dir: Base directory of the codebase
        file_paths: List of file paths to process
        file_contents: Dict mapping file paths to their contents
        prompt_template: Template string where {code} will be replaced with code content
        prompt_token_estimate: Estimated tokens in the prompt template (excluding code)
        
    Returns:
        List of dictionaries with prepared prompts and metadata
    """
    # Re-read environment variable at runtime to ensure latest value
    current_model_context_length = int(os.getenv("CURRENT_MODEL_CONTEXT_LENGTH", DEFAULT_MODEL_CONTEXT_LENGTH))
    max_input_tokens = int(current_model_context_length * 0.8)
    
    # Calculate effective max tokens for code (accounting for prompt overhead)
    effective_max_tokens = max_input_tokens - prompt_token_estimate
    
    # Log the context settings
    logger.info(f"Model context length: {current_model_context_length}")
    logger.info(f"Max input tokens (80%): {max_input_tokens}")
    logger.info(f"Effective max tokens for code: {effective_max_tokens}")
    
    # Generate chunks using the hierarchical AST-aware chunking system
    chunks = chunk_codebase(base_dir, file_paths, file_contents)
    
    # Prepare the final prompts
    prepared_prompts = []
    for chunk in chunks:
        # Check if this chunk fits within our effective max tokens limit
        if chunk["token_count"] <= effective_max_tokens:
            # Create the prompt by substituting the code into the template
            prompt = prompt_template.replace("{code}", chunk["content"])
            
            prepared_prompts.append({
                "prompt": prompt,
                "chunk_id": chunk["chunk_id"],
                "files": chunk["files"],
                "token_count": chunk["token_count"] + prompt_token_estimate,
                "estimated_response_tokens": int(current_model_context_length * 0.2)
            })
        else:
            # This should rarely happen with proper chunking, but log it if it does
            logger.warning(
                f"Chunk {chunk['chunk_id']} exceeds max token limit "
                f"({chunk['token_count']} > {effective_max_tokens}). Skipping."
            )
    
    return prepared_prompts


def estimate_model_calls(file_paths: List[str], 
                        file_contents: Dict[str, str],
                        prompt_token_overhead: int = 200) -> Dict[str, Any]:
    """
    Estimate the number of LLM API calls needed for a codebase.
    
    Args:
        file_paths: List of file paths to process
        file_contents: Dict mapping file paths to their contents
        prompt_token_overhead: Estimated tokens in prompt templates
        
    Returns:
        Dictionary with estimation details
    """
    # Re-read environment variable at runtime to ensure latest value
    current_model_context_length = int(os.getenv("CURRENT_MODEL_CONTEXT_LENGTH", DEFAULT_MODEL_CONTEXT_LENGTH))
    max_input_tokens = int(current_model_context_length * 0.8)
    
    # Just get total code size for estimation
    total_chars = sum(len(content) for content in file_contents.values())
    total_files = len(file_paths)
    
    # Rough estimate: 1 token ≈ 4 characters for code
    estimated_tokens = total_chars / 4
    
    # Estimate number of chunks needed (assuming 80% of context length per chunk)
    effective_max_tokens = max_input_tokens - prompt_token_overhead
    estimated_chunks = max(1, int(estimated_tokens / effective_max_tokens) + 1)
    
    # Estimate total token usage including prompt overhead and response tokens
    total_input_tokens = estimated_tokens + (prompt_token_overhead * estimated_chunks)
    total_response_tokens = estimated_chunks * (current_model_context_length * 0.2)
    
    return {
        "files": total_files,
        "estimated_code_tokens": int(estimated_tokens),
        "estimated_chunks": estimated_chunks,
        "estimated_input_tokens": int(total_input_tokens),
        "estimated_response_tokens": int(total_response_tokens),
        "total_tokens": int(total_input_tokens + total_response_tokens),
        "model_context_length": current_model_context_length
    }


def batch_process_chunks(prepared_prompts: List[Dict[str, Any]], 
                        call_llm_func,
                        max_concurrent: int = 3,
                        use_cache: bool = False) -> List[Dict[str, Any]]:
    """
    Process chunks in batches, calling the LLM function for each.
    
    Args:
        prepared_prompts: List of prepared prompts from process_code_for_llm
        call_llm_func: Function to call with each prompt
        max_concurrent: Maximum number of concurrent LLM calls
        use_cache: Whether to use caching with the LLM calls
        
    Returns:
        List of results with prompt and response
    """
    # This function would orchestrate batch processing
    # For now, just process sequentially
    results = []
    
    for i, prompt_data in enumerate(prepared_prompts):
        logger.info(f"Processing chunk {i+1}/{len(prepared_prompts)}: {prompt_data['chunk_id']}")
        
        try:
            # Call the LLM with the prepared prompt
            response = call_llm_func(prompt_data["prompt"], use_cache=use_cache)
            
            # Store the result
            results.append({
                "chunk_id": prompt_data["chunk_id"],
                "files": prompt_data["files"],
                "prompt": prompt_data["prompt"],
                "response": response
            })
            
            logger.info(f"Successfully processed chunk {prompt_data['chunk_id']}")
            
        except Exception as e:
            logger.error(f"Error processing chunk {prompt_data['chunk_id']}: {e}")
            
            # Add a failure entry
            results.append({
                "chunk_id": prompt_data["chunk_id"],
                "files": prompt_data["files"],
                "prompt": prompt_data["prompt"],
                "error": str(e)
            })
    
    return results


# Example usage
if __name__ == "__main__":
    # This is just an example
    from utils.call_llm import call_llm
    
    example_files = {"example.py": "def hello(): print('Hello World')"}
    example_paths = ["example.py"]
    
    # Example prompt template
    template = "Analyze the following code:\n\n{code}\n\nProvide a detailed explanation."
    
    # Process the code
    prompts = process_code_for_llm(".", example_paths, example_files, template)
    
    # Use the call_llm function to process each prompt
    results = batch_process_chunks(prompts, call_llm)
    
    for result in results:
        print(f"Response for chunk {result['chunk_id']}:")
        print(result['response'])
