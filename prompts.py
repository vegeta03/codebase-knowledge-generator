"""
Contains all the prompts used in the tutorial generation process.

This module centralizes all LLM prompts used throughout the codebase to ensure a single source of truth
and facilitate easy modifications. Prompts are organized by the node they belong to and structured as
functions that handle any variable substitution needed.
"""

def get_identify_abstractions_prompt(
    project_name,
    context,
    file_listing_for_prompt,
    language_instruction="",
    name_lang_hint="",
    desc_lang_hint=""
):
    """
    Generate the prompt for identifying key abstractions in the codebase.
    
    Args:
        project_name: Name of the project
        context: The codebase content
        file_listing_for_prompt: Formatted list of file indices and paths
        language_instruction: Optional instruction for non-English output
        name_lang_hint: Optional language hint for abstraction names
        desc_lang_hint: Optional language hint for descriptions
        
    Returns:
        Formatted prompt string
    """
    return f"""
For the project `{project_name}`:

Codebase Context:
{context}

{language_instruction}Analyze the codebase context.
Identify the complete and comprehensive core most important abstractions to help those new to the codebase.

For each abstraction, provide:
1. A concise `name`{name_lang_hint}.
2. A "technical" and "computer science" centric `description` explaining what it is with a real-world and practical analogy, in atleast 100 words or more if required{desc_lang_hint}.
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

CRITICAL INSTRUCTION: Your primary task is to identify maximum number of core functional abstractions of the application. You MUST NOT identify any form of software testing (including but not limited to unit tests, integration tests, end-to-end (E2E) tests, performance tests, etc.), testing frameworks, test runners, test utilities, or any code, files, or concepts primarily related to testing as an abstraction. If you encounter testing-related elements, ignore them for the purpose of abstraction identification. Focus exclusively on the application's runtime behavior, business logic, and core architectural components.

List of file indices and paths present in the context:
{file_listing_for_prompt}

Format the output as a JSON5 list of dictionaries:

```json5
[
  {{
    "name": "Query Processing{name_lang_hint}",
    "description": "Explains what the abstraction does.\nIt's like a central dispatcher routing requests.{desc_lang_hint}",
    "file_indices": [
      "0 # path/to/file1.py",
      "3 # path/to/related.py"
    ]
  }},
  {{
    "name": "Query Optimization{name_lang_hint}",
    "description": "Another core concept, similar to a blueprint for objects.{desc_lang_hint}",
    "file_indices": [
      "5 # path/to/another.js"
    ]
  }}
  // ... include all complete and comprehensive core most important abstractions
]
```"""


def get_analyze_relationships_prompt(
    project_name,
    abstraction_listing,
    context,
    num_abstractions,
    language_instruction="",
    lang_hint="",
    list_lang_note=""
):
    """
    Generate the prompt for analyzing relationships between abstractions.
    
    Args:
        project_name: Name of the project
        abstraction_listing: Formatted list of abstraction indices and names
        context: The abstraction details and code snippets
        num_abstractions: Number of abstractions
        language_instruction: Optional instruction for non-English output
        lang_hint: Optional language hint for summary and labels
        list_lang_note: Optional language note for the input list
        
    Returns:
        Formatted prompt string
    """
    return f"""
Based on the following abstractions and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions, Descriptions, Code):
{context}

{language_instruction}Please provide:
1. A high-level `summary` of the project's main purpose and functionality in a short "technical" and "computer science" friendly sentences{lang_hint}. Use markdown formatting with **bold** and *italic* text to highlight important concepts.
2. A list (`relationships`) describing the key interactions between these abstractions. For each relationship, specify:
    - `from_abstraction`: Index of the source abstraction (e.g., `0 # AbstractionName1`)
    - `to_abstraction`: Index of the target abstraction (e.g., `1 # AbstractionName2`)
    - `label`: A brief label for the interaction **in just a few words**{lang_hint} (e.g., "Manages", "Inherits", "Uses").
    Ideally the relationship should be backed by one abstraction calling or passing parameters to another.
    Make the relationship Simple but don't dilute it while doing so and exclude those non-important ones.

IMPORTANT INSTRUCTIONS:
1. Make sure EVERY abstraction is involved in at least ONE relationship (either as source or target).
2. Each abstraction index must appear at least once across all relationships.
3. Use ONLY the abstraction indices (0 to {num_abstractions-1}) from the list above, NOT file indices.
4. Do NOT use file indices or project names in the relationships.
5. The indices in from_abstraction and to_abstraction must be between 0 and {num_abstractions-1} inclusive.
6. Exclude any relationships that are solely testing-related. Do not focus on test frameworks, testing utilities, or test implementations when analyzing relationships.

Format the output as JSON5:

```json5
{{
  "summary": "A brief, simple explanation of the project{lang_hint}. Can span multiple lines with **bold** and *italic* for emphasis. IMPORTANT: This must be a single string value, not multiple strings.",
  "relationships": [
    {{
      "from_abstraction": "0 # AbstractionName1",
      "to_abstraction": "1 # AbstractionName2",
      "label": "Manages{lang_hint}"
    }},
    {{
      "from_abstraction": "2 # AbstractionName3",
      "to_abstraction": "0 # AbstractionName1",
      "label": "Provides config{lang_hint}"
    }}
    // ... other relationships
  ]
}}
```

Now, provide the JSON5 output:
"""


