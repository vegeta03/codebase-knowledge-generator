import os

# Print the environment variable value
context_length = os.getenv("CURRENT_MODEL_CONTEXT_LENGTH")
print(f"CURRENT_MODEL_CONTEXT_LENGTH: {context_length}")

# Print all environment variables with MODEL or CONTEXT in their name
for key, value in os.environ.items():
    if "MODEL" in key.upper() and "CONTEXT" in key.upper():
        print(f"{key}: {value}") 