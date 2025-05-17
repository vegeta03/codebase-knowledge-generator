import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variable
os.environ["CURRENT_MODEL_CONTEXT_LENGTH"] = "128000"

# Import functions from code_chunking
from utils.code_chunking import (
    get_model_context_length,
    get_max_input_tokens,
    DEFAULT_MODEL_CONTEXT_LENGTH,
    MODEL_CONTEXT_LENGTH,
    MAX_INPUT_TOKENS
)

# Print values
print(f"Environment value: {os.getenv('CURRENT_MODEL_CONTEXT_LENGTH')}")
print(f"DEFAULT_MODEL_CONTEXT_LENGTH: {DEFAULT_MODEL_CONTEXT_LENGTH}")
print(f"MODEL_CONTEXT_LENGTH (initial): {MODEL_CONTEXT_LENGTH}")
print(f"MAX_INPUT_TOKENS (initial): {MAX_INPUT_TOKENS}")
print(f"get_model_context_length(): {get_model_context_length()}")
print(f"get_max_input_tokens(): {get_max_input_tokens()}")
print(f"80% of 128000: {128000 * 0.8}")

# Import chunk_processor
from utils.chunk_processor import MODEL_CONTEXT_LENGTH as CP_MODEL_CONTEXT_LENGTH
print(f"chunk_processor.MODEL_CONTEXT_LENGTH: {CP_MODEL_CONTEXT_LENGTH}") 