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
Identify ALL distinct functional abstractions in this codebase to help those new to the codebase. Being exhaustive is critical - missing abstractions is worse than including minor ones.

NOTE: You are seeing only a portion of the codebase in this chunk. Identify ANY abstraction you can recognize, even if it seems incomplete. The goal is to capture ALL possible abstractions at multiple levels of granularity - from high-level architectural patterns down to significant utility functions, classes, or modules.

For each abstraction, provide:
1. A concise `name`{name_lang_hint}.
2. A "highly-technical" and "computer science" centric `description` explaining what it is with a real-world and practical analogy, in at least 300 words{desc_lang_hint}. Include all aspects of the abstraction, including edge cases and advanced usage patterns.
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

IMPORTANT GUIDANCE:
- Identify abstractions at ALL levels of granularity - architectural patterns, design patterns, services, components, significant classes, utility functions, etc.
- For any framework or technology stack, identify both technology-specific abstractions (e.g., services, components) and application-specific implementations
- Common abstraction categories to consider: Data models, Services/APIs, UI components, State management, Configuration, Utilities, Core logic, Domain entities, Controllers, Routing mechanisms, Authentication/Security, Event handling, etc.
- Do not limit yourself to a specific number of abstractions - identify ALL that you can find

CRITICAL INSTRUCTION: Your primary task is to identify MAXIMUM number of core abstractions of the application. You MUST NOT identify any form of software testing (including but not limited to unit tests, integration tests, end-to-end (E2E) tests, performance tests, etc.), testing frameworks, test runners, test utilities, or any code, files, or concepts primarily related to testing as an abstraction. If you encounter testing-related elements, ignore them for the purpose of abstraction identification. Focus exclusively on the application's runtime behavior, business logic, and core architectural components.

List of file indices and paths present in the context:
{file_listing_for_prompt}

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 list of dictionaries with NO explanatory text before or after
2. Do NOT include any explanation, discussion, or notes about the JSON structure
3. Do NOT describe what you're going to do - just provide the JSON5 directly
4. Your entire response must be parseable as valid JSON5
5. Start your response with the opening bracket "[" and end with the closing bracket "]"
6. Each dictionary must contain exactly these three keys: "name", "description", and "file_indices"
7. Use double curly braces {{ }} for the dictionary objects
8. Remember to escape all internal curly braces properly, especially in the description text

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

[
  {{
    "name": "Query Processing{name_lang_hint}",
    "description": "Explains what the abstraction does in detail, covering all aspects and edge cases. Include implementation details, usage patterns, and relationships with other abstractions. It's like a central dispatcher routing requests. Consider providing details about initialization, configuration, error handling, and performance aspects. Explain how it fits into the overall architecture.{desc_lang_hint}",
    "file_indices": [
      "0 # path/to/file1.py",
      "3 # path/to/related.py"
    ]
  }},
  {{
    "name": "Query Optimization{name_lang_hint}",
    "description": "Another core concept, similar to a blueprint for objects. Provide comprehensive details about its purpose, internal mechanisms, configuration options, and how other components interact with it.{desc_lang_hint}",
    "file_indices": [
      "5 # path/to/another.js"
    ]
  }}
  // ... include ALL distinct functional abstractions
]"""


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
2. A comprehensive list (`relationships`) describing ALL significant interactions between these abstractions. For each relationship, specify:
    - `from_abstraction`: Index of the source abstraction (e.g., `0 # AbstractionName1`)
    - `to_abstraction`: Index of the target abstraction (e.g., `1 # AbstractionName2`)
    - `label`: A brief, descriptive label for the interaction **in just a few words**{lang_hint}.

    Consider a WIDE VARIETY of technology-agnostic relationship types, such as:
    - Structural: "Is part of", "Contains", "Composes", "Is a component of"
    - Dependency: "Depends on", "Requires", "Is configured by", "Uses services from", "Consumes events from", "Produces events for"
    - Data Flow: "Manages data for", "Produces data for", "Consumes data from", "Provides data to"
    - Conceptual/Logical: "Specializes", "Implements", "Facilitates", "Orchestrates", "Coordinates with", "Is conceptually linked to"
    - Invocation/Control Flow: "Invokes", "Calls", "Triggers", "Controls"

    The relationship should ideally be backed by evidence in the provided code context or be a clear architectural or logical link between the abstractions.
    Be thorough in identifying ALL meaningful relationships, ensuring complete coverage of how abstractions interact.

IMPORTANT INSTRUCTIONS:
1. CRITICAL: EVERY abstraction listed MUST be involved in at least ONE meaningful relationship (either as a source or a target). Do NOT leave any abstraction isolated. If a direct interaction is not obvious, infer logical or conceptual connections based on their descriptions and roles in the system.
2. Each abstraction index (from 0 to {num_abstractions-1}) MUST appear at least once across all `from_abstraction` or `to_abstraction` fields.
3. Use ONLY the abstraction indices (0 to {num_abstractions-1}) from the list above. DO NOT use file indices or project names directly in the `from_abstraction` or `to_abstraction` fields.
4. The indices in `from_abstraction` and `to_abstraction` must be integers between 0 and {num_abstractions-1} inclusive, referencing the abstraction list.
5. Exclude any relationships that are solely testing-related. Do not focus on test frameworks, testing utilities, or test implementations when analyzing relationships.
6. Be COMPREHENSIVE and aim for completeness. It is better to include a less obvious but plausible conceptual relationship than to leave an abstraction disconnected.

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 object with NO explanatory text before or after
2. Do NOT include any explanation, discussion, or notes about the JSON structure
3. Do NOT describe what you're going to do - just provide the JSON5 directly
4. Your entire response must be parseable as valid JSON5
5. Start your response with the opening curly brace "{{" and end with the closing curly brace "}}"
6. The JSON5 object must contain exactly these two keys: "summary" and "relationships"
7. The "relationships" value must be an array of objects, each with "from_abstraction", "to_abstraction", and "label" keys

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

{{
  "summary": "A brief, simple explanation of the project{lang_hint}. Can span multiple lines with **bold** and *italic* for emphasis. IMPORTANT: This must be a single string value, not multiple strings.",
  "relationships": [
    {{
      "from_abstraction": "0 # AbstractionName1",
      "to_abstraction": "1 # AbstractionName2",
      "label": "Manages data for{lang_hint}"
    }},
    {{
      "from_abstraction": "2 # AbstractionName3",
      "to_abstraction": "0 # AbstractionName1",
      "label": "Is configured by{lang_hint}"
    }}
    // ... include ALL relationships between ALL abstractions
  ]
}}"""


