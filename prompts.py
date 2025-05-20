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

{language_instruction}Based on the provided Codebase Context, your primary task is to **DYNAMICALLY IDENTIFY** the specific programming languages, frameworks, libraries, architectural patterns (e.g., microservices, event-driven, layered), and core Computer Science principles (e.g., specific algorithms, data structures, concurrency models) evident in this portion of the code. Then, using this identified technological context, identify the **MAXIMUM POSSIBLE NUMBER** of distinct and significant **TECHNICAL** abstractions.

Abstractions can include (but are not limited to):
- Key architectural components (e.g., services, controllers, repositories, domain entities if an ORM or DDD is identified).
- Instantiations of common design patterns (e.g., Factory, Singleton, Observer, Strategy - explain how the pattern is specifically implemented with the identified language/framework features).
- Core algorithms or complex business logic units.
- Significant data structures and their management.
- Primary modules, classes, or interfaces that play a crucial role.
- Critical operational flows or processing pipelines.
- Important utility classes or functions that are widely used or encapsulate complex logic.

NOTE: You are seeing only a portion of the codebase in this chunk. Identify ANY **technical** abstraction you can recognize based on the provided context, even if it seems incomplete from a global perspective. The goal is to capture ALL possible **technical** abstractions at multiple levels of granularity. Being exhaustive is critical - missing **technical** abstractions is worse than including minor ones, as long as they are technically significant and contribute to a **LOSSLESS, recreate-level understanding** of the system.

For each identified abstraction, provide:
1.  A concise `name`{name_lang_hint}. This name should be descriptive of its function within the identified technological context.
2.  A "highly-technical" and "Computer Science" centric `description`{desc_lang_hint}. This description MUST BE **LOSSLESS** and aim for a **recreate-level understanding**. It should be at least 300 words and comprehensively explain:
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

CRITICAL INSTRUCTION: Your primary task is to identify the **MAXIMUM number** of core **technical** abstractions of the application necessary for a **LOSSLESS, recreate-level understanding**. You MUST NOT identify any form of software testing (including but not limited to unit tests, integration tests, end-to-end (E2E) tests, performance tests, etc.), testing frameworks, test runners, test utilities, or any code, files, or concepts primarily related to testing as an abstraction. If you encounter testing-related elements, ignore them for the purpose of abstraction identification. Focus exclusively on the application's runtime behavior, business logic, and core architectural components.

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

{language_instruction}Your task is to analyze these abstractions and their context to describe their interrelationships in a **LOSSLESS** manner, facilitating a **recreate-level understanding** of the system's architecture.

Please provide:
1.  A high-level `summary` of the project's main purpose and functionality. This summary must be technically precise, **LOSSLESSLY** conveying key architectural choices evident from the abstractions (e.g., "This project appears to be an [identified architecture, e.g., event-driven microservice system] built using [identified primary language/framework, e.g., Java with Spring Boot]..."), and use markdown formatting with **bold** and *italic* text to emphasize important DYNAMICALLY IDENTIFIED concepts or technologies{lang_hint}.
2.  A comprehensive list (`relationships`) describing ALL significant interactions between these abstractions. Each relationship description must be detailed enough to ensure **LOSSLESS** information transfer about how abstractions connect and influence each other. For each relationship, specify:
    *   `from_abstraction`: Index and name of the source abstraction (e.g., `0 # AbstractionName1`).
    *   `to_abstraction`: Index and name of the target abstraction (e.g., `1 # AbstractionName2`).
    *   `label`: A brief, descriptive label for the interaction{lang_hint}. This label MUST be highly specific and describe the *mechanism* of interaction, ideally referencing the DYNAMICALLY IDENTIFIED technologies involved, to ensure **LOSSLESS** capture of the interaction's nature. Examples:
        *   "Invokes via REST API call (using identified HTTP client, e.g., Axios, OkHttp)"
        *   "Sends message to (via identified Message Queue, e.g., RabbitMQ, Kafka topic)"
        *   "Depends on for data persistence (through identified ORM, e.g., SQLAlchemy, Hibernate)"
        *   "Consumes events from (using identified event bus/library, e.g., RxJS, Akka Streams)"
        *   "Extends functionality of (via identified inheritance/composition in language X)"
        *   "Manages lifecycle of (using identified framework Y's component model)"
        *   "Provides configuration to (through identified DI mechanism of framework Z)"
        *   "Composes UI with (as an identified UI component in framework A)"

    Consider a WIDE VARIETY of technology-agnostic relationship types, but ALWAYS specify them *in terms of the DYNAMICALLY IDENTIFIED technology stack* if possible, to maintain **LOSSLESS** detail:
    - Structural: "Is part of (e.g., as a module in an identified build system)", "Contains (e.g., an identified data structure)", "Composes (e.g., using identified component model)"
    - Dependency: "Requires (e.g., an identified library/module)", "Is configured by (e.g., an identified configuration file format or service)", "Uses services from (e.g., an identified internal API)"
    - Data Flow: "Produces data for (e.g., an identified data pipeline stage)", "Consumes data from (e.g., an identified database table via an ORM)"
    - Conceptual/Logical: "Specializes (e.g., an identified base class/interface)", "Implements (e.g., an identified API specification)", "Orchestrates (e.g., a series of calls to identified services)"
    - Invocation/Control Flow: "Invokes (e.g., a method from an identified class/module)", "Triggers (e.g., an event in an identified event system)"

    The relationship should ideally be backed by evidence in the provided code context or be a clear architectural or logical link between the abstractions, explained via their *identified technological roles and interactions* to ensure **LOSSLESS** information.
    Be thorough in identifying ALL meaningful relationships, ensuring complete coverage of how abstractions interact *using their DYNAMICALLY IDENTIFIED implementation details for a **LOSSLESS** architectural view*.

