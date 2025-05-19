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

Codebase Context (a portion of the overall codebase):
{context}

{language_instruction}Based on the provided Codebase Context, your primary task is to **DYNAMICALLY IDENTIFY** the specific programming languages, frameworks, libraries, architectural patterns (e.g., microservices, event-driven, layered), and core Computer Science principles (e.g., specific algorithms, data structures, concurrency models) evident in this portion of the code. Then, using this identified technological context, identify ALL distinct and significant abstractions.

Abstractions can include (but are not limited to):
- Key architectural components (e.g., services, controllers, repositories, domain entities if an ORM or DDD is identified).
- Instantiations of common design patterns (e.g., Factory, Singleton, Observer, Strategy - explain how the pattern is specifically implemented with the identified language/framework features).
- Core algorithms or complex business logic units.
- Significant data structures and their management.
- Primary modules, classes, or interfaces that play a crucial role.
- Critical operational flows or processing pipelines.
- Important utility classes or functions that are widely used or encapsulate complex logic.

NOTE: You are seeing only a portion of the codebase in this chunk. Identify ANY abstraction you can recognize based on the provided context, even if it seems incomplete from a global perspective. The goal is to capture ALL possible abstractions at multiple levels of granularity. Being exhaustive is critical - missing abstractions is worse than including minor ones, as long as they are technically significant.

For each identified abstraction, provide:
1.  A concise `name`{name_lang_hint}. This name should be descriptive of its function within the identified technological context.
2.  A "highly-technical" and "Computer Science" centric `description`{desc_lang_hint}. This description MUST BE LOSSLESS and aim for a recreate-level understanding. It should be at least 300 words and comprehensively explain:
    *   What the abstraction is and its primary purpose/responsibilities *within this specific codebase and its identified technology stack*.
    *   The problem it solves or the functionality it provides, explained *in terms of the identified languages, frameworks, or libraries being used*.
    *   Core internal mechanisms: How it works, detailing *how specific features of the identified technology stack (e.g., language constructs, framework APIs, library functions) are leveraged* to achieve its behavior.
    *   Key inputs it processes, outputs it generates, and significant side effects it might have, explained with data types or structures common in the *identified language/framework*.
    *   High-level interactions with other potential abstractions or system components, describing the *nature of these interactions (e.g., method calls, event emissions using an identified event system, data sharing via an identified state management approach)*.
    *   Underlying CS principles (e.g., if it's a caching mechanism, mention hash tables and O(1) lookups, and how the *identified language's dictionary/map or a specific caching library* implements this).
    *   If it employs a known design pattern, name the pattern and detail *how it is implemented using the specific constructs of the identified language or framework*.
    *   A brief real-world analogy, BUT this analogy MUST be immediately and thoroughly mapped back to the technical specifics of the abstraction *as it is realized using the identified technologies*. Each part of the analogy must correspond to a concrete technical aspect.
3.  A list of relevant `file_indices` (integers) using the format `idx # path/comment`, referring to the files listed below that contribute to this abstraction.

IMPORTANT GUIDANCE:
- Identify abstractions at ALL levels of granularity – from high-level architectural patterns (e.g., "Message Queue Consumer Service if a message queue library is identified") down to significant utility functions, classes, or modules, as long as they are central to the codebase portion provided.
- For any identified framework or technology stack, identify both technology-specific abstractions (e.g., "Angular Component", "Spring Boot Service", "Rust Tokio Task Executor") and application-specific implementations built upon them.
- Consider common abstraction categories: Data models/entities (and how they are defined/managed by an identified ORM or language feature), Services/APIs, UI components (if UI framework identified), State management (if state library identified), Configuration handlers, Core business logic modules, Domain entities, Controllers/Routers (as per identified framework), Authentication/Security mechanisms, Event handling/processing systems (if identified).

CRITICAL INSTRUCTION: Your primary task is to identify MAXIMUM number of core abstractions of the application. You MUST NOT identify any form of software testing (including but not limited to unit tests, integration tests, end-to-end (E2E) tests, performance tests, etc.), testing frameworks, test runners, test utilities, or any code, files, or concepts primarily related to testing as an abstraction. If you encounter testing-related elements, ignore them for the purpose of abstraction identification. Focus exclusively on the application's runtime behavior, business logic, and core architectural components.

List of file indices and paths present in the context:
{file_listing_for_prompt}

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 list of dictionaries with NO explanatory text before or after.
2. Do NOT include any explanation, discussion, or notes about the JSON structure.
3. Do NOT describe what you're going to do - just provide the JSON5 directly.
4. Your entire response must be parseable as valid JSON5.
5. Start your response with the opening bracket "[" and end with the closing bracket "]".
6. Each dictionary must contain exactly these three keys: "name", "description", and "file_indices".
7. Use double curly braces {{{{ }}}} for the dictionary objects.
8. Remember to escape all internal curly braces properly, especially in the description text.

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

