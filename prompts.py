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
    It emphasizes DYNAMICALLY IDENTIFYING the technology stack first, then finding the
    MAXIMUM number of technical abstractions, with LOSSLESS descriptions for
    RECREATE-LEVEL understanding.
    """
    return f"""
For the project `{project_name}`:

Codebase Context (a portion of the overall codebase):
{context}

{language_instruction}Your **PRIMARY TASK** is twofold:
1.  First, from the provided Codebase Context, **DYNAMICALLY IDENTIFY** the specific programming languages, frameworks (e.g., Spring Boot, React, Django), libraries (e.g., Pandas, Tokio, jQuery), architectural patterns (e.g., microservices, event-driven, layered, MVC, RESTful APIs), and core Computer Science principles (e.g., specific algorithms like sorting/searching if evident, data structures like hash maps/trees if their usage is central, concurrency models like async/await or actor model if clear).
2.  Second, using this **DYNAMICALLY IDENTIFIED TECHNOLOGICAL CONTEXT**, identify the **MAXIMUM POSSIBLE NUMBER** of distinct and significant **TECHNICAL** abstractions.

Abstractions can include (but are not limited to), and should be described *in terms of the DYNAMICALLY IDENTIFIED technologies*:
- Key architectural components (e.g., "Microservice for OrderProcessing using Spring Boot", "React Component for UserProfile UI", "Event-Driven Consumer for Kafka Topic X").
- Instantiations of common design patterns (e.g., "Factory for creating DataTransferObjects using Java", "Singleton for DatabaseConnectionPool in Python", "Observer pattern for UI updates in JavaScript with identified event library").
- Core algorithms or complex business logic units (e.g., "PricingCalculationEngine using identified currency library", "PathfindingAlgorithm implemented in C++ for identified graph structure").
- Significant data structures and their management (e.g., "In-memory Cache using identified caching library/idiom", "Custom Tree for representing identified domain hierarchy").
- Primary modules, classes, or interfaces that play a crucial role (e.g., "UserService Interface in Java", "DataRepository Class using identified ORM like Hibernate/SQLAlchemy").
- Critical operational flows or processing pipelines (e.g., "DataIngestionPipeline using identified ETL tools/libraries", "UserAuthenticationFlow with identified security framework like Spring Security/Passport.js").
- Important utility classes or functions that are widely used or encapsulate complex logic (e.g., "StringManipulationUtils specific to identified project needs", "DateHandlingService using identified date/time library").

NOTE: You are seeing only a portion of the codebase in this chunk. Identify ANY **technical** abstraction you can recognize based on the **DYNAMICALLY IDENTIFIED TECHNOLOGICAL CONTEXT** of this chunk, even if it seems incomplete from a global perspective. The goal is to capture ALL possible **technical** abstractions at multiple levels of granularity. Being exhaustive is critical - missing **technical** abstractions is worse than including minor ones, as long as they are technically significant and contribute to a **LOSSLESS, recreate-level understanding** of the system *through its DYNAMICALLY IDENTIFIED technologies*.

For each identified abstraction, provide:
1.  A concise `name`{name_lang_hint}. This name should be descriptive of its function within the **DYNAMICALLY IDENTIFIED TECHNOLOGICAL CONTEXT**.
2.  A "highly-technical" and "Computer Science" centric `description`{desc_lang_hint}. This description MUST BE **LOSSLESS** and aim for a **recreate-level understanding**. It should be at least 300 words and comprehensively explain:
    *   What the abstraction is and its primary purpose/responsibilities *within this specific codebase and its DYNAMICALLY IDENTIFIED technology stack*.
    *   The problem it solves or the functionality it provides, explained *in terms of the DYNAMICALLY IDENTIFIED languages, frameworks, or libraries being used*.
    *   Core internal mechanisms: How it works, detailing *how specific features of the DYNAMICALLY IDENTIFIED technology stack (e.g., language constructs, framework APIs, library functions) are leveraged* to achieve its behavior.
    *   Key inputs it processes, outputs it generates, and significant side effects it might have, explained with data types or structures common in the *DYNAMICALLY IDENTIFIED language/framework*.
    *   High-level interactions with other potential abstractions or system components, describing the *nature of these interactions (e.g., method calls using DYNAMICALLY IDENTIFIED language features, event emissions using an DYNAMICALLY IDENTIFIED event system, data sharing via an DYNAMICALLY IDENTIFIED state management approach)*.
    *   Underlying CS principles (e.g., if it's a caching mechanism, mention hash tables and O(1) lookups, and how the *DYNAMICALLY IDENTIFIED language's dictionary/map or a specific caching library* implements this).
    *   If it employs a known design pattern, name the pattern and detail *how it is implemented using the specific constructs of the DYNAMICALLY IDENTIFIED language or framework*.
    *   A brief real-world analogy, BUT this analogy MUST be immediately and thoroughly mapped back to the technical specifics of the abstraction *as it is realized using the DYNAMICALLY IDENTIFIED technologies*. Each part of the analogy must correspond to a concrete technical aspect.
3.  A list of relevant `file_indices` (integers) using the format `idx # path/comment`, referring to the files listed below that contribute to this abstraction.

