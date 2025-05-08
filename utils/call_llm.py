import os
import logging
import json
from datetime import datetime

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger

# Explicitly set encoding to utf-8 to handle all Unicode characters
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"


def call_llm(prompt: str, use_cache: bool = False) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")

    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")

        # Return from cache if exists
        if prompt in cache:
            logger.info(f"RESPONSE: {cache[prompt]}")
            return cache[prompt]

    # Call the Groq LLM API
    response_text = _call_groq(prompt)

        # Log the response
    logger.info(f"RESPONSE: {response_text}")

    # Update cache if enabled
    if use_cache:
        # Load cache again to avoid overwrites
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
            except:
                pass

        # Add to cache and save
        cache[prompt] = response_text
        try:
            with open(cache_file, "w") as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    return response_text


def _call_groq(prompt: str) -> str:
    """
    Call the Groq LLM API with the provided prompt
    """
    from groq import Groq
    import dotenv
    
    # Ensure environment variables are loaded
    dotenv.load_dotenv()
    
    # Get API key and model from environment variables
    api_key = os.getenv("GROQ_API_KEY", "")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not api_key:
        raise ValueError(
            "\nERROR: GROQ_API_KEY not found in environment variables.\n"
            "Please create a .env file in the project root with your Groq API key:\n"
            "GROQ_API_KEY=your_api_key_here\n"
            "\nIf you don't have a Groq API key, you can get one at https://console.groq.com/\n"
            "\nAlternatively, consider using a different model provider by setting MODEL_PROVIDER in your .env file."
        )
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    try:
        # Call the Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=model,
        )
        
        # Extract and return the response text
        return chat_completion.choices[0].message.content
    except Exception as e:
        if 'invalid_api_key' in str(e):
            raise ValueError(
                f"\nERROR: Invalid Groq API key. Please check your GROQ_API_KEY in the .env file.\n"
                f"The key you provided starts with: {api_key[:4]}... (length: {len(api_key)})\n"
                f"\nIf you recently created this key, it might take a few minutes to activate.\n"
                f"\nOriginal error: {str(e)}"
            )
        else:
            # Re-raise other exceptions
            raise




# Use OpenRouter API
# def call_llm(prompt: str, use_cache: bool = False) -> str:
#     # Log the prompt
#     logger.info(f"PROMPT: {prompt}")

#     # Check cache if enabled
#     if use_cache:
#         # Load cache from disk
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r") as f:
#                     cache = json.load(f)
#             except:
#                 logger.warning(f"Failed to load cache, starting with empty cache")

#         # Return from cache if exists
#         if prompt in cache:
#             logger.info(f"RESPONSE: {cache[prompt]}")
#             return cache[prompt]

#     # OpenRouter API configuration
#     api_key = os.getenv("OPENROUTER_API_KEY", "")
#     model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#     }

#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     response = requests.post(
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers=headers,
#         json=data
#     )

#     if response.status_code != 200:
#         error_msg = f"OpenRouter API call failed with status {response.status_code}: {response.text}"
#         logger.error(error_msg)
#         raise Exception(error_msg)
#     try:
#         response_text = response.json()["choices"][0]["message"]["content"]
#     except Exception as e:
#         error_msg = f"Failed to parse OpenRouter response: {e}; Response: {response.text}"
#         logger.error(error_msg)        
#         raise Exception(error_msg)
    

#     # Log the response
#     logger.info(f"RESPONSE: {response_text}")

#     # Update cache if enabled
#     if use_cache:
#         # Load cache again to avoid overwrites
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r") as f:
#                     cache = json.load(f)
#             except:
#                 pass

#         # Add to cache and save
#         cache[prompt] = response_text
#         try:
#             with open(cache_file, "w") as f:
#                 json.dump(cache, f)
#         except Exception as e:
#             logger.error(f"Failed to save cache: {e}")

#     return response_text

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"

    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
