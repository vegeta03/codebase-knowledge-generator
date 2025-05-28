"""
Contains all the prompts used in the tutorial generation process.

This module centralizes all LLM prompts used throughout the codebase to ensure a single source of truth
and facilitate easy modifications. Prompts are organized by the node they belong to and structured as
functions that handle any variable substitution needed.

Inspired by Arthur Schopenhauer's "Thinking for Oneself" philosophy, these prompts emphasize:
- First-principles understanding over pattern matching
- Design rationale exploration ("why this, not that")
- Independent recreation capability rather than mere copying
- Tabulation-style incremental knowledge building
- Lossless information transfer for true comprehension
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
    Enhanced with Schopenhauer's "thinking for oneself" philosophy - emphasizing
    first-principles analysis, design rationale exploration, and lossless understanding
    that enables independent recreation rather than mere pattern recognition.
    """
    return f"""
For the project `{project_name}`:

Codebase Context (a portion of the overall codebase):
{context}

{language_instruction}**PHILOSOPHICAL FOUNDATION - "THINKING FOR ONESELF":**
As Schopenhauer emphasized, true understanding comes from thinking through problems independently rather than merely recognizing patterns. Your task is to analyze this codebase with **first-principles thinking** - understanding not just WHAT exists, but WHY it was designed this way, WHAT ALTERNATIVES were likely considered, and HOW someone could independently arrive at similar solutions.

**PRIMARY TASK - LOSSLESS ABSTRACTION IDENTIFICATION:**
1. **DYNAMICALLY IDENTIFY** the specific programming languages, frameworks, libraries, architectural patterns, and core Computer Science principles from the provided context.
2. **THINK FROM FIRST PRINCIPLES** about each abstraction - not just recognizing patterns, but understanding the fundamental problems they solve and why these specific solutions were chosen.
3. Identify the **MAXIMUM POSSIBLE NUMBER** of distinct and significant **TECHNICAL** abstractions that would enable **INDEPENDENT RECREATION** of the system.

**ENHANCED ABSTRACTION ANALYSIS:**
For each abstraction, think like an architect who must justify every design decision:

- **Problem-Solution Mapping**: What fundamental problem does this abstraction solve? Why is this problem worth solving?
- **Design Rationale**: Why was THIS specific approach chosen? What alternatives likely existed?
- **First-Principles Foundation**: What core CS principles or mathematical concepts underpin this design?
- **Evolutionary Context**: How might this abstraction have evolved from simpler solutions?
- **Recreation Pathway**: What knowledge would someone need to independently arrive at this solution?

Abstractions can include (analyzed through first-principles lens):
- **Architectural Components**: Not just "Spring Boot service" but "Dependency Injection Container solving object lifecycle management through inversion of control principle"
- **Design Pattern Instantiations**: Not just "Factory pattern" but "Object creation abstraction solving compile-time vs runtime type determination trade-offs"
- **Algorithmic Solutions**: Not just "sorting algorithm" but "comparison-based ordering solution optimizing for specific time/space constraints given data characteristics"
- **Data Structure Implementations**: Not just "cache" but "temporal locality exploitation using hash-based O(1) lookup with LRU eviction policy"
- **Operational Flows**: Not just "authentication flow" but "identity verification pipeline balancing security, usability, and performance through multi-factor validation"

**LOSSLESS DESCRIPTION REQUIREMENTS:**
Each abstraction description must enable **INDEPENDENT RECREATION** by including:

1. **Fundamental Problem Analysis** (100+ words): What core problem necessitated this abstraction? Why couldn't simpler approaches suffice?

2. **Design Rationale Deep-Dive** (150+ words): 
   - Why THIS specific solution over alternatives?
   - What trade-offs were made and why?
   - What constraints (performance, maintainability, team expertise) influenced the choice?
   - How does this solution align with broader architectural principles?

3. **First-Principles Mechanisms** (200+ words):
   - How does it work at the fundamental level?
   - What CS principles, algorithms, or mathematical concepts are employed?
   - How do the DYNAMICALLY IDENTIFIED technologies implement these principles?
   - What are the key invariants and assumptions?

4. **Recreation Pathway** (100+ words):
   - What knowledge domains would someone need to independently develop this?
   - What simpler versions might they build first?
   - What are the key insights that make this solution work?

5. **Alternative Analysis** (100+ words):
   - What other approaches could solve the same problem?
   - Why weren't they chosen?
   - Under what circumstances might alternatives be preferable?

6. **Technical Implementation Details** (150+ words):
   - Specific DYNAMICALLY IDENTIFIED language features, framework APIs, library functions used
   - Key data structures, algorithms, and their complexity characteristics
   - Integration patterns and interaction mechanisms
   - Performance characteristics and scalability considerations

7. **Analogical Understanding** (50+ words):
   - Real-world analogy that illuminates the core concept
   - Detailed mapping between analogy elements and technical implementation
   - Explanation of where the analogy breaks down and why

**CRITICAL ENHANCEMENT - TABULATION APPROACH:**
Structure your analysis to build understanding incrementally:
- Start with the simplest, most fundamental aspects
- Build complexity layer by layer
- Ensure each layer depends only on previously established concepts
- Make dependencies between concepts explicit

**EXCLUSIONS:**
- NO testing-related abstractions (focus on runtime behavior and business logic)
- NO pattern recognition without understanding (explain WHY patterns were chosen)
- NO generic descriptions (everything must be specific to this DYNAMICALLY IDENTIFIED context)

List of file indices and paths present in the context:
{file_listing_for_prompt}

**RESPONSE FORMAT:**
Output ONLY a JSON5 list with NO explanatory text. Each abstraction must include:
- `name`: Descriptive of function within DYNAMICALLY IDENTIFIED context{name_lang_hint}
- `description`: 750+ words covering all seven requirements above{desc_lang_hint}
- `file_indices`: Relevant file references

[
  {{
    "name": "[Example] Asynchronous Task Orchestration Engine (using DYNAMICALLY IDENTIFIED Celery + Redis){name_lang_hint}",
    "description": "**Fundamental Problem Analysis:** This abstraction addresses the critical challenge of maintaining application responsiveness while executing computationally expensive or I/O-bound operations. In web applications, long-running tasks (data processing, external API calls, file generation) would block request threads, creating poor user experience and potential system instability. The fundamental problem is the mismatch between user expectation of immediate feedback and the reality of time-consuming operations. Traditional synchronous execution creates a bottleneck where each request must complete before the next can begin, violating the principle of concurrent resource utilization that modern systems require.\n\n**Design Rationale Deep-Dive:** The choice of Celery with Redis as the message broker represents a sophisticated solution to distributed task execution. Celery was likely chosen over alternatives like RQ (Redis Queue) or custom threading solutions because it provides mature features like task routing, retries, monitoring, and horizontal scaling. Redis serves as both message broker and result backend, chosen over RabbitMQ for its simplicity and dual-purpose capability, though sacrificing some message durability guarantees. The architecture embraces the producer-consumer pattern at scale, where web processes produce tasks and dedicated worker processes consume them. This separation allows independent scaling of web and worker tiers based on different resource requirements. The trade-off accepts eventual consistency and potential message loss in exchange for high throughput and operational simplicity.\n\n**First-Principles Mechanisms:** At its core, this implements a distributed work queue using message-passing concurrency. The system leverages Redis's atomic operations (LPUSH/BRPOP) to ensure thread-safe task queuing without race conditions. Celery's serialization layer (pickle/JSON) transforms Python objects into transmittable messages, handling the fundamental challenge of moving code and data across process boundaries. The worker processes implement an event loop pattern, continuously polling for tasks and executing them in isolated contexts. Task routing uses consistent hashing or explicit queue naming to distribute work, while the result backend provides a key-value store for task outcomes. The system maintains task state through a finite state machine (PENDING → STARTED → SUCCESS/FAILURE/RETRY), enabling monitoring and error recovery.\n\n**Recreation Pathway:** To independently develop this solution, one would need understanding of: (1) Operating system process/thread models and their limitations, (2) Network programming and message serialization protocols, (3) Distributed systems concepts like eventual consistency and fault tolerance, (4) Database/cache design for high-throughput key-value operations, (5) Python's multiprocessing and asyncio libraries for concurrent execution. The evolutionary path might start with simple threading, progress to process pools, then to networked task distribution, finally adding features like persistence, monitoring, and fault recovery. Key insights include recognizing that task distribution is fundamentally a messaging problem, and that worker isolation prevents cascading failures.\n\n**Alternative Analysis:** Alternative approaches include: (1) Threading/asyncio within the web process - simpler but limited by GIL and memory sharing, (2) Custom message queues using databases - more control but requires significant infrastructure development, (3) Cloud-native solutions like AWS SQS/Lambda - eliminates infrastructure management but introduces vendor lock-in and cold start latency, (4) Actor model systems like Akka - provides stronger guarantees but requires different programming paradigms. Celery was likely chosen because it balances feature richness with Python ecosystem integration, though it sacrifices some performance compared to lower-level solutions.\n\n**Technical Implementation Details:** The implementation leverages Celery's decorator-based task definition (@celery.task) which registers functions in a global task registry. Redis connection pooling ensures efficient network resource usage while handling concurrent worker connections. Task serialization uses pickle for Python objects or JSON for cross-language compatibility, with compression for large payloads. The worker processes implement prefork model for CPU-bound tasks or eventlet/gevent for I/O-bound work. Result expiration policies prevent memory leaks in the result backend. Error handling includes exponential backoff for retries, dead letter queues for failed tasks, and circuit breakers for external service failures. Monitoring integration provides metrics on task throughput, latency, and failure rates.\n\n**Analogical Understanding:** This system resembles a restaurant kitchen where waiters (web processes) take orders and pass them through a window (Redis queue) to specialized cooks (worker processes) who prepare dishes (execute tasks) without making customers wait. The 'order tickets' are like serialized tasks, the 'kitchen manager' is like Celery's task router, and the 'completed order area' is like the result backend. The analogy breaks down in that restaurant orders are typically FIFO while task systems often need priority queuing and complex routing logic.{desc_lang_hint}",
    "file_indices": [
      "0 # path/to/task_definitions.py",
      "3 # path/to/celery_config.py"
    ]
  }}
  // ... include ALL distinct abstractions with full first-principles analysis
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
    Enhanced with Schopenhauer's philosophy - emphasizing understanding WHY
    relationships exist, not just WHAT they are, enabling independent recreation
    of the architectural decisions.
    """
    return f"""
Based on the following abstractions and their context from project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions with first-principles analysis and DYNAMICALLY IDENTIFIED technologies):
{context}

{language_instruction}**PHILOSOPHICAL FOUNDATION - ARCHITECTURAL THINKING:**
Following Schopenhauer's emphasis on independent thought, analyze these relationships not as mere connections, but as **architectural decisions** that someone made for specific reasons. Understand the **WHY** behind each relationship - what problems do these connections solve? What alternatives were rejected? How do these relationships enable the system's emergent properties?

**ENHANCED RELATIONSHIP ANALYSIS:**
Your task is to create a **LOSSLESS ARCHITECTURAL MAP** that enables someone to independently understand and recreate the system's design decisions. Each relationship must be analyzed through multiple lenses:

1. **Causal Understanding**: Why does this relationship exist? What would break if it didn't?
2. **Design Rationale**: Why THIS type of relationship over alternatives?
3. **Architectural Patterns**: What higher-level patterns do these relationships implement?
4. **Evolution Path**: How might this relationship have evolved from simpler designs?
5. **Trade-off Analysis**: What costs and benefits does this relationship create?

**PROJECT SUMMARY REQUIREMENTS:**
Provide a **first-principles architectural analysis** that explains:
- **Core Problem Domain**: What fundamental challenges does this system address?
- **Architectural Philosophy**: What design principles guide the overall structure?
- **Technology Rationale**: Why were these specific DYNAMICALLY IDENTIFIED technologies chosen?
- **Emergent Properties**: What capabilities emerge from the combination of abstractions?
- **Evolution Hypothesis**: How might this architecture have evolved from simpler versions?

**RELATIONSHIP ANALYSIS FRAMEWORK:**
For each relationship, provide comprehensive analysis:

**`from_abstraction`**: Source abstraction index and name
**`to_abstraction`**: Target abstraction index and name  
**`label`**: Multi-layered relationship description{lang_hint} including:

1. **Mechanism**: How the interaction works technically (using DYNAMICALLY IDENTIFIED technologies)
2. **Purpose**: Why this interaction is necessary for system function
3. **Pattern**: What architectural pattern this relationship implements
4. **Alternatives**: What other interaction patterns could have been used
5. **Trade-offs**: What this relationship optimizes for and what it sacrifices

**Example Enhanced Labels:**
- "Orchestrates via Command Pattern (using DYNAMICALLY IDENTIFIED Spring's @EventListener) - chosen over direct method calls to enable loose coupling and future extensibility, trading immediate consistency for system flexibility"
- "Persists state through Repository Pattern (via DYNAMICALLY IDENTIFIED Hibernate ORM) - abstracts data access to enable database independence and testability, accepting ORM complexity for development velocity"
- "Communicates via Publish-Subscribe (using DYNAMICALLY IDENTIFIED RabbitMQ) - enables temporal decoupling and horizontal scaling, trading immediate consistency for system resilience"

**RELATIONSHIP CATEGORIES (analyze WHY each category was chosen):**

**Structural Relationships** (Why these composition choices?):
- "Composes via Dependency Injection (DYNAMICALLY IDENTIFIED framework) - enables testability and configuration flexibility"
- "Contains as Aggregate Root (DYNAMICALLY IDENTIFIED DDD pattern) - maintains consistency boundaries and encapsulation"

**Behavioral Relationships** (Why these interaction patterns?):
- "Delegates through Strategy Pattern (DYNAMICALLY IDENTIFIED polymorphism) - enables algorithm variation without modification"
- "Coordinates via Mediator Pattern (DYNAMICALLY IDENTIFIED event bus) - reduces coupling between components"

**Data Flow Relationships** (Why these data movement patterns?):
- "Transforms via Pipeline Pattern (DYNAMICALLY IDENTIFIED stream processing) - enables composable data transformations"
- "Caches using Decorator Pattern (DYNAMICALLY IDENTIFIED Redis) - optimizes performance while maintaining transparency"

**Dependency Relationships** (Why these dependency directions?):
- "Depends on via Interface Segregation (DYNAMICALLY IDENTIFIED abstractions) - follows dependency inversion principle"
- "Configures through Builder Pattern (DYNAMICALLY IDENTIFIED fluent API) - enables complex object construction"

**CRITICAL REQUIREMENTS:**
1. **Complete Coverage**: Every abstraction (0 to {num_abstractions-1}) MUST appear in at least one relationship
2. **Architectural Coherence**: Relationships must form a coherent architectural story
3. **First-Principles Grounding**: Each relationship must be explainable from fundamental principles
4. **Recreation Enablement**: Descriptions must enable independent architectural recreation
5. **Alternative Awareness**: Acknowledge other possible relationship patterns and why they weren't chosen

**TABULATION APPROACH:**
Structure relationships to build architectural understanding incrementally:
- Start with foundational dependencies (configuration, core data structures)
- Build up through business logic layers
- Culminate in user-facing interfaces and external integrations
- Make architectural patterns explicit and cumulative

**RESPONSE FORMAT:**
Output ONLY a JSON5 object with NO explanatory text:

{{
  "summary": "**Core Problem Domain:** This project addresses [fundamental challenge] through [architectural approach]. **Architectural Philosophy:** The design follows [principles] as evidenced by [patterns]. **Technology Rationale:** [DYNAMICALLY IDENTIFIED technologies] were chosen because [reasons], enabling [capabilities] while accepting [trade-offs]. **Emergent Properties:** The combination of abstractions creates [system-level behaviors] that wouldn't exist in isolation. **Evolution Hypothesis:** This architecture likely evolved from [simpler approach] by adding [complexity] to solve [scaling/feature challenges].{lang_hint}",
  "relationships": [
    {{
      "from_abstraction": "0 # AbstractionName1",
      "to_abstraction": "1 # AbstractionName2", 
      "label": "[Mechanism] via [Pattern] (using DYNAMICALLY IDENTIFIED [technology]) - [Purpose and rationale], chosen over [alternatives] to optimize for [benefits] while accepting [costs]{lang_hint}"
    }}
    // ... comprehensive relationship mapping with architectural reasoning
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
    Enhanced prompt for completing relationships using first-principles thinking.
    Focuses on understanding WHY abstractions should be connected based on
    architectural necessity rather than superficial pattern matching.
    """
    return f"""
{language_instruction}**ARCHITECTURAL COMPLETION ANALYSIS:**
Following Schopenhauer's principle of thinking from first principles, analyze these disconnected abstractions not just to create connections, but to understand **WHY** they must be connected for the system to function coherently.

**PROJECT CONTEXT:** {project_name}

**PHILOSOPHICAL APPROACH:**
Each abstraction exists for a reason and serves a purpose in the overall system. Disconnected abstractions suggest either:
1. **Missing architectural relationships** that are necessary for system function
2. **Implicit dependencies** that should be made explicit for clarity
3. **Evolutionary artifacts** where relationships existed but aren't documented

**FIRST-PRINCIPLES CONNECTION ANALYSIS:**
For each disconnected abstraction, think through:

1. **Functional Necessity**: What does this abstraction need to accomplish its purpose?
2. **Resource Dependencies**: What resources (data, services, configuration) does it require?
3. **Lifecycle Coordination**: How does its lifecycle relate to other system components?
4. **Information Flow**: What information must flow to/from this abstraction?
5. **Architectural Patterns**: What patterns would naturally connect this to other abstractions?

**Disconnected abstractions requiring analysis:**
{disconnected_abstractions}

**Context from all abstractions (with DYNAMICALLY IDENTIFIED technologies):**
{abstraction_listing}

**Existing relationships for architectural context:**
{existing_relationships}

**ENHANCED CONNECTION STRATEGY:**
Create relationships that reflect **architectural necessity** rather than convenience:

**Structural Necessities** (Why must these be composed together?):
- "Contains as Essential Component (via DYNAMICALLY IDENTIFIED composition) - required for [abstraction] to fulfill its core responsibility of [purpose]"
- "Aggregates for Consistency Boundary (using DYNAMICALLY IDENTIFIED DDD pattern) - maintains [invariant] across [related concepts]"

**Behavioral Dependencies** (Why must these interact?):
- "Orchestrates for Business Process (via DYNAMICALLY IDENTIFIED workflow engine) - implements [business rule] requiring coordination between [capabilities]"
- "Delegates for Separation of Concerns (using DYNAMICALLY IDENTIFIED strategy pattern) - isolates [responsibility] from [implementation details]"

**Information Dependencies** (Why must data flow between these?):
- "Provides Context for Decision Making (via DYNAMICALLY IDENTIFIED parameter passing) - [abstraction] requires [information type] to perform [decision/calculation]"
- "Receives Events for State Synchronization (using DYNAMICALLY IDENTIFIED event bus) - maintains consistency of [shared concept] across [boundaries]"

**Lifecycle Dependencies** (Why must these be coordinated?):
- "Manages Lifecycle of Dependent Resource (via DYNAMICALLY IDENTIFIED factory pattern) - ensures [resource] availability for [abstraction's] operation"
- "Coordinates Shutdown Sequence (using DYNAMICALLY IDENTIFIED observer pattern) - prevents [failure mode] during system termination"

**ARCHITECTURAL VALIDATION:**
Each proposed relationship must satisfy:
1. **Necessity Test**: Is this connection required for system function?
2. **Simplicity Test**: Is this the simplest way to achieve the required connection?
3. **Consistency Test**: Does this align with existing architectural patterns?
4. **Evolution Test**: How would this connection naturally emerge during development?

**RESPONSE FORMAT:**
Provide ONLY a parseable JSON array with architectural reasoning:

[
  {{
    "from_abstraction": "5 # DisconnectedAbstraction (DYNAMICALLY IDENTIFIED tech context)",
    "to_abstraction": "2 # ConnectedAbstraction (DYNAMICALLY IDENTIFIED tech context)",
    "label": "[Connection Type] for [Architectural Purpose] (via DYNAMICALLY IDENTIFIED [mechanism]) - necessary because [abstraction] requires [specific capability/resource] to [accomplish its responsibility], chosen over [alternatives] to maintain [architectural principle]{lang_hint}"
  }}
  // Include architecturally necessary relationships for ALL disconnected abstractions
]"""