IMPORTANT GUIDANCE:
- Identify abstractions at ALL levels of granularity – from high-level architectural patterns (e.g., "Message Queue Consumer Service *if a message queue library like RabbitMQ or Kafka is DYNAMICALLY IDENTIFIED*") down to significant utility functions, classes, or modules, as long as they are central to the codebase portion provided and reflect the **DYNAMICALLY IDENTIFIED** tech.
- For any **DYNAMICALLY IDENTIFIED** framework or technology stack, identify both technology-specific abstractions (e.g., "Angular Component", "Spring Boot Service", "Rust Tokio Task Executor") and application-specific implementations built upon them.
- Consider common abstraction categories based on **DYNAMICALLY IDENTIFIED** technologies: Data models/entities (and how they are defined/managed by an **DYNAMICALLY IDENTIFIED** ORM or language feature), Services/APIs, UI components (if UI framework **DYNAMICALLY IDENTIFIED**), State management (if state library **DYNAMICALLY IDENTIFIED**), Configuration handlers, Core business logic modules, Domain entities, Controllers/Routers (as per **DYNAMICALLY IDENTIFIED** framework), Authentication/Security mechanisms, Event handling/processing systems (if **DYNAMICALLY IDENTIFIED**).

CRITICAL INSTRUCTION: Your primary task is to identify the **MAXIMUM number** of core **technical** abstractions of the application necessary for a **LOSSLESS, recreate-level understanding**. You MUST NOT identify any form of software testing (including but not limited to unit tests, integration tests, end-to-end (E2E) tests, performance tests, etc.), testing frameworks, test runners, test utilities, or any code, files, or concepts primarily related to testing as an abstraction. If you encounter testing-related elements, ignore them for the purpose of abstraction identification. Focus exclusively on the application's runtime behavior, business logic, and core architectural components as realized by its **DYNAMICALLY IDENTIFIED** technology stack.

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
    "name": "[Example] Asynchronous Task Processor (using DYNAMICALLY IDENTIFIED Library X){name_lang_hint}",
    "description": "This abstraction is responsible for managing and executing background tasks asynchronously. It leverages [DYNAMICALLY IDENTIFIED Library X, e.g., Celery for Python, Tokio for Rust] to achieve non-blocking operations. Its core mechanism involves a task queue (potentially DYNAMICALLY IDENTIFIED as RabbitMQ or Redis if context allows) where tasks are enqueued. Worker processes, managed by [DYNAMICALLY IDENTIFIED Library X], pick up these tasks and execute them. For instance, if the codebase uses Python with Celery (DYNAMICALLY IDENTIFIED), this abstraction would encapsulate Celery app configuration, task definitions (decorated with `@celery.task`), and potentially custom routing logic. It solves the problem of long-running operations blocking the main application thread, crucial for [DYNAMICALLY IDENTIFIED application type, e.g., web servers needing responsive UIs]. Internally, it might use [DYNAMICALLY IDENTIFIED language features like Python's `async/await` if Celery tasks are async] or manage a pool of worker processes/threads as configured by Celery. Inputs are typically serialized task parameters, and outputs could be results stored in a backend (e.g., database via a DYNAMICALLY IDENTIFIED ORM) or notifications sent via a DYNAMICALLY IDENTIFIED event system. This is analogous to a restaurant kitchen's order system where waiters (main threads) take orders and pass them to specialized cooks (worker processes) who prepare dishes (tasks) without making the waiter stand by, thus allowing the waiter to serve more customers (handle more requests). The 'order ticket' is like the serialized task, 'specialized cooks' are like Celery workers, and the 'pass-through window' for orders is like the message queue.{desc_lang_hint}",
    "file_indices": [
      "0 # path/to/task_definitions.py",
      "3 # path/to/celery_config.py"
    ]
  }},
  {{
    "name": "[Example] Configuration Management Service (leveraging DYNAMICALLY IDENTIFIED Framework Y feature){name_lang_hint}",
    "description": "This service provides a centralized way to access application configuration. It likely uses [DYNAMICALLY IDENTIFIED Framework Y's configuration module, e.g., Spring Boot's `@ConfigurationProperties`, NestJS's `ConfigService`]. It reads configuration from various sources (e.g., environment variables, .properties/.yaml files - DYNAMICALLY IDENTIFY which if possible from context) and makes them available application-wide, often through dependency injection provided by [DYNAMICALLY IDENTIFIED Framework Y]. This solves the problem of scattered configuration settings and provides a consistent interface for all modules to retrieve parameters like database URLs, API keys, feature flags, etc. It might implement features like type validation for configuration values or dynamic reloading if supported by the [DYNAMICALLY IDENTIFIED Framework Y feature]. This is like a central control panel for a complex machine, where all settings are managed in one place and can be easily adjusted or queried by different parts of the machine.{desc_lang_hint}",
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
    Emphasizes LOSSLESS information transfer by describing interactions via
    DYNAMICALLY IDENTIFIED technologies for a RECREATE-LEVEL understanding.
    """
    return f"""
Based on the following abstractions (which may include details about their **DYNAMICALLY IDENTIFIED technology stack** and implementation) and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions, their detailed descriptions including **DYNAMICALLY IDENTIFIED technologies**, and potentially related Code Snippets):
{context}

{language_instruction}Your task is to analyze these abstractions and their context to describe their interrelationships in a **LOSSLESS** manner, facilitating a **recreate-level understanding** of the system's architecture.

Please provide:
1.  A high-level `summary` of the project's main purpose and functionality. This summary must be technically precise, **LOSSLESSLY** conveying key architectural choices evident from the abstractions (e.g., "This project appears to be a [**DYNAMICALLY IDENTIFIED architecture, e.g., event-driven microservice system**] built using [**DYNAMICALLY IDENTIFIED primary language/framework, e.g., Java with Spring Boot**]..."), and use markdown formatting with **bold** and *italic* text to emphasize important **DYNAMICALLY IDENTIFIED** concepts or technologies{lang_hint}.
2.  A comprehensive list (`relationships`) describing ALL significant interactions between these abstractions. Each relationship description must be detailed enough to ensure **LOSSLESS** information transfer about how abstractions connect and influence each other. For each relationship, specify:
    *   `from_abstraction`: Index and name of the source abstraction (e.g., `0 # AbstractionName1`).
    *   `to_abstraction`: Index and name of the target abstraction (e.g., `1 # AbstractionName2`).
    *   `label`: A brief, descriptive label for the interaction{lang_hint}. This label MUST be highly specific and describe the *mechanism* of interaction, ideally referencing the **DYNAMICALLY IDENTIFIED technologies involved**, to ensure **LOSSLESS** capture of the interaction's nature. Examples:
        *   "Invokes via REST API call (using **DYNAMICALLY IDENTIFIED** HTTP client, e.g., Axios, OkHttp)"
        *   "Sends message to (via **DYNAMICALLY IDENTIFIED** Message Queue, e.g., RabbitMQ, Kafka topic)"
        *   "Depends on for data persistence (through **DYNAMICALLY IDENTIFIED** ORM, e.g., SQLAlchemy, Hibernate)"
        *   "Consumes events from (using **DYNAMICALLY IDENTIFIED** event bus/library, e.g., RxJS, Akka Streams)"
        *   "Extends functionality of (via **DYNAMICALLY IDENTIFIED** inheritance/composition in language X)"
        *   "Manages lifecycle of (using **DYNAMICALLY IDENTIFIED** framework Y's component model)"
        *   "Provides configuration to (through **DYNAMICALLY IDENTIFIED** DI mechanism of framework Z)"
        *   "Composes UI with (as a **DYNAMICALLY IDENTIFIED** UI component in framework A)"

    Consider a WIDE VARIETY of technology-agnostic relationship types, but ALWAYS specify them *in terms of the **DYNAMICALLY IDENTIFIED technology stack*** if possible, to maintain **LOSSLESS** detail:
    - Structural: "Is part of (e.g., as a module in a **DYNAMICALLY IDENTIFIED** build system)", "Contains (e.g., a **DYNAMICALLY IDENTIFIED** data structure)", "Composes (e.g., using **DYNAMICALLY IDENTIFIED** component model)"
    - Dependency: "Requires (e.g., a **DYNAMICALLY IDENTIFIED** library/module)", "Is configured by (e.g., a **DYNAMICALLY IDENTIFIED** configuration file format or service)", "Uses services from (e.g., a **DYNAMICALLY IDENTIFIED** internal API)"
    - Data Flow: "Produces data for (e.g., a **DYNAMICALLY IDENTIFIED** data pipeline stage)", "Consumes data from (e.g., a **DYNAMICALLY IDENTIFIED** database table via an ORM)"
    - Conceptual/Logical: "Specializes (e.g., a **DYNAMICALLY IDENTIFIED** base class/interface)", "Implements (e.g., a **DYNAMICALLY IDENTIFIED** API specification)", "Orchestrates (e.g., a series of calls to **DYNAMICALLY IDENTIFIED** services)"
    - Invocation/Control Flow: "Invokes (e.g., a method from a **DYNAMICALLY IDENTIFIED** class/module)", "Triggers (e.g., an event in a **DYNAMICALLY IDENTIFIED** event system)"

    The relationship should ideally be backed by evidence in the provided code context or be a clear architectural or logical link between the abstractions, explained via their ***DYNAMICALLY IDENTIFIED technological roles and interactions*** to ensure **LOSSLESS** information.
    Be thorough in identifying ALL meaningful relationships, ensuring complete coverage of how abstractions interact *using their **DYNAMICALLY IDENTIFIED implementation details for a LOSSLESS architectural view***.

IMPORTANT INSTRUCTIONS:
1. CRITICAL: EVERY abstraction listed MUST be involved in at least ONE meaningful relationship (either as a source or a target) to ensure a **LOSSLESS** representation of the system. Do NOT leave any abstraction isolated. If a direct interaction is not obvious from the immediate code, infer logical or conceptual connections based on their descriptions, their likely roles in the ***DYNAMICALLY IDENTIFIED architecture***, and common patterns in the ***DYNAMICALLY IDENTIFIED technology stack***.
2. Each abstraction index (from 0 to {num_abstractions-1}) MUST appear at least once across all `from_abstraction` or `to_abstraction` fields.
3. Use ONLY the abstraction indices and names (e.g., `0 # AbstractionName1`) from the list above for `from_abstraction` and `to_abstraction` fields. DO NOT use file indices or generic project names.
4. The indices in `from_abstraction` and `to_abstraction` must reference the abstraction list (0 to {num_abstractions-1}).
5. Exclude any relationships that are solely testing-related. Focus on the application's runtime architecture and logic.
6. Be COMPREHENSIVE. It's better to include a plausible conceptual relationship (explained via the **DYNAMICALLY IDENTIFIED** tech for **LOSSLESS** understanding) than to leave an abstraction disconnected.

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
  "summary": "This project appears to be a [**DYNAMICALLY IDENTIFIED architecture, e.g., serverless data processing pipeline**] implemented in [**DYNAMICALLY IDENTIFIED language, e.g., *Python***] using [**DYNAMICALLY IDENTIFIED key frameworks/libraries, e.g., AWS Lambda, Pandas, and S3**]. Its main purpose is to [project function, e.g., ingest raw data, transform it according to defined business rules, and store the results for analytics]. Key abstractions like [Abstraction A name] and [Abstraction B name] (potentially implemented using [**DYNAMICALLY IDENTIFIED tech for A**] and [**DYNAMICALLY IDENTIFIED tech for B**] respectively) suggest a focus on [identified core functionality, e.g., efficient data manipulation and scalable event handling].{lang_hint}",
  "relationships": [
    {{
      "from_abstraction": "0 # DataIngestionLambda",
      "to_abstraction": "1 # DataTransformationService (Pandas)",
      "label": "Passes raw data to (via **DYNAMICALLY IDENTIFIED** S3 event trigger and **DYNAMICALLY IDENTIFIED** data format, e.g., Parquet){lang_hint}"
    }},
    {{
      "from_abstraction": "1 # DataTransformationService (Pandas)",
      "to_abstraction": "2 # ReportingModule (using DYNAMICALLY IDENTIFIED DB client)",
      "label": "Writes transformed data to (using **DYNAMICALLY IDENTIFIED** DB client, e.g., psycopg2, to **DYNAMICALLY IDENTIFIED** PostgreSQL DB){lang_hint}"
    }}
    // ... include ALL relationships between ALL abstractions, with labels explaining the mechanism via DYNAMICALLY IDENTIFIED TECHNOLOGIES
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
    This prompt guides the LLM to use DYNAMICALLY IDENTIFIED technology concepts
    to create meaningful links.
    """
    return f"""
{language_instruction}Based on the abstractions in the project (which may include details on their **DYNAMICALLY IDENTIFIED technology stack**) and the existing relationships already identified,
please generate SPECIFIC and CONCEPTUALLY MEANINGFUL relationships for each of these disconnected abstractions.

PROJECT CONTEXT: {project_name}

For each disconnected abstraction, create at least one relationship connecting it to another abstraction.
The relationship must be conceptually valid and reflect a real architectural connection *based on the likely roles within the DYNAMICALLY IDENTIFIED technology stack or architecture*.

Disconnected abstractions that need relationships:
{disconnected_abstractions}

Context from all abstractions (note their potential DYNAMICALLY IDENTIFIED technologies):
{abstraction_listing}

Existing relationships for context (note their DYNAMICALLY IDENTIFIED interaction mechanisms):
{existing_relationships}

IMPORTANT GUIDANCE:
1. Create ONLY meaningful, relationships based on the likely architectural roles of these abstractions *within their DYNAMICALLY IDENTIFIED technology context*.
2. Each relationship should reflect a standard software architecture concept, *ideally specified with the DYNAMICALLY IDENTIFIED technology if inferable*:
   - STRUCTURAL: "Contains (e.g., as a module managed by **DYNAMICALLY IDENTIFIED build tool**)", "Composes (via **DYNAMICALLY IDENTIFIED component model**)"
   - BEHAVIORAL: "Calls (e.g., method from **DYNAMICALLY IDENTIFIED class/API**)", "Delegates to (another **DYNAMICALLY IDENTIFIED service**)"
   - DEPENDENCY: "Depends on (for **DYNAMICALLY IDENTIFIED configuration/service**)", "Uses (**DYNAMICALLY IDENTIFIED library feature**)"
   - INHERITANCE/IMPLEMENTATION: "Specializes (**DYNAMICALLY IDENTIFIED base class**)", "Implements (**DYNAMICALLY IDENTIFIED interface**)"
   - COMMUNICATION: "Sends data to (via **DYNAMICALLY IDENTIFIED protocol/queue**)", "Receives data from (**DYNAMICALLY IDENTIFIED event source**)"
3. Ensure relationships accurately reflect the software architecture domain rather than generic connections, grounding them in the **DYNAMICALLY IDENTIFIED technological context**.
4. Each disconnected abstraction must be connected to at least one other abstraction in a meaningful way.
5. Be specific about each relationship type, using the **DYNAMICALLY IDENTIFIED technology** for context where possible.

Respond with ONLY a parseable JSON array containing the relationships with these three fields:
- from_abstraction: The source abstraction index and name (format: "0 # AbstractionName (potentially DYNAMICALLY IDENTIFIED tech)")
- to_abstraction: The target abstraction index and name (format: "1 # OtherAbstraction (potentially DYNAMICALLY IDENTIFIED tech)")
- label: A specific, technical relationship description{lang_hint} (e.g., "Provides configuration via **DYNAMICALLY IDENTIFIED DI** to", "Processes data from **DYNAMICALLY IDENTIFIED message queue**")

Here is the expected JSON format:
```json
[
  {{
    "from_abstraction": "5 # DisconnectedAbstraction (e.g., UserAuthModule using DYNAMICALLY IDENTIFIED JWT library)",
    "to_abstraction": "2 # ConnectedAbstraction (e.g., APIGateway using DYNAMICALLY IDENTIFIED framework)",
    "label": "Provides authentication tokens to (via DYNAMICALLY IDENTIFIED JWT mechanism){lang_hint}"
  }},
  {{
    "from_abstraction": "8 # AnotherDisconnectedAbstraction (e.g., CachingService using DYNAMICALLY IDENTIFIED Redis client)",
    "to_abstraction": "5 # DisconnectedAbstraction (e.g., UserAuthModule)",
    "label": "Caches session data for (using DYNAMICALLY IDENTIFIED Redis commands){lang_hint}"
  }}
  // Include a relationship for EACH disconnected abstraction, grounded in DYNAMICALLY IDENTIFIED tech.
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
    Generate the prompt for determining the chapter order using a "Tabulation" approach
    for RECREATE-LEVEL understanding, considering DYNAMICALLY IDENTIFIED dependencies.
    """
    return f"""
Given the following project abstractions and their relationships for the project `{project_name}` (which may include details on their **DYNAMICALLY IDENTIFIED technology stack, implementation, and interdependencies**):

Abstractions (Index # Name){list_lang_note}:
{abstraction_listing}

Context about Project Summary and Abstraction Relationships (including interaction mechanisms via **DYNAMICALLY IDENTIFIED TECHNOLOGIES**):
{context}

Your task is to determine the optimal chapter order for a comprehensive technical tutorial of `{project_name}`. The primary goal of this tutorial is to enable a developer to achieve a **recreate-level understanding** of the codebase, where they could, in principle, reconstruct its core components and their interactions *based on its DYNAMICALLY IDENTIFIED technologies*.

To achieve this, the chapter order MUST follow a logical progression that facilitates deep understanding and mental model construction. Employ a strategy inspired by the **"Tabulation" approach from Dynamic Programming**: each chapter should build upon the established knowledge from previous chapters, incrementally constructing a complete and **LOSSLESS** understanding of the system *as it is built with its DYNAMICALLY IDENTIFIED technologies*.

Consider these principles for ordering:
1.  **Dependency-First (Conceptual and Technical, based on DYNAMICALLY IDENTIFIED context)**:
    *   Explain foundational or prerequisite abstractions before those that depend on or build upon them. This applies to both conceptual dependencies (e.g., a core data model before a service that uses it) and technical dependencies (e.g., a base class or utility module before its consumers; a messaging infrastructure before services that publish/subscribe to it, especially if these are **DYNAMICALLY IDENTIFIED** from the context).
    *   Analyze the provided `relationships` (which detail interaction mechanisms via **DYNAMICALLY IDENTIFIED TECHNOLOGIES**) to infer these dependencies for a **LOSSLESS** flow of information.
2.  **Build from Core to Periphery (based on DYNAMICALLY IDENTIFIED architecture)**:
    *   Start with the most central, architecturally significant, or fundamental abstractions that define the core purpose or structure of the project (based on the **DYNAMICALLY IDENTIFIED architecture**).
    *   Gradually move towards more specialized, supporting, or peripheral abstractions.
3.  **Minimize Forward References for Clarity**: Structure the order to minimize the need for a reader to understand concepts that haven't been explained yet. While some forward referencing might be unavoidable in complex systems, strive for a flow that builds knowledge incrementally, vital for **recreate-level understanding** of the *DYNAMICALLY IDENTIFIED system*.
4.  **Complexity Progression**: If possible, introduce simpler or more self-contained abstractions before highly complex or heavily interconnected ones, assuming dependencies (derived from **DYNAMICALLY IDENTIFIED interactions**) allow.
5.  **User/Entry-Point Perspective (If DYNAMICALLY IDENTIFIABLE)**: If the system has clear user-facing entry points or primary use-case flows (and these can be **DYNAMICALLY IDENTIFIED** from the abstractions, e.g., an API Gateway, a main UI component), it might be logical to start with these high-level interaction points before diving into their underlying components. However, balance this with the dependency-first principle to ensure a **LOSSLESS** buildup of knowledge about the *DYNAMICALLY IDENTIFIED technologies*.

Inspired by the "Tabulation" approach, aim for an order where each chapter builds upon the established knowledge from previous chapters, ensuring a cohesive and **recreate-level understanding** of the system's *DYNAMICALLY IDENTIFIED components and architecture*.

IMPORTANT: Do not prioritize testing frameworks, test utilities, or any testing-related abstractions in your ordering. Focus on explaining the core functionality and architecture of the application itself to achieve a **LOSSLESS** and functional comprehension of its *DYNAMICALLY IDENTIFIED implementation*.

RESPONSE FORMAT REQUIREMENTS:
1. Output ONLY a JSON5 array with NO explanatory text before or after.
2. Do NOT include any explanation, discussion, or notes about the JSON structure.
3. Do NOT describe what you're going to do - just provide the JSON5 directly.
4. Your entire response must be parseable as valid JSON5.
5. Start your response with the opening bracket "[" and end with the closing bracket "]".
6. Each array element must be a string in the format "idx # AbstractionName (briefly noting its DYNAMICALLY IDENTIFIED core tech if applicable)".
7. Include ALL abstractions in your ordered list.

Here is the exact format to follow. Begin your response immediately with this JSON5 structure:

[
  "2 # [Example] CoreDataModel (Defines foundational structures used by DYNAMICALLY IDENTIFIED ORM X)",
  "0 # [Example] ConfigurationService (Provides settings for DYNAMICALLY IDENTIFIED framework Y)",
  "1 # [Example] MainBusinessLogicService (Uses CoreDataModel, configured by ConfigurationService, built on DYNAMICALLY IDENTIFIED framework Y)",
  "3 # [Example] APIGateway (Exposes MainBusinessLogicService via DYNAMICALLY IDENTIFIED protocol Z, e.g., REST with Spring MVC)"
  // ... include ALL abstractions in the optimal learning and recreation-focused order, considering DYNAMICALLY IDENTIFIED dependencies and architecture
]"""


def get_write_chapter_prompt(
    project_name,
    chapter_num,
    abstraction_name,
    abstraction_description, # This description already contains DYNAMICALLY IDENTIFIED tech details
    full_chapter_listing,
    file_context_str, # This context should highlight DYNAMICALLY IDENTIFIED tech
    previous_chapters_summary, # This summary might also reference DYNAMICALLY IDENTIFIED tech
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
    This prompt enforces the Core Explanation Mandate (CEM) for extreme depth,
    focusing on LOSSLESS, RECREATE-LEVEL understanding through DYNAMICALLY IDENTIFIED
    technologies and "Thinking for Oneself" (design rationale).
    """

    # The Core Explanation Mandate (CEM) is applied via the `cem_instruction_snippet`.
    # It requires detailed paragraphs (min 5-7 sentences EACH) for EVERY structural element, covering:
    # 1. "Why": Purpose/problem solved within DYNAMICALLY IDENTIFIED tech stack.
    # 2. "How": Mechanisms using DYNAMICALLY IDENTIFIED language features, framework APIs, library functions.
    # 3. "Design Rationale ('Thinking for Oneself')": Reasons for specific DYNAMICALLY IDENTIFIED tech/pattern choices, discussion of alternatives.
    # 4. "Technical Trade-offs": Compromises in the DYNAMICALLY IDENTIFIED stack.
    # 5. "CS Principles & Architectural Patterns": How they manifest in DYNAMICALLY IDENTIFIED implementation; why relevant.
    # 6. "Impact & Interactions": Broader implications for DYNAMICALLY IDENTIFIED architecture.
    # Adherence is paramount for LOSSLESS, recreate-level understanding, grounded in DYNAMICALLY IDENTIFIED project technologies.

    cem_instruction_snippet = \
        "(Apply the Core Explanation Mandate (CEM) here: for this point and ALL its sub-points/elements, provide detailed paragraphs (min 5-7 sentences EACH). These paragraphs must cover the 'Why' (purpose/problem solved), 'How' (mechanisms), 'Design Rationale' (including alternatives considered), 'Technical Trade-offs', 'CS Principles & Architectural Patterns' applied, and 'Impact/Interactions'. All explanations MUST be grounded in the DYNAMICALLY IDENTIFIED specific programming languages, frameworks, libraries, and architectural patterns of this project to ensure a LOSSLESS, recreate-level understanding. Each distinct idea, list item, or code block requires its own set of comprehensive CEM paragraphs.)"

    return f'''\
{language_instruction}Write a comprehensive, in-depth tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

**PRIMARY GOAL: LOSSLESS, RECREATE-LEVEL UNDERSTANDING via DYNAMICALLY IDENTIFIED TECHNOLOGIES**
Your main objective is to explain this abstraction with such technical depth and focus on the project's **DYNAMICALLY IDENTIFIED technology stack** (languages, frameworks, libraries, CS principles, architectural patterns identified from code) that a developer could, in principle, recreate a similar implementation and thoroughly understand its design rationale. All explanations must be **LOSSLESS** and deeply technical.

**CORE EXPLANATION MANDATE (CEM) - CRITICAL REMINDER:**
For **EVERY** structural element in this chapter (ALL headings H1-H6, ALL sub-headings, EVERY list item in bulleted or numbered lists, EVERY code example, EVERY diagram, and EVERY distinct conceptual point introduced), you MUST provide one or more detailed explanatory PARAGRAPHS. Each set of paragraphs for an element must be substantial (minimum 5-7 sentences EACH, or more if complexity warrants). These paragraphs are the CORE of the chapter and must provide in-depth technical explanations covering:
1.  The **"Why"**: The specific problem this element addresses, its purpose, and its significance *within the DYNAMICALLY IDENTIFIED technology stack of this project*.
2.  The **"How"**: The underlying mechanisms, detailing the use of *DYNAMICALLY IDENTIFIED language features, framework capabilities, or library functions*. Explain how these specific technologies are practically applied.
3.  **Design Rationale ("Thinking for Oneself")**: The reasons *why this specific DYNAMICALLY IDENTIFIED approach, technology, or pattern was likely chosen* for this codebase. Crucially, *discuss potential alternative DYNAMICALLY IDENTIFIED technologies or patterns* that could have been used and explain why they might have been considered and ultimately accepted or dismissed in this specific context.
4.  **Technical Trade-offs**: Any compromises made (e.g., performance vs. readability, flexibility vs. complexity, development speed vs. long-term maintainability) due to the chosen approach *within the DYNAMICALLY IDENTIFIED stack*.
5.  **CS Principles & Architectural Patterns**: Relevant underlying computer science concepts (specific algorithms, data structures, concurrency models, established architectural patterns like MVC, Microservices, Event-Driven etc.) and how they manifest in this specific *DYNAMICALLY IDENTIFIED implementation*. Explain *why* these principles/patterns are relevant and beneficial here.
6.  **Impact & Interactions**: How this element interacts with other parts of the system and its broader implications for the *DYNAMICALLY IDENTIFIED architecture*.
Adherence to this CEM is paramount. All explanations MUST be grounded in the **DYNAMICALLY IDENTIFIED specific technologies** of this project.

Concept Details{concept_details_note} (This is the abstraction being explained; its description already includes DYNAMICALLY IDENTIFIED tech info from a previous step): {cem_instruction_snippet}
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note} (List of all chapters, names may be translated):
{full_chapter_listing}

Context from previous chapters{prev_summary_note} (Summary may be translated and reference DYNAMICALLY IDENTIFIED tech):
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}
{cem_instruction_snippet if previous_chapters_summary else ""}

Relevant Code Snippets (These snippets should be used to illustrate points and MUST be explained in terms of their DYNAMICALLY IDENTIFIED technologies): {cem_instruction_snippet}
{file_context_str if file_context_str else "No specific code snippets provided for this abstraction, but general principles of its DYNAMICALLY IDENTIFIED technology stack should be discussed."}

**CHAPTER CONTENT INSTRUCTIONS:**
(Adhere to the Core Explanation Mandate (CEM) for all points and structural elements below. Every instruction implies CEM application.)

1.  **Chapter Heading & Introduction:**
    *   Start with: `# Chapter {chapter_num}: {abstraction_name}`.
    *   Follow with introductory paragraphs. {cem_instruction_snippet}

2.  **Transition (if not the first chapter):**
    *   Provide a brief, meaningful transition. {cem_instruction_snippet}

3.  **Problem Statement Section:** {cem_instruction_snippet}
    (Elaborate on each aspect below in detailed CEM paragraphs.)
    *   The specific technical challenge this abstraction solves *using the DYNAMICALLY IDENTIFIED technology stack*.
    *   Architectural consequences of lacking this abstraction, and *why* this abstraction is an effective solution *given the DYNAMICALLY IDENTIFIED technologies*.
    *   A concrete technical example of the problem (with code reflecting the *DYNAMICALLY IDENTIFIED language/framework*).
    *   A real-world analogy, mapped back to the technical domain, explaining how the problem is solved *using DYNAMICALLY IDENTIFIED technologies/patterns, justifying the mapping*.

4.  **Dedicated Technical Sections for Major Aspects of the Abstraction:**
    (Each major aspect gets its own H2/H3 heading. Each heading requires full CEM elaboration.) {cem_instruction_snippet}
    *   For each aspect: deep technical explanations of internal mechanisms; applied design patterns with *DYNAMICALLY IDENTIFIED implementation details and justification*; technical trade-offs; boundary conditions, edge cases, error handling; *DYNAMICALLY IDENTIFIED performance characteristics and scalability solutions*.

5.  **Code Examples (illustrating DYNAMICALLY IDENTIFIED technologies):** {cem_instruction_snippet}
    *   Include ALL relevant, complete code examples. Annotate non-trivial lines, explaining *how* and *why* with *DYNAMICALLY IDENTIFIED features*.
    *   Highlight and explain *DYNAMICALLY IDENTIFIED patterns, idioms, language/framework features, justifying choices*.
    *   Note and explain *DYNAMICALLY IDENTIFIED optimizations/performance considerations*.
    *   Compare implementation approaches if applicable, evaluating design choices *within the DYNAMICALLY IDENTIFIED context*.
    *   **Each code block MUST be immediately followed by a detailed analysis adhering to the CEM.**

6.  **Lists (Bulleted or Numbered - EVERY item demands CEM depth):** {cem_instruction_snippet}
    *   **Every single list item is a topic for full, multi-paragraph CEM elaboration.** Do not treat items as brief entries. Each item must be expanded as if it were a sub-section heading.
    *   **Example of CEM-level depth for ONE list item (e.g., "Define entity relationships using DYNAMICALLY IDENTIFIED ORM X"):**
        Provide detailed paragraphs covering: Why DYNAMICALLY IDENTIFIED ORM X was chosen for relationship management; *how* it defines relationships (e.g., decorators, annotations, fluent API specific to ORM X); implications for data integrity and query efficiency (eager vs. lazy loading rationale *in ORM X*); how ORM X features mitigate issues like N+1; reasoning behind chosen cascade options *in ORM X*; how ORM X translates these to database queries; and trade-offs of this ORM X-based approach compared to alternatives for *this project's DYNAMICALLY IDENTIFIED stack*. This depth is for EACH list item.

7.  **Internal Implementation Details (grounded in DYNAMICALLY IDENTIFIED tech):**
    *   **Walkthrough:** Non-code/code-light step-by-step walkthrough of operation, explaining *DYNAMICALLY IDENTIFIED component participation and design flow*. {cem_instruction_snippet}
    *   **Sequence Diagram:** Detailed Mermaid `sequenceDiagram` (5-8 participants) for a dummy example relevant to the abstraction. Thorough explanation. {cem_instruction_snippet}
    *   **Deep Dive into Code (organized by subheadings, each adhering to CEM):** {cem_instruction_snippet}
        *   Initialization sequences & *DYNAMICALLY IDENTIFIED DI/management strategies* (explain benefits).
        *   Runtime behavior, control flow, algorithmic complexity (*how DYNAMICALLY IDENTIFIED features support this, why algorithms chosen*).
        *   Memory management *in the DYNAMICALLY IDENTIFIED context* (lifecycles, caching, addressing leaks).
        *   Concurrency/threading *using DYNAMICALLY IDENTIFIED patterns* (how they manage it effectively).
        *   Error/exception propagation & handling *in the DYNAMICALLY IDENTIFIED stack* (why strategy is robust).
        *   Performance optimizations implemented *using DYNAMICALLY IDENTIFIED techniques* (how they work, their impact).

8.  **Interactions with Other Abstractions (via DYNAMICALLY IDENTIFIED mechanisms):** {cem_instruction_snippet}
    *   Explicitly discuss interactions with EVERY related abstraction. Explain technically (data/control flow, dependencies) *using DYNAMICALLY IDENTIFIED framework mechanisms or language features*, justifying *why* these interaction patterns were selected. Use Markdown links for other chapters{link_lang_note}.

9.  **Advanced Topics (each as a subheading with CEM elaboration, focused on DYNAMICALLY IDENTIFIED tech):** {cem_instruction_snippet}
    *   Cover all aspects: core functionality; *DYNAMICALLY IDENTIFIED initialization/configuration (with rationale)*; error handling/recovery (*and resilience contribution via DYNAMICALLY IDENTIFIED tech*); *DYNAMICALLY IDENTIFIED performance characteristics/optimizations*; integration patterns (*with justification for DYNAMICALLY IDENTIFIED choices*); architectural patterns realized (*and DYNAMICALLY IDENTIFIED advantages*); known *DYNAMICALLY IDENTIFIED limitations (and workarounds)*.

10. **Technical Best Practices Section (in the DYNAMICALLY IDENTIFIED context):** {cem_instruction_snippet}
    (This heading and each sub-point below require full CEM elaboration.)
    *   Common pitfalls/anti-patterns *when using the DYNAMICALLY IDENTIFIED technologies of this abstraction* (explaining why problematic).
    *   Optimized usage patterns for different scenarios (*with technical reasoning for DYNAMICALLY IDENTIFIED tools, why optimal*).
    *   Scaling considerations *with DYNAMICALLY IDENTIFIED tech* (how design accounts for it).
    *   Version-specific issues or considerations of *DYNAMICALLY IDENTIFIED tools/libraries used*.

**GENERAL STYLE AND CONTENT MANDATES:**
-   Maintain a highly technical, authoritative, and precise writing style suitable for senior developers{tone_note}.
-   **"Thinking for Oneself" / Design Rationale:** Integral to the CEM. For every significant technical point, explain not just "what" and "how" but critically, the "why"—the design rationale, reasons for choosing specific **DYNAMICALLY IDENTIFIED** technologies/patterns, and potential alternatives.
-   **Analogies:** Use to clarify complex **DYNAMICALLY IDENTIFIED** technical points, but always follow with detailed mapping back to specific technologies and rationale. The analogy explanation itself must adhere to the CEM.
-   **Conclusion:** Summarize key technical insights, design rationale, demonstrated CS principles/patterns (as implemented with **DYNAMICALLY IDENTIFIED** tools), and connections to the broader architecture. Transition to the next chapter. {cem_instruction_snippet}
-   **EXCLUDE ALL TESTING-RELATED CONTENT.** Focus entirely on application logic for a LOSSLESS tutorial.
-   {code_comment_note} {mermaid_lang_note} {instruction_lang_note}

Output *only* the Markdown content for this chapter.
Now, directly provide a "technical" and "Computer Science"-friendly Markdown output (DON'T need ```markdown``` tags):
'''
