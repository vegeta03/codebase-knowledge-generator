import re
import json5
from utils.code_chunking import get_model_context_length, get_max_input_tokens

def clean_llm_response(response: str) -> str:
    """
    Clean LLM response by removing <think></think> tags and other artifacts.
    
    Args:
        response: The raw LLM response to clean
        
    Returns:
        Cleaned response with thinking tags removed
    """
    # Remove <think>...</think> blocks
    clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
    # Remove possible trailing/leading whitespace from the cleaning
    clean_response = clean_response.strip()
    
    # If the response is now empty (entire response was inside think tags), 
    # return the original (this shouldn't happen with proper LLM behavior)
    if not clean_response and response:
        print("Warning: Entire response was inside <think> tags. Using original response.")
        return response
        
    return clean_response

def extract_json_from_response(response: str) -> str:
    """
    Extract JSON content from an LLM response.
    
    Args:
        response: The LLM response, potentially containing JSON code blocks
        
    Returns:
        The extracted JSON as a string
    """
    # First, clean any thinking tags from the response
    response = clean_llm_response(response)
    
    # Look for JSON/JSON5 in code blocks (improved pattern matching)
    json_match = re.search(r'```(?:json5?|jsonc?)\s*(.+?)\s*```', response, flags=re.DOTALL)
    if json_match:
        # Found JSON in a code block
        return json_match.group(1).strip()
        
    # If no code block, try to find a JSON object with curly braces
    json_obj_match = re.search(r'({[\s\S]*})', response, flags=re.DOTALL)
    if json_obj_match:
        return json_obj_match.group(1).strip()
    
    # Look for JSON arrays starting with [ and ending with ]
    array_match = re.search(r'(\[\s*(?:{.+}|\".+\")\s*(?:,\s*(?:{.+}|\".+\")\s*)*\])', response, flags=re.DOTALL)
    if array_match:
        return array_match.group(1).strip()
            
    # If still nothing found, assume the entire (cleaned) response is JSON
    return response.strip()

def test_think_tag_removal():
    # Test cases
    test_cases = [
        {
            "name": "Simple response with think tags",
            "input": "Hello world<think>This is my thought process</think>",
            "expected": "Hello world"
        },
        {
            "name": "Multiple think tags",
            "input": "<think>Initial thinking</think>Result<think>More thinking</think>",
            "expected": "Result"
        },
        {
            "name": "No think tags",
            "input": "Just a normal response",
            "expected": "Just a normal response"
        },
        {
            "name": "Multiline think tags",
            "input": "Start of content\n<think>\nThis is\nmultiline\nthinking\n</think>\nActual content",
            "expected": "Start of content\n\nActual content"
        },
        {
            "name": "JSON with think tags",
            "input": "```json\n<think>Thinking about JSON format</think>{\n  \"name\": \"value\"\n}\n```",
            "expected": "```json\n{\n  \"name\": \"value\"\n}\n```"
        },
        {
            "name": "Entire response is think tag",
            "input": "<think>This is all thinking</think>",
            "expected": "<think>This is all thinking</think>"  # Should return original if all is in think tags
        },
        {
            "name": "JSON extraction from response with think tags",
            "input": "<think>Let me think about the proper JSON format...</think>\n```json\n{\n  \"data\": [1, 2, 3]\n}\n```",
            "expected_json": "{\n  \"data\": [1, 2, 3]\n}"
        },
        {
            "name": "JSON5 extraction with think tags",
            "input": "Here's the JSON5 data: <think>Should I add comments?</think>\n```json5\n{\n  // This is a comment\n  data: [1, 2, 3],\n}\n```",
            "expected_json": "{\n  // This is a comment\n  data: [1, 2, 3],\n}"
        }
    ]
    
    # Run tests
    for i, test in enumerate(test_cases):
        print(f"Test {i+1}: {test['name']}")
        
        cleaned = clean_llm_response(test["input"])
        print(f"  Input: {test['input'][:50]}{'...' if len(test['input']) > 50 else ''}")
        print(f"  Cleaned: {cleaned[:50]}{'...' if len(cleaned) > 50 else ''}")
        
        if "expected" in test:
            success = cleaned == test["expected"]
            print(f"  Success: {success}")
            if not success:
                print(f"  Expected: {test['expected'][:50]}{'...' if len(test['expected']) > 50 else ''}")
        
        if "expected_json" in test:
            extracted = extract_json_from_response(test["input"])
            json_success = extracted == test["expected_json"]
            print(f"  JSON extraction success: {json_success}")
            if not json_success:
                print(f"  Extracted: {extracted[:50]}{'...' if len(extracted) > 50 else ''}")
                print(f"  Expected JSON: {test['expected_json'][:50]}{'...' if len(test['expected_json']) > 50 else ''}")
        
        print()
    
    # Also verify model context settings
    print(f"Model context length: {get_model_context_length()}")
    print(f"Max input tokens (80%): {get_max_input_tokens()}")
    print(f"Reserved for response (20%): {get_model_context_length() - get_max_input_tokens()}")
    
    # Calculate percentages
    max_input_percentage = (get_max_input_tokens() / get_model_context_length()) * 100
    response_percentage = 100 - max_input_percentage
    
    print(f"Input percentage: {max_input_percentage:.1f}%")
    print(f"Response percentage: {response_percentage:.1f}%")
    
    return True

if __name__ == "__main__":
    print("Testing <think></think> tag removal functionality...")
    test_think_tag_removal()
    print("Tests completed!") 