def get_abstraction_relationship_completion_prompt(
    project_name,
    disconnected_abstractions,
    abstraction_listing,
    existing_relationships,
    language_instruction="",
    lang_hint=""
):
    """
    Generate a prompt for completing relationships for disconnected abstractions.
    
    Args:
        project_name: Name of the project
        disconnected_abstractions: List of disconnected abstraction details
        abstraction_listing: Full list of all abstractions
        existing_relationships: List of existing relationships for context
        language_instruction: Optional instruction for non-English output
        lang_hint: Optional language hint for outputs
        
    Returns:
        Formatted prompt string
    """
    return f"""
{language_instruction}Based on the abstractions in the project and the existing relationships already identified,
please generate SPECIFIC and CONCEPTUALLY MEANINGFUL relationships for each of these disconnected abstractions.

PROJECT CONTEXT: {project_name}

For each disconnected abstraction, create at least one relationship connecting it to another abstraction.
The relationship must be conceptually valid and reflect a real architectural connection.

Disconnected abstractions that need relationships:
{disconnected_abstractions}

Context from all abstractions:
{abstraction_listing}

Existing relationships for context:
{existing_relationships}

IMPORTANT GUIDANCE:
1. Create ONLY meaningful, technology-agnostic relationships based on the likely architectural roles of these abstractions
2. Each relationship should reflect a standard software architecture concept like:
   - STRUCTURAL: "Contains", "Is part of", "Composes", "Aggregates", "Consists of"
   - BEHAVIORAL: "Calls", "Triggers", "Notifies", "Delegates to", "Coordinates"
   - DEPENDENCY: "Depends on", "Uses", "Requires", "Leverages", "Consumes"
   - INHERITANCE: "Specializes", "Extends", "Implements", "Refines"
   - FUNCTIONAL: "Transforms", "Processes", "Validates", "Enriches", "Filters"
   - COMMUNICATION: "Sends data to", "Receives data from", "Exchanges information with"
3. Ensure relationships accurately reflect the software architecture domain rather than generic connections
4. Each abstraction must be connected to at least one other abstraction in a meaningful way
5. Be specific about each relationship type rather than using generic terms like "relates to"

Respond with ONLY a parseable JSON array containing the relationships with these three fields:
- from_abstraction: The source abstraction index and name (format: "0 # AbstractionName")
- to_abstraction: The target abstraction index and name (format: "1 # OtherAbstraction")
- label: A specific, technical relationship description{lang_hint} (e.g., "Provides configuration to", "Processes data from")

Here is the expected JSON format:
```json
[
  {{
    "from_abstraction": "5 # DisconnectedAbstraction",
    "to_abstraction": "2 # ConnectedAbstraction",
    "label": "Validates data for{lang_hint}"
  }},
  {{
    "from_abstraction": "8 # AnotherDisconnectedAbstraction",
    "to_abstraction": "5 # DisconnectedAbstraction",
    "label": "Composes{lang_hint}"
  }}
  // Include a relationship for EACH disconnected abstraction
]
```
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

If you are going to make a comprehensive tutorial for ```` {project_name} ````, what is the best order to explain these abstractions, from first to last?
Ideally, first explain those that are the most important or foundational, perhaps user-facing concepts or entry points. Then move to more detailed, lower-level implementation details or supporting concepts. Inspired by the "Tabulation" approach from Dynamic Programming.

Create a logical progression that maximizes learning effectiveness:
1. Start with core concepts that provide an architectural overview
2. Move to foundational abstractions that many other parts depend on
3. Cover major subsystems and their components
4. Address specialized or advanced abstractions that build on earlier concepts
5. Ensure that no abstraction is presented before the abstractions it depends on

IMPORTANT: Do not prioritize testing frameworks, test utilities, or any testing-related abstractions in your ordering. Focus on explaining the core functionality of the application rather than how to test it.

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 array with NO explanatory text before or after
2. Do NOT include any explanation, discussion, or notes about the JSON structure
3. Do NOT describe what you're going to do - just provide the JSON5 directly
4. Your entire response must be parseable as valid JSON5
5. Start your response with the opening bracket "[" and end with the closing bracket "]"
6. Each array element must be a string in the format "idx # AbstractionName"
7. Include ALL abstractions in your ordered list

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

[
  "2 # FoundationalConcept",
  "0 # CoreClassA",
  "1 # CoreClassB (uses CoreClassA)",
  // ... include ALL abstractions in the optimal learning order
]"""


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
{language_instruction}Write a comprehensive, in-depth tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

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
- Be STRICTLY LOSSLESS and COMPREHENSIVE - capture ALL aspects of this abstraction from the provided context/data.
- The chapter should be thorough and detailed, covering the abstraction from basic concepts to advanced usage patterns.
- **IMPORTANT**: Maintain a HIGHLY TECHNICAL writing style throughout. Readers are senior software developers who need in-depth technical explanations.

