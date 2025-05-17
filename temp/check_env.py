import os
from dotenv import load_dotenv
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env file
load_dotenv(override=True)

# Try to get the environment variable
context_length = os.getenv("CURRENT_MODEL_CONTEXT_LENGTH")
print(f"CURRENT_MODEL_CONTEXT_LENGTH: {context_length}")

# Check all environment variables to see if the variable exists with a different case
env_vars = os.environ
for key, value in env_vars.items():
    if "MODEL" in key.upper() and "CONTEXT" in key.upper():
        print(f"{key}: {value}")

try:
    # Now try importing from utils.code_chunking
    from utils.code_chunking import DEFAULT_MODEL_CONTEXT_LENGTH, MODEL_CONTEXT_LENGTH
    print(f"DEFAULT_MODEL_CONTEXT_LENGTH: {DEFAULT_MODEL_CONTEXT_LENGTH}")
    print(f"MODEL_CONTEXT_LENGTH: {MODEL_CONTEXT_LENGTH}")
except ImportError as e:
    print(f"Error importing: {e}") 