[
  {{
    "name": "[Example] Asynchronous Task Processor (using Identified Library X){name_lang_hint}",
    "description": "This abstraction is responsible for managing and executing background tasks asynchronously. It leverages [Identified Library X, e.g., Celery for Python, Tokio for Rust] to achieve non-blocking operations. Its core mechanism involves a task queue (potentially identified as RabbitMQ or Redis if context allows) where tasks are enqueued. Worker processes, managed by [Identified Library X], pick up these tasks and execute them. For instance, if the codebase uses Python with Celery, this abstraction would encapsulate Celery app configuration, task definitions (decorated with `@celery.task`), and potentially custom routing logic. It solves the problem of long-running operations blocking the main application thread, crucial for [identified application type, e.g., web servers needing responsive UIs]. Internally, it might use [identified language features like Python's `async/await` if Celery tasks are async] or manage a pool of worker processes/threads as configured by Celery. Inputs are typically serialized task parameters, and outputs could be results stored in a backend (e.g., database via an identified ORM) or notifications sent via an identified event system. This is analogous to a restaurant kitchen's order system where waiters (main threads) take orders and pass them to specialized cooks (worker processes) who prepare dishes (tasks) without making the waiter stand by, thus allowing the waiter to serve more customers (handle more requests). The 'order ticket' is like the serialized task, 'specialized cooks' are like Celery workers, and the 'pass-through window' for orders is like the message queue.{desc_lang_hint}",
    "file_indices": [
      "0 # path/to/task_definitions.py",
      "3 # path/to/celery_config.py"
    ]
  }},
  {{
    "name": "[Example] Configuration Management Service (leveraging Identified Framework Y feature){name_lang_hint}",
    "description": "This service provides a centralized way to access application configuration. It likely uses [Identified Framework Y's configuration module, e.g., Spring Boot's `@ConfigurationProperties`, NestJS's `ConfigService`]. It reads configuration from various sources (e.g., environment variables, .properties/.yaml files - identify which if possible from context) and makes them available application-wide, often through dependency injection provided by [Identified Framework Y]. This solves the problem of scattered configuration settings and provides a consistent interface for all modules to retrieve parameters like database URLs, API keys, feature flags, etc. It might implement features like type validation for configuration values or dynamic reloading if supported by the [Identified Framework Y feature]. This is like a central control panel for a complex machine, where all settings are managed in one place and can be easily adjusted or queried by different parts of the machine.{desc_lang_hint}",
    "file_indices": [
      "5 # path/to/config_service.java"
    ]
  }}
  // ... include ALL distinct functional abstractions based on the DYNAMICALLY IDENTIFIED technology stack and codebase context
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
        context: The abstraction details and code snippets (potentially including identified tech stack info for each abstraction)
        num_abstractions: Number of abstractions
        language_instruction: Optional instruction for non-English output
        lang_hint: Optional language hint for summary and labels
        list_lang_note: Optional language note for the input list
        
    Returns:
        Formatted prompt string
    """
    return f"""
Based on the following abstractions (which may include details about their DYNAMICALLY IDENTIFIED technology stack and implementation) and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions, their detailed descriptions including identified technologies, and potentially related Code Snippets):
{context}

{language_instruction}Your task is to analyze these abstractions and their context to describe their interrelationships.