def get_order_chapters_prompt(
    project_name,
    abstraction_listing,
    context,
    list_lang_note=""
):
    """
    Generate the prompt for determining the chapter order.
    
    Args:
        project_name: Name of the project
        abstraction_listing: Formatted list of abstraction indices and names
        context: Context about relationships and project summary
        list_lang_note: Optional language note for the input list
        
    Returns:
        Formatted prompt string
    """
    return f"""
Given the following project abstractions and their relationships for the project ```` {project_name} ````:

Abstractions (Index # Name){list_lang_note}:
{abstraction_listing}

Context about relationships and project summary:
{context}

If you are going to make a tutorial for ```` {project_name} ````, what is the best order to explain these abstractions, from first to last?
Ideally, first explain those that are the most important or foundational, perhaps user-facing concepts or entry points. Then move to more detailed, lower-level implementation details or supporting concepts.

IMPORTANT: Do not prioritize testing frameworks, test utilities, or any testing-related abstractions in your ordering. Focus on explaining the core functionality of the application rather than how to test it.

Output the ordered list of abstraction indices, including the name in a comment for clarity. Use the format `idx # AbstractionName`.

```json5
[
  "2 # FoundationalConcept",
  "0 # CoreClassA",
  "1 # CoreClassB (uses CoreClassA)",
  // ...
]
```

Now, provide the JSON5 output:
"""


