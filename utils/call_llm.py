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
    # Get the root logger to check if verbose mode is enabled
    root_logger = logging.getLogger()
    is_verbose = root_logger.level <= logging.DEBUG
    
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")
    if is_verbose:
        print(f"\nSending prompt to LLM (length: {len(prompt)} chars)")
        if len(prompt) > 500:
            # Show truncated prompt in verbose mode for readability
            print(f"Truncated prompt preview: {prompt[:250]}...{prompt[-250:]}")
        else:
            print(f"Full prompt: {prompt}")

    # Check cache if enabled
    if use_cache:
        if is_verbose:
            print("LLM caching is enabled, checking for cached response...")
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
                if is_verbose:
                    print(f"Loaded cache with {len(cache)} entries")
            except Exception as e:
                error_msg = f"Failed to load cache: {str(e)}"
                logger.warning(error_msg)
                if is_verbose:
                    print(error_msg)

        # Return from cache if exists
        if prompt in cache:
            if is_verbose:
                print("Cache hit! Using cached response")
            logger.info(f"RESPONSE: {cache[prompt]}")
            return cache[prompt]
        elif is_verbose:
            print("Cache miss. Calling LLM API...")

    # Check which model provider to use
    model_provider = os.getenv("MODEL_PROVIDER", "groq").lower()
    
    # Check if streaming is enabled
    stream = os.getenv("STREAM", "False").lower() in ["true", "1", "yes"]
    if is_verbose and stream:
        print("Streaming mode is enabled")
    
    # Determine which model will be used based on provider
    if model_provider == "openrouter":
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
        print(f"🔄 LLM API Call: Provider=[OpenRouter] Model=[{model}] Stream=[{stream}]")
        response_text = _call_openrouter(prompt, stream=stream)
    else:  # Default to groq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        print(f"🔄 LLM API Call: Provider=[Groq] Model=[{model}] Stream=[{stream}]")
        response_text = _call_groq(prompt, stream=stream)
        
    if is_verbose:
        print(f"Additional debug info - Using model provider: {model_provider}")

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


def _call_groq(prompt: str, stream: bool = False) -> str:
    """
    Call the Groq LLM API with the provided prompt
    """
    from groq import Groq
    import dotenv
    import sys
    
    # Ensure environment variables are loaded
    dotenv.load_dotenv(override=True)
    
    # Check if verbose mode is enabled
    root_logger = logging.getLogger()
    is_verbose = root_logger.level <= logging.DEBUG
    
    # Get API key and model from environment variables
    api_key = os.getenv("GROQ_API_KEY", "")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if is_verbose:
        print(f"Using Groq LLM model: {model}")
        print(f"Streaming mode: {'Enabled' if stream else 'Disabled'}")
        # Check API key format without revealing the full key
        if api_key:
            print(f"API key found. Key starts with: {api_key[:4]}... (length: {len(api_key)})")
        else:
            print("WARNING: No API key found in environment variables.")
    
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
        if is_verbose:
            print("Sending request to Groq API...")
            start_time = datetime.now()
        
        # Handle streaming differently if enabled
        if stream:
            full_response = ""
            # Using streaming API
            stream_response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model,
                stream=True
            )
            
            # Process the stream
            print("Receiving streamed response:")
            for chunk in stream_response:
                # Extract content from the chunk
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # Print the chunk content to the console
                    print(content, end="", flush=True)
            
            # Add a newline after the streamed response
            print()
            response = full_response
        else:
            # Non-streaming API call
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model,
            )
            
            # Extract and return the response text
            response = chat_completion.choices[0].message.content
        
        # Calculate and log response time in verbose mode
        if is_verbose:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"Received {'streamed ' if stream else ''}response from Groq API in {duration:.2f} seconds")
            print(f"Response length: {len(response)} characters")
            if len(response) > 500 and not stream:
                # Show truncated response in verbose mode for readability (only if not streamed)
                print(f"Truncated response preview: {response[:250]}...{response[-250:]}")
        
        return response
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




def _call_openrouter(prompt: str, stream: bool = False) -> str:
    """
    Call the OpenRouter API using the OpenAI SDK with the provided prompt
    Can use streaming if the stream parameter is True
    """
    from openai import OpenAI
    import dotenv
    import sys
    
    # Ensure environment variables are loaded
    dotenv.load_dotenv(override=True)
    
    # Check if verbose mode is enabled
    root_logger = logging.getLogger()
    is_verbose = root_logger.level <= logging.DEBUG
    
    # Get API key and model from environment variables
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
    
    if is_verbose:
        print(f"Using OpenRouter with model: {model}")
        print(f"Streaming mode: {'Enabled' if stream else 'Disabled'}")
        # Check API key format without revealing the full key
        if api_key:
            print(f"API key found. Key starts with: {api_key[:4]}... (length: {len(api_key)})")
        else:
            print("WARNING: No API key found in environment variables.")
    
    if not api_key:
        raise ValueError(
            "\nERROR: OPENROUTER_API_KEY not found in environment variables.\n"
            "Please create a .env file in the project root with your OpenRouter API key:\n"
            "OPENROUTER_API_KEY=your_api_key_here\n"
            "OPENROUTER_MODEL=openai/gpt-4o (or another model ID)\n"
            "\nIf you don't have an OpenRouter API key, you can get one at https://openrouter.ai/\n"
            "\nAlternatively, consider using a different model provider by setting MODEL_PROVIDER in your .env file."
        )
    
    # Initialize OpenAI client with OpenRouter base URL
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    try:
        # Call the OpenRouter API via OpenAI SDK
        if is_verbose:
            print("Sending request to OpenRouter API...")
            start_time = datetime.now()
        
        # No extra headers needed for basic functionality
        # OpenRouter will still work without site information
        extra_headers = {}
        
        # Handle streaming differently if enabled
        if stream:
            full_response = ""
            # Using streaming API
            stream_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                extra_headers=extra_headers
            )
            
            # Process the stream
            print("Receiving streamed response:")
            for chunk in stream_response:
                # Extract content from the chunk
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # Print the chunk content to the console
                    print(content, end="", flush=True)
            
            # Add a newline after the streamed response
            print()
            response = full_response
        else:
            # Non-streaming API call
            chat_completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers=extra_headers
            )
            
            # Extract and return the response text
            response = chat_completion.choices[0].message.content
        
        # Calculate and log response time in verbose mode
        if is_verbose:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"Received {'streamed ' if stream else ''}response from OpenRouter API in {duration:.2f} seconds")
            # Log which model was actually used if not streaming (not available in streaming response)
            if not stream and hasattr(chat_completion, 'model'):
                print(f"Model used: {chat_completion.model}")
            
            print(f"Response length: {len(response)} characters")
            if len(response) > 500 and not stream:
                # Show truncated response in verbose mode for readability (only if not streamed)
                print(f"Truncated response preview: {response[:250]}...{response[-250:]}")
        
        return response
    except Exception as e:
        if 'invalid_api_key' in str(e) or 'authentication' in str(e).lower():
            raise ValueError(
                f"\nERROR: Invalid OpenRouter API key. Please check your OPENROUTER_API_KEY in the .env file.\n"
                f"The key you provided starts with: {api_key[:4]}... (length: {len(api_key)})\n"
                f"\nOriginal error: {str(e)}"
            )
        elif 'model_not_found' in str(e) or 'model' in str(e).lower() and 'not' in str(e).lower():
            raise ValueError(
                f"\nERROR: Model '{model}' not found or not available. Please check your OPENROUTER_MODEL in the .env file.\n"
                f"\nOriginal error: {str(e)}"
            )
        else:
            # Re-raise other exceptions
            raise

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