def get_order_chapters_prompt(
    project_name,
    abstraction_listing,
    context,
    list_lang_note=""
):
    """
    Enhanced chapter ordering using true tabulation approach inspired by
    Schopenhauer's incremental knowledge building and dynamic programming's
    optimal substructure principle.
    """
    return f"""
**ENHANCED TABULATION APPROACH FOR KNOWLEDGE CONSTRUCTION:**

Given the abstractions and relationships for `{project_name}`:

Abstractions (Index # Name){list_lang_note}:
{abstraction_listing}

Context (Architectural relationships and DYNAMICALLY IDENTIFIED technologies):
{context}

**PHILOSOPHICAL FOUNDATION - INCREMENTAL UNDERSTANDING:**
Following Schopenhauer's insight that true knowledge must be "worked out in one's own mind," structure this tutorial so each chapter builds understanding that enables **independent thinking** about the next concepts. Like dynamic programming's tabulation, each chapter should solve a "subproblem" of understanding that becomes a building block for more complex concepts.

**ENHANCED TABULATION PRINCIPLES:**

**1. Conceptual Dependency Resolution (True Prerequisites):**
- **Foundational Concepts First**: Abstract concepts that other abstractions depend on conceptually
- **Implementation Dependencies**: Concrete implementations that other code directly uses
- **Knowledge Prerequisites**: Understanding required to comprehend later abstractions
- **Cognitive Load Management**: Simpler concepts before complex ones

**2. Optimal Substructure for Learning:**
- Each chapter should provide **complete understanding** of its abstraction
- Later chapters should **build upon** rather than **repeat** earlier knowledge
- **Minimize cognitive overhead** by ensuring prerequisites are already internalized
- **Maximize learning efficiency** by ordering concepts for natural progression

**3. Independent Recreation Pathway:**
- Order chapters so a developer could **implement each abstraction** after reading its chapter
- Ensure **design rationale** is clear before showing implementation details
- Build **architectural intuition** progressively from simple to complex patterns
- Enable **first-principles thinking** about each design decision

**ENHANCED ORDERING CRITERIA:**

**Tier 1 - Foundational Abstractions (Build First):**
- **Core Data Models**: Fundamental entities that define the problem domain
- **Configuration Systems**: Settings and parameters that other components need
- **Utility Libraries**: Reusable functions that many other abstractions depend on
- **Basic Infrastructure**: Logging, error handling, basic connectivity

**Tier 2 - Business Logic Core (Build on Foundation):**
- **Domain Services**: Core business logic that operates on foundational data
- **Processing Engines**: Algorithms and computations that transform data
- **State Management**: Systems that maintain and coordinate application state
- **Internal APIs**: Interfaces between major system components

**Tier 3 - Integration Layer (Build on Core):**
- **External Adapters**: Connections to databases, external services, file systems
- **Event Systems**: Pub/sub, messaging, and asynchronous communication
- **Caching Layers**: Performance optimizations that wrap core functionality
- **Security Components**: Authentication, authorization, data protection

**Tier 4 - User Interface (Build on Integration):**
- **API Endpoints**: External interfaces that expose system functionality
- **User Interface Components**: Web pages, forms, user interaction elements
- **Orchestration Services**: High-level workflows that coordinate multiple components
- **Monitoring and Observability**: Systems that provide insight into operation

**COGNITIVE LOAD OPTIMIZATION:**
Within each tier, order by:
1. **Conceptual Simplicity**: Fewer moving parts and dependencies first
2. **Abstraction Level**: More abstract/general concepts before specific implementations
3. **Usage Frequency**: Widely-used abstractions before specialized ones
4. **Learning Curve**: Gentler learning curves before steep ones

**TABULATION VALIDATION:**
For each proposed ordering, verify:
- **Can implement**: Could someone implement this abstraction with only previous chapters' knowledge?
- **Understand rationale**: Are the design decisions comprehensible at this point?
- **See alternatives**: Can they evaluate other approaches with current knowledge?
- **Extend naturally**: Does this prepare them for the next level of complexity?

**ARCHITECTURAL NARRATIVE:**
The chapter order should tell a coherent story:
1. **"What problems are we solving?"** (Domain and foundational abstractions)
2. **"How do we solve them?"** (Core business logic and algorithms)
3. **"How do we connect to the world?"** (Integration and external interfaces)
4. **"How do users interact with our solution?"** (User interfaces and orchestration)

**RESPONSE FORMAT:**
Output ONLY a JSON5 array representing the optimal learning sequence:

[
  "2 # CoreDataModel (Foundational domain entities using DYNAMICALLY IDENTIFIED ORM)",
  "0 # ConfigurationService (System parameters using DYNAMICALLY IDENTIFIED config framework)",
  "1 # BusinessLogicEngine (Core algorithms building on data model)",
  "3 # ExternalAPIAdapter (Integration layer using established business logic)"
  // ... complete ordering optimized for incremental understanding and independent recreation
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
    Enhanced chapter writing prompt incorporating Schopenhauer's "thinking for oneself"
    philosophy and true tabulation approach for lossless knowledge transfer.
    """

    # Enhanced CEM with Schopenhauer's principles
    enhanced_cem_snippet = \
        "(Apply the Enhanced Core Explanation Mandate (CEM) with Schopenhauer's 'Thinking for Oneself' principle: For this element, provide comprehensive analysis (7-10 sentences minimum) covering: **Why** (fundamental problem and necessity), **How** (mechanisms using DYNAMICALLY IDENTIFIED technologies), **Design Rationale** (why THIS approach over alternatives, with specific alternative analysis), **First-Principles Foundation** (underlying CS/mathematical principles), **Trade-offs** (what's optimized vs. what's sacrificed), **Recreation Pathway** (how someone could independently arrive at this solution), **Architectural Context** (how this fits into broader system design). Every explanation must enable independent understanding and recreation, not mere pattern recognition.)"

    return f'''\
{language_instruction}**ENHANCED TUTORIAL CHAPTER - THINKING FOR ONESELF APPROACH**

Write a comprehensive tutorial chapter for `{project_name}` about: "{abstraction_name}" (Chapter {chapter_num})

**PHILOSOPHICAL FOUNDATION:**
Following Schopenhauer's "Thinking for Oneself," this chapter must enable readers to **independently understand and recreate** this abstraction, not merely recognize and copy patterns. Every explanation should build from first principles, explore design rationale, and provide the intellectual foundation for independent innovation.

**PRIMARY OBJECTIVES:**
1. **Independent Recreation**: Reader should be able to implement similar solutions from scratch
2. **Design Rationale Understanding**: Clear grasp of WHY decisions were made
3. **Alternative Awareness**: Knowledge of other approaches and their trade-offs  
4. **First-Principles Grounding**: Understanding of underlying CS/mathematical principles
5. **Architectural Context**: How this fits into broader system design philosophy

**ENHANCED CORE EXPLANATION MANDATE (CEM):**
For **EVERY** structural element (headings, lists, code blocks, diagrams, concepts), provide detailed analysis covering:

1. **Fundamental Necessity**: Why does this element exist? What breaks without it?
2. **Mechanism Deep-Dive**: How it works using DYNAMICALLY IDENTIFIED technologies
3. **Design Rationale**: Why THIS approach? What alternatives were considered?
4. **First-Principles Foundation**: What CS principles, algorithms, or math concepts apply?
5. **Trade-off Analysis**: What's optimized vs. what's sacrificed?
6. **Recreation Pathway**: How could someone independently develop this?
7. **Architectural Integration**: How does this serve the broader system design?

**ABSTRACTION CONTEXT:**{concept_details_note}
{enhanced_cem_snippet}
- **Name**: {abstraction_name}
- **Analysis**: {abstraction_description}

**TUTORIAL STRUCTURE:**{structure_note}
{full_chapter_listing}

**KNOWLEDGE FOUNDATION:**{prev_summary_note}
{previous_chapters_summary if previous_chapters_summary else "This is the foundational chapter - establish core principles."}
{enhanced_cem_snippet if previous_chapters_summary else ""}

**CODE CONTEXT:**{enhanced_cem_snippet}
{file_context_str if file_context_str else "No specific code provided - focus on general principles and theoretical foundation of DYNAMICALLY IDENTIFIED technologies."}

**ENHANCED CHAPTER STRUCTURE:**

**1. Chapter Introduction with Philosophical Context:**{enhanced_cem_snippet}
- Start with: `# Chapter {chapter_num}: {abstraction_name}`
- **Problem Genesis**: What fundamental challenge necessitated this abstraction?
- **Historical Context**: How might this solution have evolved?
- **Learning Objectives**: What will readers be able to independently create/understand?

**2. First-Principles Problem Analysis:**{enhanced_cem_snippet}
- **Core Problem Statement**: The fundamental challenge this abstraction addresses
- **Problem Decomposition**: Breaking down the challenge into manageable parts
- **Constraint Analysis**: Technical, business, and architectural constraints
- **Solution Space Exploration**: What approaches could theoretically work?
- **Convergence Rationale**: Why solutions tend toward this pattern

**3. Design Rationale Deep-Dive:**{enhanced_cem_snippet}
- **Alternative Approaches Analysis**: 
  - What other solutions exist for this problem?
  - Why weren't they chosen?
  - Under what circumstances might they be preferable?
- **Technology Selection Rationale**:
  - Why these specific DYNAMICALLY IDENTIFIED technologies?
  - What capabilities do they provide?
  - What limitations do they impose?
- **Architectural Pattern Justification**:
  - What design patterns are employed and why?
  - How do they solve specific sub-problems?
  - What are their inherent trade-offs?

**4. First-Principles Implementation Analysis:**{enhanced_cem_snippet}
- **Conceptual Foundation**:
  - What CS principles underpin this solution?
  - What mathematical or algorithmic concepts apply?
  - How do these principles manifest in the implementation?
- **Mechanism Walkthrough**:
  - Step-by-step operation from first principles
  - How DYNAMICALLY IDENTIFIED technologies enable each step
  - What invariants and assumptions are maintained?
- **Complexity Analysis**:
  - Time and space complexity characteristics
  - Scalability implications and bottlenecks
  - Performance trade-offs and optimization opportunities

**5. Independent Recreation Guide:**{enhanced_cem_snippet}
- **Knowledge Prerequisites**: What must someone understand first?
- **Incremental Development Path**: How to build this solution step-by-step
- **Key Insights**: Critical realizations that make the solution work
- **Common Pitfalls**: Where independent developers typically struggle
- **Validation Strategies**: How to verify the solution works correctly

**6. Code Analysis with Design Rationale:**{enhanced_cem_snippet}
- **Complete Code Examples**: Full, working implementations
- **Line-by-Line Rationale**: Why each significant line exists
- **Pattern Implementation**: How abstract patterns become concrete code
- **DYNAMICALLY IDENTIFIED Technology Usage**: Specific framework/library features and why they're used
- **Alternative Implementation Approaches**: How the same logic could be implemented differently

**7. Architectural Integration Analysis:**{enhanced_cem_snippet}
- **System Role**: How this abstraction serves the broader architecture
- **Interaction Patterns**: How it communicates with other abstractions (link to other chapters{link_lang_note})
- **Dependency Management**: What it depends on and what depends on it
- **Evolution Considerations**: How this abstraction might change over time
- **Scaling Implications**: How it affects system scalability

**8. Advanced Topics and Extensions:**{enhanced_cem_snippet}
- **Performance Optimization**: Advanced techniques for improving efficiency
- **Error Handling and Resilience**: How failures are managed and recovered
- **Configuration and Customization**: How behavior can be modified
- **Testing and Validation**: How to verify correctness (without focusing on test code)
- **Monitoring and Observability**: How to understand runtime behavior

**9. Alternative Implementations and Trade-offs:**{enhanced_cem_snippet}
- **Comparative Analysis**: How other teams/projects solve similar problems
- **Technology Alternatives**: Different tech stacks for the same solution
- **Architectural Variations**: Different patterns for similar outcomes
- **Context-Dependent Choices**: When to choose different approaches
- **Evolution Paths**: How this solution might evolve

**10. Synthesis and Forward Connections:**{enhanced_cem_snippet}
- **Key Insights Summary**: Most important learnings for independent thinking
- **Design Principles Demonstrated**: What general principles this example illustrates
- **Preparation for Next Concepts**: How this knowledge enables understanding of subsequent chapters
- **Independent Innovation Opportunities**: Where readers might improve or extend this solution

**ENHANCED WRITING REQUIREMENTS:**

**Thinking for Oneself Integration:**
- **Question Everything**: Why does each element exist? What alternatives were possible?
- **Build from Fundamentals**: Start with basic principles, build complexity incrementally
- **Explore Rationale**: Don't just show WHAT, explain WHY and WHY NOT alternatives
- **Enable Innovation**: Provide foundation for readers to develop their own solutions

**Tabulation Approach:**
- **Incremental Complexity**: Each concept builds on previous ones
- **Complete Understanding**: Each section provides full understanding of its scope
- **Minimal Forward References**: Avoid concepts not yet explained
- **Optimal Learning Sequence**: Order content for maximum comprehension

**Technical Depth Requirements:**
- **Senior Developer Focus**: Assume high technical competence{tone_note}
- **Implementation-Level Detail**: Sufficient depth for actual recreation
- **Performance Awareness**: Understand efficiency and scalability implications
- **Production Readiness**: Consider real-world deployment challenges

**Quality Assurance:**
- **Lossless Information Transfer**: No critical details omitted
- **Independent Verification**: Readers can validate their understanding
- **Alternative Awareness**: Multiple approaches considered
- **Architectural Coherence**: Fits logically into broader system design

{code_comment_note} {mermaid_lang_note} {instruction_lang_note}

**OUTPUT REQUIREMENTS:**
Provide ONLY the Markdown chapter content. No code fences or meta-commentary.
Focus on enabling independent thinking and recreation rather than pattern copying.
Every explanation must pass the test: "Could someone use this to independently develop a similar solution?"

Begin the chapter now:
'''