- Start with a clear heading (e.g., `# Chapter {chapter_num}: {abstraction_name}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter{instruction_lang_note}, referencing it with a proper Markdown link using its name{link_lang_note}.

- Begin with a problem statement section that:
  * Clearly articulates the technical challenge this abstraction solves{instruction_lang_note}
  * Explains the architectural consequences of NOT having this abstraction
  * Provides a concrete, technical example of the problem (with code if applicable)
  * Uses a real-world analogy but immediately connects it back to the technical domain

- For each major aspect of the abstraction, create dedicated technical sections that:
  * Begin with an H2/H3 heading clearly identifying the concept
  * Provide detailed technical explanations of internal mechanisms, not just surface-level behavior
  * Explain design patterns being applied (Singleton, Factory, Observer, etc.) with rationale
  * Discuss technical trade-offs made in the implementation ("This approach optimizes for X at the cost of Y")
  * Describe boundary conditions, edge cases, and error handling strategies
  * Explore performance characteristics and scalability considerations

- Include ALL relevant code examples for this abstraction from the codebase. For each code example:
  * Show complete implementation details with proper context
  * Annotate with line-by-line technical explanation of non-trivial aspects
  * Highlight key design patterns, idioms, or language features being leveraged
  * Note any optimizations or performance considerations
  * If multiple implementations exist, compare and contrast their technical merits

- Each code block should be COMPLETE! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Make the code Simple however don't loose clarity. Use comments{code_comment_note} to skip non-important implementation details. Each code block should have a senior software developer friendly explanation right after it{instruction_lang_note}.

- CRITICAL REQUIREMENT FOR BULLET POINTS: When using bullet points in your chapter, ALWAYS follow each bullet point with at least one detailed paragraph (5+ sentences) that thoroughly explains the technical aspects of that point. Never leave bullet points unexplained. For example:

  * Define entity relationships
    
    Entity relationships establish the formal connections between domain objects, implementing concepts like aggregation, composition, and association from object-oriented design. These relationships transcend mere references between objects, encoding cardinality constraints (one-to-many, many-to-many), cascading behaviors for persistence operations, and navigability rules that dictate traversal paths through the domain model. Well-defined relationships serve as the semantic foundation for data integrity rules, enabling the system to enforce business invariants through referential integrity constraints. They also inform how change propagation occurs throughout the system when state modifications happen to related entities.

- EXPLICITLY ENSURE all bullet points are expanded with detailed paragraphs. The detailed explanations should include:
  * Underlying theoretical computer science principles
  * Implementation considerations and technical trade-offs
  * Performance implications and optimization strategies 
  * Common design variations and their consequences
  * Language-agnostic explanations that focus on core concepts rather than specific syntax

- Describe the internal implementation to help understand what's under the hood{instruction_lang_note}. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called{instruction_lang_note}. It's recommended to use a detailed sequence diagram with mermaid syntax (`sequenceDiagram`) with a dummy example - include at least 5-8 participants to ensure proper representation of the flow. If participant name has space, use: `participant QP as Query Processing`. ALWAYS use proper mermaid syntax with `sequenceDiagram` at the beginning and the correct arrow syntax (e.g., use `->>` for messages, NOT `->`). Example: ```mermaid\nsequenceDiagram\n    participant A as ComponentA\n    participant B as ComponentB\n    A->>B: Request\n    B->>A: Response\n```{mermaid_lang_note}.

- Then dive deeper into code for the internal implementation with references to files. Provide explicit technical details on:
  * Initialization sequences and dependency management
  * Runtime behavior and control flow
  * Memory management considerations (if applicable)
  * Threading/concurrency concerns (if applicable)
  * How errors propagate through the system
  * Performance optimizations implemented (caching, lazy loading, etc.)

- IMPORTANT: Explicitly discuss how this abstraction interacts with EVERY other related abstraction. When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title{link_lang_note}. Translate the surrounding text.

- Cover ALL aspects of the abstraction, including edge cases and advanced usage patterns. Include technical sections on:
  * Core functionality and internal mechanisms (not just API surface)
  * Initialization and configuration with deep technical details
  * Error handling strategies and failure modes
  * Performance characteristics and optimization techniques
  * Integration patterns with other system components
  * Architectural patterns it implements (with detailed explanation of pattern implementation)
  * Known limitations or constraints and their technical reasons

- Include a technical best practices section that:
  * Identifies common pitfalls when using this abstraction
  * Provides optimized usage patterns for different scenarios
  * Discusses scaling considerations
  * Addresses any version-specific considerations or compatibility issues

- Use mermaid diagrams to illustrate complex concepts with PROPER mermaid syntax. ALWAYS begin with the diagram type (e.g., `sequenceDiagram`, `flowchart LR`, `classDiagram`, etc.) and use the correct syntax for that diagram type. For sequence diagrams, use proper arrow syntax like `->>`, `-->>`, `-->`, etc. NOT just `->`. For flowcharts, use proper node and connection syntax. Example with correct syntax: ```mermaid\nsequenceDiagram\n    participant A as ComponentA\n    participant B as ComponentB\n    A->>B: Request\n    B->>A: Response\n``` {mermaid_lang_note}.

- TECHNOLOGY AGNOSTICISM: Present all explanations in a way that emphasizes fundamental computer science principles that apply across languages and frameworks. When discussing implementations:
  * Focus on abstract patterns rather than specific syntax
  * Discuss the underlying algorithms and data structures
  * Explain architectural decisions in technology-neutral terms
  * Present multiple implementation approaches across different paradigms (OOP, functional, etc.)
  * Highlight universal principles that transcend specific technology stacks

- Heavily use real-world and practical analogies and examples throughout{instruction_lang_note} to help a Senior Software Developer understand, but ALWAYS follow analogies with detailed technical specifics.

- End the chapter with a technical conclusion that:
  * Summarizes the key technical insights about the abstraction
  * Highlights architectural patterns and principles demonstrated
  * Connects this abstraction to broader system architecture
  * Provides a transition to the next chapter{instruction_lang_note}. If there is a next chapter, use a proper Markdown link: [Next Chapter Title](next_chapter_filename){link_lang_note}.

- Ensure the tone is welcoming yet technically precise and substantive{tone_note}.

- IMPORTANT: DO NOT include any content related to unit tests, end-to-end (e2e) tests, integration tests, or any other types of testing in the tutorial. Skip all testing-related code and explanations. Focus exclusively on explaining the abstractions, concepts, and how to use them without any test coverage discussions.

- Output *only* the Markdown content for this chapter.

Now, directly provide a "technical" and "Computer Science"-friendly Markdown output (DON'T need ```markdown``` tags):
"""