IMPORTANT INSTRUCTIONS:
1. CRITICAL: EVERY abstraction listed MUST be involved in at least ONE meaningful relationship (either as a source or a target) to ensure a **LOSSLESS** representation of the system. Do NOT leave any abstraction isolated. If a direct interaction is not obvious from the immediate code, infer logical or conceptual connections based on their descriptions, their likely roles in the *identified architecture*, and common patterns in the *identified technology stack*.
2. Each abstraction index (from 0 to {num_abstractions-1}) MUST appear at least once across all `from_abstraction` or `to_abstraction` fields.
3. Use ONLY the abstraction indices and names (e.g., `0 # AbstractionName1`) from the list above for `from_abstraction` and `to_abstraction` fields. DO NOT use file indices or generic project names.
4. The indices in `from_abstraction` and `to_abstraction` must reference the abstraction list (0 to {num_abstractions-1}).
5. Exclude any relationships that are solely testing-related. Focus on the application's runtime architecture and logic.
6. Be COMPREHENSIVE. It's better to include a plausible conceptual relationship (explained via the identified tech for **LOSSLESS** understanding) than to leave an abstraction disconnected.

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

Your task is to determine the optimal chapter order for a comprehensive technical tutorial of `{project_name}`. The primary goal of this tutorial is to enable a developer to achieve a **recreate-level understanding** of the codebase, where they could, in principle, reconstruct its core components and their interactions.

To achieve this, the chapter order MUST follow a logical progression that facilitates deep understanding and mental model construction. Employ a strategy inspired by the **"Tabulation" approach from Dynamic Programming**: each chapter should build upon the established knowledge from previous chapters, incrementally constructing a complete and **LOSSLESS** understanding of the system.

Consider these principles for ordering:
1.  **Dependency-First (Conceptual and Technical)**:
    *   Explain foundational or prerequisite abstractions before those that depend on or build upon them. This applies to both conceptual dependencies (e.g., a core data model before a service that uses it) and technical dependencies (e.g., a base class or utility module before its consumers; a messaging infrastructure before services that publish/subscribe to it, especially if these are DYNAMICALLY IDENTIFIED from the context).
    *   Analyze the provided `relationships` (which detail interaction mechanisms via IDENTIFIED TECHNOLOGIES) to infer these dependencies for a **LOSSLESS** flow of information.
2.  **Build from Core to Periphery**: 
    *   Start with the most central, architecturally significant, or fundamental abstractions that define the core purpose or structure of the project (based on the DYNAMICALLY IDENTIFIED architecture).
    *   Gradually move towards more specialized, supporting, or peripheral abstractions.
