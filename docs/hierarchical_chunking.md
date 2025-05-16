# Hierarchical AST-aware Code Chunking System

## Overview

This system implements a sophisticated 5-level, hierarchical, AST-aware chunking strategy for large codebases. It preserves semantic structure when processing code for LLM analysis and ensures optimal token usage by:

1. Reserving 20% of the model's context length for responses
2. Limiting input chunks to 80% of the context length
3. Using tree-sitter to understand code structure at multiple levels

## Hierarchical Levels

The system divides code into 5 distinct hierarchical levels:

1. **Directory Level**: Project structure, grouping files by directory
2. **File Level**: Entire files viewed as coherent units
3. **Class/Module Level**: Classes, modules, namespaces, and other high-level structures
4. **Function/Method Level**: Functions, methods, and procedures
5. **Statement Level**: Individual statements, expressions, and code blocks

## Supported Languages

The system supports multiple languages through tree-sitter integration:

- Python
- Java
- Rust
- Go
- Scala
- Clojure
- TypeScript/JavaScript
- C#
- F#

## Configuration

The context length is configured through the environment variable:

```
CURRENT_MODEL_CONTEXT_LENGTH=8192  # Default if not specified
```

This value is used to:
- Reserve 20% for model responses (1,638 tokens for default 8192 context)
- Limit input to 80% of context (6,554 tokens for default 8192 context)

## Usage Example

```python
from utils.chunk_processor import process_code_for_llm, batch_process_chunks
from utils.call_llm import call_llm

# Prepare your file data
file_paths = ["path/to/file1.py", "path/to/file2.py"]
file_contents = {
    "path/to/file1.py": "def hello(): print('World')",
    "path/to/file2.py": "class Person:\n    def __init__(self, name):\n        self.name = name"
}

# Create a prompt template with {code} placeholder
prompt_template = "Analyze this code:\n\n{code}\n\nProvide insights."

# Process the code into optimal chunks
prepared_prompts = process_code_for_llm(
    base_dir=".", 
    file_paths=file_paths,
    file_contents=file_contents,
    prompt_template=prompt_template
)

# Send to LLM and get responses
results = batch_process_chunks(prepared_prompts, call_llm)

# Process results
for result in results:
    print(f"Analysis for chunk {result['chunk_id']}:")
    print(result['response'])
```

## Benefits

1. **Preserves Semantic Structure**: Chunks respect code boundaries like functions and classes
2. **Adaptive to Different Languages**: Language-specific parsing rules
3. **Overlapping Chunks**: Maintains context between chunks through intelligent overlap
4. **Optimal Token Usage**: Ensures no token waste while preserving code semantics
5. **Lossless Information**: By using AST awareness, no important code relationships are lost

## Implementation Details

The implementation follows the Adapter design pattern, making it easy to integrate with the existing LLM call system without modifying core functionality. It includes:

- `utils/code_chunking.py`: Core AST-aware chunking implementation
- `utils/chunk_processor.py`: Integration with LLM call system
- Environment variables: `CURRENT_MODEL_CONTEXT_LENGTH` for configuration

This system significantly improves code analysis quality by presenting code to LLMs in more semantically meaningful chunks.