Please provide:
1.  A high-level `summary` of the project's main purpose and functionality. This summary should be technically precise, highlight key architectural choices evident from the abstractions (e.g., "This project appears to be an [identified architecture, e.g., event-driven microservice system] built using [identified primary language/framework, e.g., Java with Spring Boot]..."), and use markdown formatting with **bold** and *italic* text to emphasize important DYNAMICALLY IDENTIFIED concepts or technologies{lang_hint}.
2.  A comprehensive list (`relationships`) describing ALL significant interactions between these abstractions. For each relationship, specify:
    *   `from_abstraction`: Index and name of the source abstraction (e.g., `0 # AbstractionName1`).
    *   `to_abstraction`: Index and name of the target abstraction (e.g., `1 # AbstractionName2`).
    *   `label`: A brief, descriptive label for the interaction{lang_hint}. This label MUST be highly specific and describe the *mechanism* of interaction, ideally referencing the DYNAMICALLY IDENTIFIED technologies involved. Examples:
        *   "Invokes via REST API call (using identified HTTP client, e.g., Axios, OkHttp)"
        *   "Sends message to (via identified Message Queue, e.g., RabbitMQ, Kafka topic)"
        *   "Depends on for data persistence (through identified ORM, e.g., SQLAlchemy, Hibernate)"
        *   "Consumes events from (using identified event bus/library, e.g., RxJS, Akka Streams)"
        *   "Extends functionality of (via identified inheritance/composition in language X)"
        *   "Manages lifecycle of (using identified framework Y's component model)"
        *   "Provides configuration to (through identified DI mechanism of framework Z)"
        *   "Composes UI with (as an identified UI component in framework A)"

    Consider a WIDE VARIETY of technology-agnostic relationship types, but ALWAYS specify them *in terms of the DYNAMICALLY IDENTIFIED technology stack* if possible:
    - Structural: "Is part of (e.g., as a module in an identified build system)", "Contains (e.g., an identified data structure)", "Composes (e.g., using identified component model)"
    - Dependency: "Requires (e.g., an identified library/module)", "Is configured by (e.g., an identified configuration file format or service)", "Uses services from (e.g., an identified internal API)"
    - Data Flow: "Produces data for (e.g., an identified data pipeline stage)", "Consumes data from (e.g., an identified database table via an ORM)"
    - Conceptual/Logical: "Specializes (e.g., an identified base class/interface)", "Implements (e.g., an identified API specification)", "Orchestrates (e.g., a series of calls to identified services)"
    - Invocation/Control Flow: "Invokes (e.g., a method from an identified class/module)", "Triggers (e.g., an event in an identified event system)"

    The relationship should ideally be backed by evidence in the provided code context or be a clear architectural or logical link between the abstractions, explained via their *identified technological roles and interactions*.
    Be thorough in identifying ALL meaningful relationships, ensuring complete coverage of how abstractions interact *using their DYNAMICALLY IDENTIFIED implementation details*.

IMPORTANT INSTRUCTIONS:
1. CRITICAL: EVERY abstraction listed MUST be involved in at least ONE meaningful relationship (either as a source or a target). Do NOT leave any abstraction isolated. If a direct interaction is not obvious from the immediate code, infer logical or conceptual connections based on their descriptions, their likely roles in the *identified architecture*, and common patterns in the *identified technology stack*.
2. Each abstraction index (from 0 to {num_abstractions-1}) MUST appear at least once across all `from_abstraction` or `to_abstraction` fields.
3. Use ONLY the abstraction indices and names (e.g., `0 # AbstractionName1`) from the list above for `from_abstraction` and `to_abstraction` fields. DO NOT use file indices or generic project names.
4. The indices in `from_abstraction` and `to_abstraction` must reference the abstraction list (0 to {num_abstractions-1}).
5. Exclude any relationships that are solely testing-related. Focus on the application's runtime architecture and logic.
6. Be COMPREHENSIVE. It's better to include a plausible conceptual relationship (explained via the identified tech) than to leave an abstraction disconnected.

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 object with NO explanatory text before or after.
2. Do NOT include any explanation, discussion, or notes about the JSON structure.
3. Do NOT describe what you're going to do - just provide the JSON5 directly.
4. Your entire response must be parseable as valid JSON5.
5. Start your response with the opening curly brace "{{" and end with the closing curly brace "}}".
6. The JSON5 object must contain exactly these two keys: "summary" and "relationships".
7. The "relationships" value must be an array of objects, each with "from_abstraction", "to_abstraction", and "label" keys.

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