def get_write_chapter_prompt(
    project_name,
    chapter_num,
    abstraction_name,
    abstraction_description,
    full_chapter_listing,
    file_context_str,
    previous_chapters_summary,
    language_instruction="",
    concept_details_note="",
    structure_note="",
    prev_summary_note="",
    instruction_lang_note="",
    mermaid_lang_note="",
    code_comment_note="",
    link_lang_note="",
    tone_note="",
    language="english"
):
    """
    Generate the prompt for writing an individual chapter.
    
    Args:
        project_name: Name of the project
        chapter_num: Current chapter number
        abstraction_name: Name of the abstraction
        abstraction_description: Description of the abstraction
        full_chapter_listing: Complete list of chapters
        file_context_str: Relevant code snippets
        previous_chapters_summary: Summary of previous chapters
        language_instruction: Optional instruction for non-English output
        concept_details_note: Optional language note for concept details
        structure_note: Optional language note for tutorial structure
        prev_summary_note: Optional language note for previous chapters
        instruction_lang_note: Optional language hint for instructions
        mermaid_lang_note: Optional language hint for mermaid diagrams
        code_comment_note: Optional language hint for code comments
        link_lang_note: Optional language hint for links
        tone_note: Optional language hint for tone
        language: Target language
        
    Returns:
        Formatted prompt string
    """
    return f"""
{language_instruction}Write a software developer friendly tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

Concept Details{concept_details_note}:
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note}:
{full_chapter_listing}

Context from previous chapters{prev_summary_note}:
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}

Relevant Code Snippets (Code itself remains unchanged):
{file_context_str if file_context_str else "No specific code snippets provided for this abstraction."}

Instructions for the chapter (Generate content in {language.capitalize()} unless specified otherwise):
- Start with a clear heading (e.g., `# Chapter {chapter_num}: {abstraction_name}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter{instruction_lang_note}, referencing it with a proper Markdown link using its name{link_lang_note}.

- Begin with a high-level motivation explaining what problem this abstraction solves{instruction_lang_note}. Start with a central use case as a concrete example. The whole chapter should guide the reader to understand how to solve this use case. Make it very comprehensive and very understandable to a Senior Software Developer.

- If the abstraction is complex, break it down into key concepts. Explain each concept one-by-one in a very beginner-friendly way{instruction_lang_note}.

- Explain how to use this abstraction to solve the use case{instruction_lang_note}. Give example inputs and outputs for code snippets (if the output isn't values, describe at a high level what will happen{instruction_lang_note}).

- Each code block should be COMPLETE! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Make the code Simple however don't loose clarity. Use comments{code_comment_note} to skip non-important implementation details. Each code block should have a senior software developer friendly explanation right after it{instruction_lang_note}.

- Describe the internal implementation to help understand what's under the hood{instruction_lang_note}. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called{instruction_lang_note}. It's recommended to use a simple sequence diagram with mermaid syntax (`sequenceDiagram`) with a dummy example - keep it minimal with at least 5 participants to ensure clarity. If participant name has space, use: `participant QP as Query Processing`. ALWAYS use proper mermaid syntax with `sequenceDiagram` at the beginning and the correct arrow syntax (e.g., use `->>` for messages, NOT `->`). Example: ```mermaid\nsequenceDiagram\n    participant A as ComponentA\n    participant B as ComponentB\n    A->>B: Request\n    B->>A: Response\n```{mermaid_lang_note}.

- Then dive deeper into code for the internal implementation with references to files. Provide example code blocks, but make them similarly simple however don't dilute it, and "Computer Science"-friendly. Explain{instruction_lang_note}.

- IMPORTANT: When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title{link_lang_note}. Translate the surrounding text.

- Use mermaid diagrams to illustrate complex concepts with PROPER mermaid syntax. ALWAYS begin with the diagram type (e.g., `sequenceDiagram`, `flowchart LR`, `classDiagram`, etc.) and use the correct syntax for that diagram type. For sequence diagrams, use proper arrow syntax like `->>`, `-->>`, `-->`, etc. NOT just `->`. For flowcharts, use proper node and connection syntax. Example with correct syntax: ```mermaid\nsequenceDiagram\n    participant A as ComponentA\n    participant B as ComponentB\n    A->>B: Request\n    B->>A: Response\n``` {mermaid_lang_note}.

- Heavily use real-world and practical analogies and examples throughout{instruction_lang_note} to help a Senior Software Developer understand.

- End the chapter with a brief conclusion that summarizes what was learned{instruction_lang_note} and provides a transition to the next chapter{instruction_lang_note}. If there is a next chapter, use a proper Markdown link: [Next Chapter Title](next_chapter_filename){link_lang_note}.

- Ensure the tone is welcoming and easy for a seasoned sofware developer professional to understand{tone_note}.

- IMPORTANT: DO NOT include any content related to unit tests, end-to-end (e2e) tests, integration tests, or any other types of testing in the tutorial. Skip all testing-related code and explanations. Focus exclusively on explaining the abstractions, concepts, and how to use them without any test coverage discussions.

- Output *only* the Markdown content for this chapter.

Now, directly provide a "technical" and "Computer Science"-friendly Markdown output (DON'T need ```markdown``` tags):
"""