3.  **Minimize Forward References for Clarity**: Structure the order to minimize the need for a reader to understand concepts that haven't been explained yet. While some forward referencing might be unavoidable in complex systems, strive for a flow that builds knowledge incrementally, vital for **recreate-level understanding**.
4.  **Complexity Progression**: If possible, introduce simpler or more self-contained abstractions before highly complex or heavily interconnected ones, assuming dependencies allow.
5.  **User/Entry-Point Perspective (If Applicable)**: If the system has clear user-facing entry points or primary use-case flows (and these can be DYNAMICALLY IDENTIFIED from the abstractions, e.g., an API Gateway, a main UI component), it might be logical to start with these high-level interaction points before diving into their underlying components. However, balance this with the dependency-first principle to ensure a **LOSSLESS** buildup of knowledge.

Inspired by the "Tabulation" approach, aim for an order where each chapter builds upon the established knowledge from previous chapters, ensuring a cohesive and **recreate-level understanding**.

IMPORTANT: Do not prioritize testing frameworks, test utilities, or any testing-related abstractions in your ordering. Focus on explaining the core functionality and architecture of the application itself to achieve a **LOSSLESS** and functional comprehension.

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
    Generate the prompt for writing an individual chapter. This prompt has been refactored for clarity, conciseness,
    and to strongly enforce in-depth narrative explanations for all structural elements, aiming for a
    recreate-level understanding of the codebase.
    """

    # CORE EXPLANATION MANDATE (CEM) DEFINITION (Conceptual - applied in the f-string below):
    # This mandate is the guiding principle for all content generation within this chapter.
    # It applies to EVERY structural element: headings (H1, H2, H3, etc.), list items (bullet points, numbered lists),
    # code examples, diagrams, and any distinct conceptual point introduced.
    # Each such element MUST be immediately followed by one or more detailed explanatory PARAGRAPHS
    # (minimum 5-7 sentences EACH, or more if complexity warrants). These paragraphs are the CORE of the chapter
    # and must provide in-depth technical explanations. They should not merely restate the heading/item,
    # but rather elaborate significantly on the following, all grounded in the DYNAMICALLY IDENTIFIED
    # specific programming languages, frameworks, libraries, and architectural patterns evident in the
    # provided codebase context:
    #
    # 1.  The "Why": The specific problem this element addresses, its purpose, and its significance
    #     within the DYNAMICALLY IDENTIFIED technology stack of the project.
    # 2.  The "How": The underlying mechanisms, detailing the use of DYNAMICALLY IDENTIFIED language features,
    #     framework capabilities, or library functions.
    # 3.  Design Rationale ("Thinking for Oneself"): The reasons *why* this specific approach, technology,
    #     or pattern was likely chosen for the DYNAMICALLY IDENTIFIED codebase. This includes discussing
    #     potential alternatives considered and why they might have been dismissed in this context.
    # 4.  Technical Trade-offs: Any compromises made (e.g., performance vs. readability, flexibility vs. complexity)
    #     due to the chosen approach within the DYNAMICALLY IDENTIFIED stack.
    # 5.  CS Principles & Architectural Patterns: Relevant underlying computer science concepts (algorithms,
    #     data structures, established architectural patterns) and how they manifest in this specific
    #     DYNAMICALLY IDENTIFIED implementation. Explain *why* these principles are relevant here.
    # 6.  Impact & Interactions: How this element interacts with other parts of the system and its broader
    #     implications for the DYNAMICALLY IDENTIFIED architecture.
    #
    # Adherence to this CEM is paramount for achieving a LOSSLESS, recreate-level understanding.
    # All explanations MUST be grounded in the DYNAMICALLY IDENTIFIED specific technologies of this project.

    # This note will be appended to instructions for sections/elements that need CEM application.
    cem_application_instruction = \
        "(Apply the Core Explanation Mandate (CEM) here: provide detailed paragraphs covering the 'Why', 'How', 'Design Rationale', 'Trade-offs', 'CS Principles', and 'Impact/Interactions' in the context of DYNAMICALLY IDENTIFIED technologies for this point and all its sub-points. Each distinct idea or list item requires its own set of comprehensive paragraphs.)"

    return f'''
{language_instruction}Write a comprehensive, in-depth tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

**PRIMARY GOAL: LOSSLESS, RECREATE-LEVEL UNDERSTANDING**
Your main objective is to explain this abstraction with such technical depth and focus on the project's **DYNAMICALLY IDENTIFIED technology stack** (languages, frameworks, libraries, CS principles) that a developer could, in principle, recreate a similar implementation and understand its design rationale. All explanations must be **LOSSLESS**.

**CORE EXPLANATION MANDATE (CEM) - REMINDER:**
(The full CEM is defined internally in this prompt template. All structural elements require CEM adherence.)
**Every heading, sub-heading, list item, code example, diagram, and distinct conceptual point in this chapter MUST be expanded with substantial, multi-sentence paragraphs (minimum 5-7 sentences each). These paragraphs MUST cover: The "Why", "How", "Design Rationale", "Technical Trade-offs", "CS Principles & Architectural Patterns", and "Impact & Interactions", all grounded in the DYNAMICALLY IDENTIFIED specific technologies of this project.**

Concept Details{concept_details_note}: {cem_application_instruction}
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note}:
{full_chapter_listing}

Context from previous chapters{prev_summary_note}:
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}
{cem_application_instruction if previous_chapters_summary else ""}

Relevant Code Snippets: {cem_application_instruction}
{file_context_str if file_context_str else "No specific code snippets provided for this abstraction."}

**CHAPTER CONTENT INSTRUCTIONS:**
(Adhere to the Core Explanation Mandate (CEM) for all points and structural elements below.)

1.  **Chapter Heading & Introduction:**
    *   Start with: `# Chapter {{chapter_num}}: {{abstraction_name}}`.
    *   Follow with introductory paragraphs explaining the chapter's scope, the abstraction's importance to the project, and what the reader will learn. {cem_application_instruction}

2.  **Transition (if not the first chapter):**
    *   Provide a brief, meaningful transition from the previous chapter, referencing it with a Markdown link. Explain its relevance to the current chapter. {cem_application_instruction}

3.  **Problem Statement Section:** {cem_application_instruction}
    (Elaborate on each of the following aspects in detailed, multi-sentence paragraphs, adhering fully to the CEM.)
    *   The specific technical challenge this abstraction solves within the project's DYNAMICALLY IDENTIFIED technology stack.
    *   Architectural consequences of lacking this abstraction, and *why* this abstraction is an effective solution given the DYNAMICALLY IDENTIFIED technologies.
    *   A concrete technical example of the problem (with code if appropriate, reflecting the DYNAMICALLY IDENTIFIED language/framework).
    *   A real-world analogy, immediately and thoroughly mapped back to the technical domain, explaining how the problem manifests and is solved using the DYNAMICALLY IDENTIFIED technologies and patterns, including the *reasoning* for this mapping.

4.  **Dedicated Technical Sections for Major Aspects:**
    (Each major aspect of the abstraction should have its own H2/H3 heading. Each heading requires full CEM elaboration.) {cem_application_instruction}
    *   For each aspect: provide deep technical explanations of internal mechanisms; explain applied design patterns with DYNAMICALLY IDENTIFIED implementation details and justification; discuss technical trade-offs; describe boundary conditions, edge cases, error handling; explore DYNAMICALLY IDENTIFIED performance characteristics and scalability.

5.  **Code Examples:** {cem_application_instruction}
    *   Include ALL relevant, complete code examples. Annotate non-trivial lines, explaining *how* and *why* with DYNAMICALLY IDENTIFIED features.
    *   Highlight and explain DYNAMICALLY IDENTIFIED patterns, idioms, language/framework features, justifying choices.
    *   Note and explain DYNAMICALLY IDENTIFIED optimizations/performance considerations.
    *   Compare implementation approaches if applicable, evaluating design choices within the DYNAMICALLY IDENTIFIED context.
    *   **Each code block must be immediately followed by a detailed analysis adhering to the CEM.**

6.  **Lists (Bulleted or Numbered):** {cem_application_instruction}
    *   **Every single list item is a topic for full, multi-paragraph CEM elaboration.** Do not treat items as brief entries.
    *   **Example of CEM-level depth for a list item (e.g., "Define entity relationships" in an ORM context):**
        *You would provide detailed paragraphs covering:* Why the DYNAMICALLY IDENTIFIED ORM was chosen; how it defines relationships (e.g., decorators, annotations); the implications for data integrity and query efficiency (eager vs. lazy loading rationale); how DYNAMICALLY IDENTIFIED ORM features mitigate issues like N+1; the reasoning behind chosen cascade options; how the ORM translates these to database queries; and the trade-offs involved in this specific ORM-based approach compared to alternatives for this project. This explanation must be rich, specific to the DYNAMICALLY IDENTIFIED tech, and many sentences long for each core aspect of that single list item.

7.  **Internal Implementation Details:**
    *   **Walkthrough:** Provide a non-code/code-light step-by-step walkthrough of the abstraction's operation, explaining DYNAMICALLY IDENTIFIED component participation and design flow. {cem_application_instruction}
    *   **Sequence Diagram:** Include a detailed Mermaid `sequenceDiagram` (5-8 participants) for a dummy example. Follow with a thorough explanation. {cem_application_instruction}
    *   **Deep Dive into Code (organized by subheadings, each adhering to CEM):** {cem_application_instruction}
        *   Initialization sequences & DYNAMICALLY IDENTIFIED DI/management strategies (explain benefits).
        *   Runtime behavior, control flow, algorithmic complexity (how DYNAMICALLY IDENTIFIED features support this, why algorithms chosen).
        *   Memory management in the DYNAMICALLY IDENTIFIED context (lifecycles, caching, addressing leaks).
        *   Concurrency/threading using DYNAMICALLY IDENTIFIED patterns (how they manage it effectively).
        *   Error/exception propagation & handling in the DYNAMICALLY IDENTIFIED stack (why strategy is robust).
        *   Performance optimizations implemented using DYNAMICALLY IDENTIFIED techniques (how they work, their impact).

8.  **Interactions with Other Abstractions:** {cem_application_instruction}
    *   Explicitly discuss interactions with EVERY related abstraction. Explain technically (data/control flow, dependencies) using DYNAMICALLY IDENTIFIED framework mechanisms, justifying *why* these interaction patterns were selected. Use Markdown links for other chapters{link_lang_note}.

9.  **Advanced Topics (each as a subheading with CEM elaboration):** {cem_application_instruction}
    *   Cover all aspects: core functionality, DYNAMICALLY IDENTIFIED initialization/configuration (with rationale), error handling/recovery (and resilience contribution), DYNAMICALLY IDENTIFIED performance characteristics/optimizations, integration patterns (with justification for choices), architectural patterns realized (and DYNAMICALLY IDENTIFIED advantages), known DYNAMICALLY IDENTIFIED limitations (and workarounds).

10. **Technical Best Practices Section:** {cem_application_instruction}
    (This heading and each sub-point below require full CEM elaboration.)
    *   Common pitfalls/anti-patterns in the DYNAMICALLY IDENTIFIED context (explaining why problematic).
    *   Optimized usage patterns for different scenarios (with technical reasoning for DYNAMICALLY IDENTIFIED tools, why optimal).
    *   Scaling considerations with DYNAMICALLY IDENTIFIED tech (how design accounts for it).
    *   Version-specific issues of DYNAMICALLY IDENTIFIED tools.

**GENERAL STYLE AND CONTENT MANDATES:**
-   Maintain a highly technical, authoritative, and precise writing style suitable for senior developers{tone_note}.
-   **"Thinking for Oneself" / Design Rationale:** This is integral to the CEM. For every significant technical point, explain not just the "what" and "how" but critically, the "why"—the design rationale, the reasons for choosing specific DYNAMICALLY IDENTIFIED technologies or patterns, and potential alternatives.
-   **Analogies:** Use them to clarify complex DYNAMICALLY IDENTIFIED technical points, but always follow with a detailed mapping back to the specific technologies and rationale. The analogy explanation itself must adhere to the CEM.
-   **Conclusion:** Summarize key technical insights, design rationale, demonstrated CS principles/patterns (as implemented with DYNAMICALLY IDENTIFIED tools), and connections to the broader architecture. Transition to the next chapter with a Markdown link. {cem_application_instruction}
-   **EXCLUDE ALL TESTING-RELATED CONTENT.** Focus entirely on application logic for a LOSSLESS tutorial.
-   {code_comment_note} {mermaid_lang_note} {instruction_lang_note}

Output *only* the Markdown content for this chapter.
Now, directly provide a "technical" and "Computer Science"-friendly Markdown output (DON'T need ```markdown``` tags):
'''
