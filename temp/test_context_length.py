"""
Test script to verify model context length
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_context")

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_context_length():
    """Test context length reading"""
    # Print environment value
    print(f"Environment CURRENT_MODEL_CONTEXT_LENGTH: {os.getenv('CURRENT_MODEL_CONTEXT_LENGTH')}")
    
    # Import after setting up path
    from utils.code_chunking import (
        DEFAULT_MODEL_CONTEXT_LENGTH,
        MODEL_CONTEXT_LENGTH,
        MAX_INPUT_TOKENS,
        get_model_context_length,
        get_max_input_tokens
    )
    
    # Print initial values from module
    print(f"DEFAULT_MODEL_CONTEXT_LENGTH: {DEFAULT_MODEL_CONTEXT_LENGTH}")
    print(f"MODEL_CONTEXT_LENGTH (initial): {MODEL_CONTEXT_LENGTH}")
    print(f"MAX_INPUT_TOKENS (initial): {MAX_INPUT_TOKENS}")
    
    # Get current values from getter functions
    current_context_length = get_model_context_length()
    current_max_tokens = get_max_input_tokens()
    
    print(f"get_model_context_length(): {current_context_length}")
    print(f"get_max_input_tokens(): {current_max_tokens}")
    
    # Test chunk processor
    from utils.chunk_processor import process_code_for_llm
    
    # Create a simple example
    example_files = {"example.py": "def hello(): print('Hello World')"}
    example_paths = ["example.py"]
    template = "Analyze: {code}"
    
    # Process code - this should log the current context length
    print("\nCalling process_code_for_llm (check logs):")
    prompts = process_code_for_llm(".", example_paths, example_files, template)
    
    # Print values from the first prompt
    if prompts:
        print(f"\nFrom first prompt:")
        print(f"estimated_response_tokens: {prompts[0]['estimated_response_tokens']}")
        est_context = prompts[0]['estimated_response_tokens'] / 0.2
        print(f"Implied context length: {est_context}")
    
if __name__ == "__main__":
    test_context_length() 