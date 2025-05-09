#!/usr/bin/env python3

import os
import json
import dotenv
from datetime import datetime
from groq import Groq
import time

# Load environment variables
dotenv.load_dotenv(override=True)

def print_separator(title):
    """Print a separator with a title for better readability."""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")

# Get configuration from environment variables
api_key = os.getenv("GROQ_API_KEY", "")
model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
stream = os.getenv("STREAM", "False").lower() in ["true", "1", "yes"]
use_system_prompt = os.getenv("USE_SYSTEM_PROMPT", "False").lower() in ["true", "1", "yes"]
system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

# The question to ask the LLM
question = "Why is the answer to life, the universe and everything? Explain your reasoning with in-depth and detailed information."

# Print configuration
print_separator("CONFIGURATION")
print(f"Provider: Groq")
print(f"Model: {model}")
print(f"Stream: {stream}")
print(f"Use System Prompt: {use_system_prompt}")
if use_system_prompt:
    print(f"System Prompt: {system_prompt[:50]}..." if len(system_prompt) > 50 else system_prompt)

# Check if API key is present
if not api_key:
    print("\nERROR: GROQ_API_KEY not found in environment variables.")
    print("Please set it in your .env file.")
    exit(1)

# Initialize Groq client
client = Groq(api_key=api_key)

# Prepare messages
messages = []
if use_system_prompt:
    messages.append({"role": "system", "content": system_prompt})
messages.append({"role": "user", "content": question})

# Print the request
print_separator("REQUEST")
request_data = {
    "model": model,
    "messages": messages,
    "stream": stream,
}
print(json.dumps(request_data, indent=2))

# Make the API call
try:
    print_separator("RESPONSE")
    start_time = datetime.now()
    
    print(f"Sending request to Groq API at {start_time.strftime('%H:%M:%S')}...")
    
    if stream:
        print("\nStreaming response:")
        full_response = ""
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)
        
        print("\n")  # Add newline after streaming
        response_text = full_response
        
    else:
        # Non-streaming call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )
        
        response_text = response.choices[0].message.content
        
        # Print full response for non-streaming mode
        print(response_text)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print response metadata
    print_separator("RESPONSE METADATA")
    print(f"Time taken: {duration:.2f} seconds")
    print(f"Response length: {len(response_text)} characters")
    
    if not stream and hasattr(response, "model"):
        print(f"Model used: {response.model}")
    
    if not stream and hasattr(response, "usage"):
        print(f"Token usage:")
        print(f"  - Prompt tokens: {response.usage.prompt_tokens}")
        print(f"  - Completion tokens: {response.usage.completion_tokens}")
        print(f"  - Total tokens: {response.usage.total_tokens}")
    
    # Get raw response
    if not stream:
        print_separator("RAW RESPONSE OBJECT")
        # Convert response object to dict, excluding non-serializable parts
        response_dict = {
            "id": response.id,
            "choices": [{
                "index": choice.index,
                "message": {
                    "role": choice.message.role,
                    "content": choice.message.content
                },
                "finish_reason": choice.finish_reason
            } for choice in response.choices],
            "created": response.created,
            "model": response.model if hasattr(response, "model") else model,
        }
        
        # Add usage if available
        if hasattr(response, "usage"):
            response_dict["usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
        print(json.dumps(response_dict, indent=2))

except Exception as e:
    print(f"\nERROR: {str(e)}")
    if 'invalid_api_key' in str(e).lower():
        print(f"\nThe API key provided seems to be invalid. Please check your GROQ_API_KEY.")
    elif 'rate limit' in str(e).lower():
        print(f"\nYou've hit a rate limit. Please try again later.")
    else:
        print(f"\nAn error occurred while calling the Groq API.")

if __name__ == "__main__":
    print_separator("DONE")