{{
  "summary": "This project appears to be a [DYNAMICALLY IDENTIFIED architecture, e.g., **serverless data processing pipeline**] implemented in [DYNAMICALLY IDENTIFIED language, e.g., *Python*] using [DYNAMICALLY IDENTIFIED key frameworks/libraries, e.g., **AWS Lambda, Pandas, and S3**]. Its main purpose is to [project function, e.g., ingest raw data, transform it according to defined business rules, and store the results for analytics]. Key abstractions like [Abstraction A name] and [Abstraction B name] suggest a focus on [identified core functionality, e.g., efficient data manipulation and scalable event handling].{lang_hint}",
  "relationships": [
    {{
      "from_abstraction": "0 # DataIngestionLambda",
      "to_abstraction": "1 # DataTransformationService (Pandas)",
      "label": "Passes raw data to (via identified S3 event trigger and identified data format, e.g., Parquet){lang_hint}"
    }},
    {{
      "from_abstraction": "1 # DataTransformationService (Pandas)",
      "to_abstraction": "2 # ReportingModule (using identified DB client)",
      "label": "Writes transformed data to (using identified DB client, e.g., psycopg2, to identified PostgreSQL DB){lang_hint}"
    }}
    // ... include ALL relationships between ALL abstractions, with labels explaining the mechanism via IDENTIFIED TECHNOLOGIES
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
        context: Context about relationships and project summary (potentially including identified tech stack info)
        list_lang_note: Optional language note for the input list
        
    Returns:
        Formatted prompt string
    """
    return f"""
Given the following project abstractions and their relationships for the project `{project_name}` (which may include details on their DYNAMICALLY IDENTIFIED technology stack, implementation, and interdependencies):

Abstractions (Index # Name){list_lang_note}:
{abstraction_listing}

Context about Project Summary and Abstraction Relationships (including interaction mechanisms via IDENTIFIED TECHNOLOGIES):
{context}

Your task is to determine the optimal chapter order for a comprehensive technical tutorial of `{project_name}`. The primary goal of this tutorial is to enable a developer to understand the codebase so deeply that they could, in principle, recreate its core components and their interactions.

To achieve this, the chapter order MUST follow a logical progression that facilitates deep understanding and mental model construction. Consider these principles for ordering:
1.  **Dependency-First (Conceptual and Technical)**:
    *   Explain foundational or prerequisite abstractions before those that depend on or build upon them. This applies to both conceptual dependencies (e.g., a core data model before a service that uses it) and technical dependencies (e.g., a base class or utility module before its consumers; a messaging infrastructure before services that publish/subscribe to it, especially if these are DYNAMICALLY IDENTIFIED from the context).
    *   Analyze the provided `relationships` (which detail interaction mechanisms via IDENTIFIED TECHNOLOGIES) to infer these dependencies.
2.  **Build from Core to Periphery**: 
    *   Start with the most central, architecturally significant, or fundamental abstractions that define the core purpose or structure of the project (based on the DYNAMICALLY IDENTIFIED architecture).
    *   Gradually move towards more specialized, supporting, or peripheral abstractions.
3.  **Minimize Forward References**: Structure the order to minimize the need for a reader to understand concepts that haven't been explained yet. While some forward referencing might be unavoidable in complex systems, strive for a flow that builds knowledge incrementally.
4.  **Complexity Progression**: If possible, introduce simpler or more self-contained abstractions before highly complex or heavily interconnected ones, assuming dependencies allow.
5.  **User/Entry-Point Perspective (If Applicable)**: If the system has clear user-facing entry points or primary use-case flows (and these can be DYNAMICALLY IDENTIFIED from the abstractions, e.g., an API Gateway, a main UI component), it might be logical to start with these high-level interaction points before diving into their underlying components. However, balance this with the dependency-first principle.

Inspired by the "Tabulation" approach from Dynamic Programming, aim for an order where each chapter builds upon the established knowledge from previous chapters.

IMPORTANT: Do not prioritize testing frameworks, test utilities, or any testing-related abstractions in your ordering. Focus on explaining the core functionality and architecture of the application itself.

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 array with NO explanatory text before or after.
2. Do NOT include any explanation, discussion, or notes about the JSON structure.
3. Do NOT describe what you're going to do - just provide the JSON5 directly.
4. Your entire response must be parseable as valid JSON5.
5. Start your response with the opening bracket "[" and end with the closing bracket "]".
6. Each array element must be a string in the format "idx # AbstractionName".
7. Include ALL abstractions in your ordered list.

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

[
  "2 # [Example] CoreDataModel (Defines foundational structures used by identified ORM X)",
  "0 # [Example] ConfigurationService (Provides settings for identified framework Y)",
  "1 # [Example] MainBusinessLogicService (Uses CoreDataModel, configured by ConfigurationService, built on identified framework Y)",
  "3 # [Example] APIGateway (Exposes MainBusinessLogicService via identified protocol Z, e.g., REST with Spring MVC)"
  // ... include ALL abstractions in the optimal learning and recreation-focused order, considering DYNAMICALLY IDENTIFIED dependencies and architecture
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
    return f"""{language_instruction}Write a comprehensive, in-depth tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

**OVERALL GOAL**: Your primary objective is to explain this abstraction in such detail and with such focus on the **specifics of the provided codebase context (its languages, frameworks, libraries, and evident CS principles that YOU MUST DYNAMICALLY IDENTIFY from the provided context)** that a developer reading this chapter could gain a deep enough understanding to conceptually recreate a similar implementation. All explanations must be **LOSSLESS**, capturing all critical implementation details and design rationale inferable from the context.

Concept Details{concept_details_note}:
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note}:
{full_chapter_listing}

Context from previous chapters{prev_summary_note}:
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}

Relevant Code Snippets (Code itself remains unchanged. Focus on explaining HOW and WHY this code works in the context of the project's **dynamically identified specific technology stack**):

{file_context_str if file_context_str else "No specific code snippets provided for this abstraction."}

Instructions for the chapter (Generate content in {language.capitalize()} unless specified otherwise):

- Be STRICTLY LOSSLESS and COMPREHENSIVE - capture ALL aspects of this abstraction from the provided context/data.
- The chapter should be thorough and detailed, covering the abstraction from basic concepts to advanced usage patterns, always linking back to the **specific implementation strategies and technologies dynamically identified as used in this codebase**.
- **IMPORTANT**: Maintain a HIGHLY TECHNICAL writing style throughout. Readers are senior software developers who need in-depth technical explanations tailored to the project's **dynamically identified stack**.

- Start with a clear heading (e.g., `# Chapter {{{{chapter_num}}}}: {{{{abstraction_name}}}}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter{instruction_lang_note}, referencing it with a proper Markdown link using its name{link_lang_note}.

- Begin with a problem statement section that:
  * Clearly articulates the technical challenge this abstraction solves **within the context of this specific project and its dynamically identified technology stack**{instruction_lang_note}.
  * Explains the architectural consequences of NOT having this abstraction, considering the project's **dynamically identified frameworks and patterns**.
  * Provides a concrete, technical example of the problem (with code if applicable, reflecting the codebase's **dynamically identified language/framework**).
  * Uses a real-world analogy but immediately connects it back to the technical domain, specifically how this problem manifests and is solved using the **dynamically identified technologies and patterns of this codebase**. Each part of the analogy must be mapped to a specific technical aspect of the abstraction being discussed.

- **CRITICAL REQUIREMENT FOR ALL HEADINGS AND LIST ITEMS**: 
  * EVERY heading (H1, H2, H3, etc.) and EVERY list item (bullet points, numbered lists) MUST be followed by at least one, preferably multiple, detailed technical paragraph(s) (minimum 5-7 sentences each). 
  * These paragraphs must provide in-depth explanations of the concept introduced by the heading or list item.
  * Focus on:
    * The "why" and "how" from a technical perspective, **as implemented in this codebase using its DYNAMICALLY IDENTIFIED technologies**.
    * Underlying computer science principles, data structures, and algorithms, **and how they are applied or manifested using the project's DYNAMICALLY IDENTIFIED specific language features and framework capabilities**.
    * Design patterns applied and the rationale behind them, **detailing how they are realized with the codebase's DYNAMICALLY IDENTIFIED tech stack**.
    * Technical trade-offs (e.g., "This approach, using [a specific framework feature you DYNAMICALLY IDENTIFY, like 'a particular change detection strategy' or 'a component memoization feature'], optimizes for rendering performance...").
    * Boundary conditions, edge cases, and robust error handling strategies **relevant to the DYNAMICALLY IDENTIFIED implementation**.
    * Performance characteristics, scalability considerations, and potential bottlenecks, **considering the project's DYNAMICALLY IDENTIFIED specific framework and architecture**.
    * How this specific part of the abstraction interacts with other parts of the abstraction or other related abstractions, detailing the mechanisms (e.g., API calls via [the specific HTTP client library you IDENTIFY], event emissions using [the specific event library/pattern you IDENTIFY, like RxJS subjects or Node.js EventEmitter], shared state via [the specific state management solution you IDENTIFY]) used **within the given codebase context**.
    * **How DYNAMICALLY IDENTIFIED specific language features (e.g., Python decorators, Java annotations, JavaScript async/await), framework capabilities (e.g., specific dependency injection mechanisms, ORM features, template engine syntax), or library functions are used to implement this part of the abstraction.**
  * DO NOT introduce a heading or list item and leave it with only a brief or superficial explanation. Depth and **codebase-specificity based on DYNAMIC IDENTIFICATION** are paramount.

- For each major aspect of the abstraction, create dedicated technical sections that:
  * Begin with an H2/H3 heading clearly identifying the concept. Ensure this heading is followed by detailed explanatory paragraphs as per the critical requirement above.
  * Provide detailed technical explanations of internal mechanisms, not just surface-level behavior, **focusing on how the project's DYNAMICALLY IDENTIFIED tools achieve this**.
  * Explain design patterns being applied (Singleton, Factory, Observer, etc.) with rationale and how they are implemented **using the specific language constructs and framework features DYNAMICALLY IDENTIFIED in this project**.
  * Discuss technical trade-offs made in the implementation ("This approach optimizes for X at the cost of Y") in detail, **grounded in the project's DYNAMICALLY IDENTIFIED context**.
  * Describe boundary conditions, edge cases, and error handling strategies comprehensively, **as they would apply to this codebase based on its DYNAMICALLY IDENTIFIED stack**.
  * Explore performance characteristics and scalability considerations in depth, **relevant to the DYNAMICALLY IDENTIFIED chosen tech stack**.

- Include ALL relevant code examples for this abstraction from the codebase. For each code example:
  * Show complete implementation details with proper context.
  * Annotate with line-by-line technical explanation of non-trivial aspects. Each annotation should be substantial and explain **how that line contributes to the abstraction using the project's DYNAMICALLY IDENTIFIED language/framework features**.
  * Highlight key design patterns, idioms, or language/framework features being leveraged, explaining their significance **in achieving the abstraction's goals within this specific codebase, using DYNAMICALLY IDENTIFIED technologies**.
  * Note any optimizations or performance considerations, explaining how they work **in this DYNAMICALLY IDENTIFIED environment**.
  * If multiple implementations exist (e.g., different ways a service could be written), compare and contrast their technical merits **within the project's DYNAMICALLY IDENTIFIED architectural style**.

- Each code block should be COMPLETE! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Make the code Simple however don't loose clarity. Use comments{code_comment_note} to skip non-important implementation details. Each code block should have a senior software developer friendly explanation right after it{instruction_lang_note}, following the detailed paragraph requirement and focusing on **how this code works with the project's DYNAMICALLY IDENTIFIED specific tools**.

- When using bullet points or any list format in your chapter, ALWAYS follow each list item with at least one detailed paragraph (minimum 5-7 sentences) that thoroughly explains the technical aspects of that point, its relevance to the abstraction, and its implications **within the DYNAMICALLY IDENTIFIED codebase**. Never leave list items unexplained or superficially explained. For example (illustrative, YOU MUST adapt this to the DYNAMICALLY IDENTIFIED technologies):

  * Define entity relationships (if discussing a data-centric abstraction in the context of an ORM DYNAMICALLY IDENTIFIED from the codebase):
    
    In this system, entity relationships, likely managed by [the specific ORM you DYNAMICALLY IDENTIFIED, e.g., SQLAlchemy, Hibernate, TypeORM, Prisma] (inferred from the codebase context and common patterns associated with the DYNAMICALLY IDENTIFIED backend framework like Django, Spring Boot, NestJS, etc.), establish the formal connections between domain objects like `User` and `Article`. These are not just conceptual links but translate to concrete database schema definitions (e.g., foreign keys, join tables) and runtime behaviors facilitated by [the identified ORM's specific features, e.g., decorators, annotations, or model definitions]. For instance, a `OneToMany` relationship (or its equivalent in [the identified ORM]) from `User` to `Article` would imply a user can have multiple articles. This is crucial for data integrity (ensuring an article always has a valid author ID, managed by [the identified ORM's referential integrity mechanisms]) and for query efficiency (allowing eager or lazy loading of related articles via [the identified ORM's specific query-building or relation-loading mechanisms]). The choice of cascade options (e.g., `cascade: ['insert', 'update']` or their equivalent in [the identified ORM]) on such a relationship dictates how persistence operations on a `User` entity affect its related `Article` entities, directly impacting data consistency. [The identified ORM] then uses this metadata to generate appropriate database queries (e.g., SQL for relational DBs), abstracting the developer from raw database interactions while enforcing these structural and behavioral rules. Performance considerations here include choosing between eager loading (potentially causing over-fetching) and lazy loading (potentially leading to N+1 query problems if not handled carefully with mechanisms like [specific features of the identified ORM, e.g., 'joinedload' in SQLAlchemy, 'fetch joins' in JPA, or 'relations' options in TypeORM's find queries]).

- EXPLICITLY ENSURE all list items (bullet points, numbered lists) are expanded with detailed paragraphs. The detailed explanations should include:
  * Underlying theoretical computer science principles (e.g., graph theory for relationships, state machines for lifecycle management), **and how the project's DYNAMICALLY IDENTIFIED specific libraries or framework features implement or relate to these principles.**
  * Implementation considerations and technical trade-offs **faced when using the project's DYNAMICALLY IDENTIFIED chosen technologies** (e.g., performance impact of [a specific data fetching strategy in the identified framework] vs. another).
  * Performance implications and optimization strategies **available within the project's DYNAMICALLY IDENTIFIED framework** (e.g., specific list rendering optimizations like `trackBy` in Angular or `key` prop in React).
  * Common design variations and their consequences **when building with this DYNAMICALLY IDENTIFIED specific tech stack**.
  * Explain core concepts, **then immediately show how these concepts are instantiated or utilized by the DYNAMICALLY IDENTIFIED specific languages, frameworks, or libraries used in this project.**

- Describe the internal implementation to help understand what's under the hood{instruction_lang_note}. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called, **explaining how the codebase's DYNAMICALLY IDENTIFIED specific architectural components (e.g., specific service types, controller patterns, state store structures) participate in this flow**{instruction_lang_note}. It's recommended to use a detailed sequence diagram with mermaid syntax (`sequenceDiagram`) with a dummy example - include at least 5-8 participants to ensure proper representation of the flow. If participant name has space, use: `participant QP as Query Processing`. ALWAYS use proper mermaid syntax with `sequenceDiagram` at the beginning and the correct arrow syntax (e.g., use `->>` for messages, NOT `->`). Example: ```mermaid\\nsequenceDiagram\\n    participant A as ComponentA\\n    participant B as ComponentB\\n    A->>B: Request\\n    B->>A: Response\\n```{mermaid_lang_note}. Ensure the diagram and its explanation are detailed and technically rich, reflecting the project's **DYNAMICALLY IDENTIFIED** components.

- Then dive deeper into code for the internal implementation with references to files. Provide explicit technical details on:
  * Initialization sequences and dependency injection/management strategies **as employed by the project's DYNAMICALLY IDENTIFIED framework (e.g., specific DI syntax or patterns for the identified framework)**.
  * Runtime behavior, control flow, and algorithmic complexity of key operations, **explaining how DYNAMICALLY IDENTIFIED language/framework features support this**.
  * Memory management considerations (e.g., object lifecycles, caching strategies using specific libraries if evident from context, potential memory leaks if [e.g., event listeners or subscriptions in the identified asynchronous programming model like RxJS or Promises] aren't managed).
  * Threading/concurrency concerns (e.g., the event loop in Node.js/browser JavaScript, goroutines in Go, async/await patterns in Python/C#/JS, or specific threading models if a multi-threaded language is identified).
  * How errors and exceptions are propagated and handled through the system, **potentially using DYNAMICALLY IDENTIFIED framework-specific error handlers or common patterns like try-catch with async/await in the identified language**.
  * Performance optimizations implemented (e.g., [framework-specific rendering optimizations like memoization or virtual DOM strategies], [specific state management library's memoized selectors], specific library features for efficient data handling DYNAMICALLY IDENTIFIED from context), **explaining how these DYNAMICALLY IDENTIFIED specific techniques work**.

- IMPORTANT: Explicitly discuss how this abstraction interacts with EVERY other related abstraction. These interactions must be explained technically, detailing data flow, control flow, and dependencies **using the mechanisms provided by the project's DYNAMICALLY IDENTIFIED framework (e.g., specific state management patterns, component communication methods like props/events or context APIs, service-to-service invocation patterns)**. When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title{link_lang_note}. Translate the surrounding text.

- Cover ALL aspects of the abstraction, including edge cases and advanced usage patterns. Include technical sections on:
  * Core functionality and internal mechanisms (not just API surface), explained with CS principles **as applied by the project's DYNAMICALLY IDENTIFIED tech stack**.
  * Initialization and configuration with deep technical details (e.g., configuration schemas used by a specific library you IDENTIFY, validation, dynamic reconfiguration if the DYNAMICALLY IDENTIFIED framework supports it).
  * Error handling strategies, failure modes, and recovery mechanisms (e.g., retry logic using [features of an identified async library like RxJS `retryWhen` or a promise-based retry utility], circuit breakers if a library for this is IDENTIFIED, idempotency considerations for API calls).
  * Performance characteristics, benchmarking results (if applicable/inferable), and optimization techniques **specific to the project's DYNAMICALLY IDENTIFIED environment**.
  * Integration patterns with other system components (e.g., message queues, external APIs via [specific HTTP client libraries IDENTIFIED like Axios or Fetch API], databases via an [IDENTIFIED ORM like Sequelize or Django ORM]), explaining the protocols and data formats involved.
  * Architectural patterns it implements (e.g., MVC in a traditional backend, MVVM/MVC in a frontend framework, CQRS with a state management library), with a detailed explanation of how the pattern is realized **using the tools and structures DYNAMICALLY IDENTIFIED in this specific project**.
  * Known limitations or constraints and their underlying technical reasons, **often tied to the DYNAMICALLY IDENTIFIED chosen framework or language version**.

- Include a technical best practices section that:
  * Identifies common pitfalls and anti-patterns when using or extending this abstraction **within the project's DYNAMICALLY IDENTIFIED specific framework/language context**.
  * Provides optimized usage patterns for different scenarios, backed by technical reasoning **relevant to the project's DYNAMICALLY IDENTIFIED tools**.
  * Discusses scaling considerations and how the abstraction behaves under high load, **given its implementation with the project's DYNAMICALLY IDENTIFIED tech stack**.
  * Addresses any version-specific considerations or compatibility issues of the DYNAMICALLY IDENTIFIED frameworks/libraries used, explaining the technical differences.

- **CODEBASE-SPECIFIC TECHNOLOGIES (DYNAMICALLY IDENTIFIED) AND UNDERLYING PRINCIPLES**: Present ALL explanations by first **DYNAMICALLY IDENTIFYING and then focusing on the specific programming languages, frameworks, libraries, and architectural patterns evident in the provided codebase context**. Your primary goal is to explain how *these DYNAMICALLY IDENTIFIED specific tools* are used to build the abstraction. Then, connect these specific implementations back to fundamental computer science principles and broader architectural patterns to provide a deeper understanding.
    *   For example, if your analysis of the codebase context reveals the use of a particular frontend framework (e.g., React, Angular, Vue, Svelte) and a specific state management library (e.g., Redux, Vuex, Zustand, NgRx, Pinia), your explanation for an abstraction should first detail how it *specifically* utilizes the core constructs of *that identified framework* (e.g., its component model, lifecycle hooks, service/provider patterns) and *that identified state library* (e.g., its specific mechanisms for actions, state updates, selectors, and side-effect handling). After thoroughly explaining this usage of the *identified tools*, you must then connect these specific implementations to the underlying CS concepts these features embody, such as reactive programming, the observer pattern, virtual DOM diffing, unidirectional data flow, or specific state management patterns (like Flux, Elm architecture, etc.).
    *   Focus on how the *DYNAMICALLY IDENTIFIED chosen tools* solve the problem (e.g., "The [identified framework's DI system, such as Spring's @Autowired or Angular's constructor injection,] is used here to provide the [specific service name], which decouples the [specific component/module name] from the direct instantiation of its dependencies, an application of the Inversion of Control principle.").
    *   Discuss the underlying algorithms and data structures, and then show or infer how they might be implemented or leveraged by the project's **DYNAMICALLY IDENTIFIED language/framework** (e.g., "The efficiency of the [specific feature, like tag lookup] suggests a hash map is used internally, which in [the identified language, like TypeScript or Python] could be a `Map` object or a dictionary respectively, because this allows for O(1) average time complexity for insertions and lookups.").
    *   Explain architectural decisions in terms of *why this project likely chose these DYNAMICALLY IDENTIFIED specific technologies/patterns* to solve its problems (e.g., "[The identified state management library, like NgRx or Redux] was likely chosen to handle complex application state, offering predictability and traceability through [its specific mechanisms, like unidirectional data flow and immutable updates], which is beneficial for larger applications like this one.").
    *   Highlight how the unique features of the project's **DYNAMICALLY IDENTIFIED tech stack** (e.g., static typing in TypeScript, observable streams in RxJS if identified, specific component lifecycle hooks of the identified framework) are leveraged by this abstraction to provide its functionality robustly and efficiently.

- Heavily use real-world and practical analogies and examples throughout{instruction_lang_note} to help a Senior Software Developer understand, but ALWAYS follow analogies with detailed technical specifics **directly relevant to the abstraction and how it's built using the codebase's DYNAMICALLY IDENTIFIED specific technologies**. The analogy should illuminate a complex technical point *about the codebase's DYNAMICALLY IDENTIFIED specific implementation*, not replace it.

- End the chapter with a technical conclusion that:
  * Summarizes the key technical insights about the abstraction, its design, and its role **within the project's DYNAMICALLY IDENTIFIED specific architecture**.
  * Highlights the core architectural patterns and computer science principles demonstrated by this abstraction, **as implemented with the project's DYNAMICALLY IDENTIFIED tools**.
  * Reinforces how this abstraction connects to the broader system architecture of the project.
  * Provides a transition to the next chapter{instruction_lang_note}. If there is a next chapter, use a proper Markdown link: [Next Chapter Title](next_chapter_filename){link_lang_note}.

- Ensure the tone is welcoming yet technically precise, substantive, and authoritative{tone_note}.

- IMPORTANT: DO NOT include any content related to unit tests, end-to-end (e2e) tests, integration tests, or any other types of testing in the tutorial. Skip all testing-related code and explanations. Focus exclusively on explaining the abstractions, concepts, and how to use them without any test coverage discussions.

- Output *only* the Markdown content for this chapter.

Now, directly provide a "technical" and "Computer Science"-friendly Markdown output (DON'T need ```markdown``` tags):
"""
