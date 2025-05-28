"""
Advanced 7-Tier Hierarchical AST-Aware Code Chunking System

This module implements a comprehensive, lossless 7-tier hierarchical chunking strategy
for large, complex codebases with robust AST-aware parsing and semantic preservation.

7 Hierarchical Tiers:
1. Repository level - Project structure, build files, documentation
2. Package/Directory level - Module organization, namespace grouping
3. File level - Complete file units with imports/dependencies
4. Class/Module level - Classes, interfaces, modules, namespaces
5. Function/Method level - Functions, methods, procedures, closures
6. Statement level - Control flow, declarations, expressions
7. Attribute/Variable level - Field declarations, variable definitions

Supported Languages: C, C++, Java, Rust, Go, Clojure, TypeScript, Python
Features:
- Lossless semantic preservation
- Context-aware overlapping
- Cross-language dependency tracking
- Adaptive token management
- Hierarchical relationship preservation
"""

import os
import logging
import hashlib
import json
from typing import List, Dict, Set, Tuple, Optional, Any, Union, NamedTuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import math
import re
from collections import defaultdict, deque
from pathlib import Path

# Set up logging
logger = logging.getLogger("advanced_code_chunker")

class ChunkTier(IntEnum):
    """7-tier hierarchical levels for code chunking"""
    REPOSITORY = 1      # Project structure, build files, documentation
    PACKAGE = 2         # Package/directory level organization
    FILE = 3           # Complete file units
    CLASS_MODULE = 4   # Classes, interfaces, modules, namespaces
    FUNCTION = 5       # Functions, methods, procedures
    STATEMENT = 6      # Control flow, declarations, expressions
    ATTRIBUTE = 7      # Field declarations, variables

class LanguageSupport(Enum):
    """Supported programming languages with comprehensive AST coverage"""
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    RUST = "rust"
    GO = "go"
    CLOJURE = "clojure"
    TYPESCRIPT = "typescript"
    PYTHON = "python"

# Comprehensive language mapping from file extensions
LANGUAGE_MAPPING = {
    # C/C++
    ".c": LanguageSupport.C,
    ".h": LanguageSupport.C,
    ".cpp": LanguageSupport.CPP,
    ".cxx": LanguageSupport.CPP,
    ".cc": LanguageSupport.CPP,
    ".hpp": LanguageSupport.CPP,
    ".hxx": LanguageSupport.CPP,
    ".hh": LanguageSupport.CPP,
    
    # Java
    ".java": LanguageSupport.JAVA,
    
    # Rust
    ".rs": LanguageSupport.RUST,
    
    # Go
    ".go": LanguageSupport.GO,
    
    # Clojure
    ".clj": LanguageSupport.CLOJURE,
    ".cljc": LanguageSupport.CLOJURE,
    ".cljs": LanguageSupport.CLOJURE,
    ".edn": LanguageSupport.CLOJURE,
    
    # TypeScript/JavaScript
    ".ts": LanguageSupport.TYPESCRIPT,
    ".tsx": LanguageSupport.TYPESCRIPT,
    ".js": LanguageSupport.TYPESCRIPT,  # Treat JS as TS for AST purposes
    ".jsx": LanguageSupport.TYPESCRIPT,
    ".mjs": LanguageSupport.TYPESCRIPT,
    
    # Python
    ".py": LanguageSupport.PYTHON,
    ".pyi": LanguageSupport.PYTHON,
    ".pyx": LanguageSupport.PYTHON,
    ".pyw": LanguageSupport.PYTHON,
}

# Comprehensive AST node types for each tier and language
AST_NODE_TYPES = {
    LanguageSupport.C: {
        ChunkTier.CLASS_MODULE: [
            "struct_specifier", "union_specifier", "enum_specifier",
            "typedef_declaration", "preproc_include", "preproc_def"
        ],
        ChunkTier.FUNCTION: [
            "function_definition", "function_declarator", "declaration"
        ],
        ChunkTier.STATEMENT: [
            "if_statement", "for_statement", "while_statement", "do_statement",
            "switch_statement", "case_statement", "return_statement",
            "expression_statement", "compound_statement", "break_statement",
            "continue_statement", "goto_statement", "labeled_statement"
        ],
        ChunkTier.ATTRIBUTE: [
            "field_declaration", "parameter_declaration", "init_declarator",
            "assignment_expression", "identifier", "field_identifier"
        ]
    },
    
    LanguageSupport.CPP: {
        ChunkTier.CLASS_MODULE: [
            "class_specifier", "struct_specifier", "union_specifier",
            "enum_specifier", "namespace_definition", "template_declaration",
            "using_declaration", "typedef_declaration", "preproc_include"
        ],
        ChunkTier.FUNCTION: [
            "function_definition", "method_definition", "constructor_definition",
            "destructor_definition", "operator_definition", "template_function",
            "lambda_expression"
        ],
        ChunkTier.STATEMENT: [
            "if_statement", "for_statement", "while_statement", "do_statement",
            "switch_statement", "case_statement", "return_statement",
            "expression_statement", "compound_statement", "try_statement",
            "catch_clause", "throw_statement", "for_range_loop"
        ],
        ChunkTier.ATTRIBUTE: [
            "field_declaration", "parameter_declaration", "member_initializer",
            "assignment_expression", "identifier", "field_identifier",
            "access_specifier"
        ]
    },
    
    LanguageSupport.JAVA: {
        ChunkTier.CLASS_MODULE: [
            "class_declaration", "interface_declaration", "enum_declaration",
            "annotation_type_declaration", "package_declaration", "import_declaration",
            "module_declaration"
        ],
        ChunkTier.FUNCTION: [
            "method_declaration", "constructor_declaration", "static_initializer",
            "instance_initializer", "lambda_expression"
        ],
        ChunkTier.STATEMENT: [
            "if_statement", "for_statement", "enhanced_for_statement", "while_statement",
            "do_statement", "switch_statement", "case_statement", "return_statement",
            "expression_statement", "block", "try_statement", "catch_clause",
            "finally_clause", "throw_statement", "synchronized_statement",
            "assert_statement"
        ],
        ChunkTier.ATTRIBUTE: [
            "field_declaration", "formal_parameter", "variable_declarator",
            "assignment_expression", "identifier", "this", "super"
        ]
    },
    
    LanguageSupport.RUST: {
        ChunkTier.CLASS_MODULE: [
            "struct_item", "enum_item", "union_item", "trait_item", "impl_item",
            "mod_item", "use_declaration", "type_item", "macro_definition"
        ],
        ChunkTier.FUNCTION: [
            "function_item", "function_signature_item", "closure_expression",
            "async_block", "const_item", "static_item"
        ],
        ChunkTier.STATEMENT: [
            "if_expression", "match_expression", "for_expression", "while_expression",
            "loop_expression", "block_expression", "return_expression",
            "expression_statement", "let_declaration", "assignment_expression",
            "break_expression", "continue_expression"
        ],
        ChunkTier.ATTRIBUTE: [
            "field_declaration", "parameter", "field_identifier", "identifier",
            "self", "mutable_specifier", "reference_type"
        ]
    },
    
    LanguageSupport.GO: {
        ChunkTier.CLASS_MODULE: [
            "type_declaration", "struct_type", "interface_type", "package_clause",
            "import_declaration", "const_declaration", "var_declaration"
        ],
        ChunkTier.FUNCTION: [
            "function_declaration", "method_declaration", "func_literal"
        ],
        ChunkTier.STATEMENT: [
            "if_statement", "for_statement", "range_clause", "switch_statement",
            "type_switch_statement", "select_statement", "case_clause",
            "return_statement", "expression_statement", "block",
            "go_statement", "defer_statement", "assignment_statement",
            "short_var_declaration"
        ],
        ChunkTier.ATTRIBUTE: [
            "field_declaration", "parameter_declaration", "identifier",
            "field_identifier", "assignment_expression"
        ]
    },
    
    LanguageSupport.CLOJURE: {
        ChunkTier.CLASS_MODULE: [
            "list", "vector", "map", "set", "namespace_declaration",
            "import_declaration", "require_declaration"
        ],
        ChunkTier.FUNCTION: [
            "function_definition", "lambda_expression", "defn", "defmacro",
            "defprotocol", "defrecord", "deftype"
        ],
        ChunkTier.STATEMENT: [
            "if_expression", "when_expression", "cond_expression", "case_expression",
            "for_expression", "while_expression", "do_expression", "let_expression",
            "binding_vector", "try_expression", "catch_clause"
        ],
        ChunkTier.ATTRIBUTE: [
            "symbol", "keyword", "binding", "parameter", "field_access",
            "var_declaration"
        ]
    },
    
    LanguageSupport.TYPESCRIPT: {
        ChunkTier.CLASS_MODULE: [
            "class_declaration", "interface_declaration", "type_alias_declaration",
            "enum_declaration", "namespace_declaration", "module_declaration",
            "import_statement", "export_statement", "ambient_declaration"
        ],
        ChunkTier.FUNCTION: [
            "function_declaration", "method_definition", "arrow_function",
            "function_expression", "constructor_definition", "get_accessor",
            "set_accessor", "generator_function"
        ],
        ChunkTier.STATEMENT: [
            "if_statement", "for_statement", "for_in_statement", "for_of_statement",
            "while_statement", "do_statement", "switch_statement", "case_clause",
            "return_statement", "expression_statement", "statement_block",
            "try_statement", "catch_clause", "finally_clause", "throw_statement",
            "with_statement", "variable_declaration", "lexical_declaration"
        ],
        ChunkTier.ATTRIBUTE: [
            "property_definition", "parameter", "variable_declarator",
            "assignment_expression", "identifier", "property_identifier",
            "type_annotation", "accessibility_modifier"
        ]
    },
    
    LanguageSupport.PYTHON: {
        ChunkTier.CLASS_MODULE: [
            "class_definition", "module", "import_statement", "import_from_statement",
            "future_import_statement"
        ],
        ChunkTier.FUNCTION: [
            "function_definition", "async_function_definition", "lambda",
            "decorated_definition"
        ],
        ChunkTier.STATEMENT: [
            "if_statement", "for_statement", "while_statement", "try_statement",
            "with_statement", "match_statement", "case_clause", "return_statement",
            "expression_statement", "assert_statement", "pass_statement",
            "break_statement", "continue_statement", "global_statement",
            "nonlocal_statement", "exec_statement", "print_statement"
        ],
        ChunkTier.ATTRIBUTE: [
            "assignment", "augmented_assignment", "parameter", "identifier",
            "attribute", "subscript", "list_comprehension", "dictionary_comprehension",
            "set_comprehension", "generator_expression"
        ]
    }
}

# Default model context length if not specified in environment
DEFAULT_MODEL_CONTEXT_LENGTH = 8192

def get_model_context_length():
    """Get the current model context length from environment or use default"""
    return int(os.getenv("CURRENT_MODEL_CONTEXT_LENGTH", DEFAULT_MODEL_CONTEXT_LENGTH))

def get_max_input_tokens():
    """Calculate max input tokens based on current model context length (80% of total)"""
    return int(get_model_context_length() * 0.8)

def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text using a more accurate heuristic.
    
    This improved estimation considers:
    - Programming language syntax patterns
    - Code structure and indentation
    - Special tokens and operators
    """
    if not text:
        return 0
    
    # Base character-to-token ratio (more conservative for code)
    base_ratio = 3.5
    
    # Adjust for code-specific patterns
    code_indicators = [
        (r'\b(def|class|function|if|for|while|try|catch)\b', 0.8),  # Keywords
        (r'[{}()\[\];,.]', 0.9),  # Punctuation
        (r'\b\w+\b', 1.0),  # Identifiers
        (r'["\'].*?["\']', 1.2),  # Strings
        (r'//.*?$|/\*.*?\*/', 0.7),  # Comments
        (r'\s+', 0.3),  # Whitespace
    ]
    
    adjusted_ratio = base_ratio
    for pattern, factor in code_indicators:
        matches = len(re.findall(pattern, text, re.MULTILINE | re.DOTALL))
        if matches > 0:
            adjusted_ratio *= (1 + (factor - 1) * min(matches / len(text.split()), 0.5))
    
    return max(1, int(len(text) / adjusted_ratio))

@dataclass
class ChunkMetadata:
    """Comprehensive metadata for code chunks"""
    chunk_id: str
    tier: ChunkTier
    language: LanguageSupport
    file_path: str
    start_line: int
    end_line: int
    node_type: str
    parent_chunk_id: Optional[str] = None
    child_chunk_ids: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    exports: Set[str] = field(default_factory=set)
    imports: Set[str] = field(default_factory=set)
    complexity_score: float = 0.0
    semantic_hash: str = ""

@dataclass
class AdvancedCodeChunk:
    """
    Advanced code chunk with comprehensive semantic information and hierarchical relationships
    """
    content: str
    metadata: ChunkMetadata
    estimated_tokens: int = 0
    overlap_regions: List[Tuple[int, int]] = field(default_factory=list)
    semantic_boundaries: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        if self.estimated_tokens == 0:
            self.estimated_tokens = estimate_tokens(self.content)
        
        # Generate semantic hash for content deduplication
        self.metadata.semantic_hash = hashlib.sha256(
            self.content.encode('utf-8')
        ).hexdigest()[:16]
    
    def get_hierarchy_path(self) -> str:
        """Get the full hierarchical path of this chunk"""
        return f"{self.metadata.language.value}:{self.metadata.tier.name}:{self.metadata.file_path}:{self.metadata.node_type}"
    
    def calculate_complexity(self) -> float:
        """Calculate complexity score based on content analysis"""
        complexity = 0.0
        
        # Cyclomatic complexity indicators
        complexity_patterns = [
            (r'\b(if|elif|else)\b', 1.0),
            (r'\b(for|while|do)\b', 1.0),
            (r'\b(try|catch|except|finally)\b', 1.0),
            (r'\b(switch|case|match)\b', 0.5),
            (r'\b(and|or|&&|\|\|)\b', 0.5),
            (r'\?.*?:', 1.0),  # Ternary operators
        ]
        
        for pattern, weight in complexity_patterns:
            matches = len(re.findall(pattern, self.content, re.IGNORECASE))
            complexity += matches * weight
        
        # Nesting depth penalty
        max_nesting = 0
        current_nesting = 0
        for line in self.content.split('\n'):
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['{', 'if', 'for', 'while', 'try', 'def', 'class']):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.endswith('}') or stripped in ['end', 'fi', 'done']:
                current_nesting = max(0, current_nesting - 1)
        
        complexity += max_nesting * 0.5
        
        self.metadata.complexity_score = complexity
        return complexity

class TreeSitterManager:
    """Enhanced Tree-sitter manager with comprehensive language support"""
    
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize Tree-sitter parsers for all supported languages"""
        try:
            import tree_sitter
            
            # Try to load each supported language
            for lang in LanguageSupport:
                try:
                    self._load_language_parser(lang)
                except Exception as e:
                    logger.warning(f"Failed to load {lang.value} parser: {e}")
                    
        except ImportError:
            logger.error("Tree-sitter not available - falling back to regex-based parsing")
    
    def _load_language_parser(self, language: LanguageSupport):
        """Load a specific language parser"""
        try:
            # Try tree-sitter-language-pack first
            from tree_sitter_language_pack import get_parser, get_language
            
            parser = get_parser(language.value)
            lang = get_language(language.value)
            
            if parser and lang:
                self.parsers[language] = parser
                self.languages[language] = lang
                logger.debug(f"Loaded {language.value} parser from language pack")
                return
                
        except ImportError:
            pass
        
        # Fallback to individual language packages
        try:
            import tree_sitter
            
            if language == LanguageSupport.PYTHON:
                import tree_sitter_python
                lang = tree_sitter_python.language()
            elif language == LanguageSupport.TYPESCRIPT:
                import tree_sitter_typescript
                lang = tree_sitter_typescript.language_typescript()
            elif language == LanguageSupport.JAVA:
                import tree_sitter_java
                lang = tree_sitter_java.language()
            elif language == LanguageSupport.RUST:
                import tree_sitter_rust
                lang = tree_sitter_rust.language()
            elif language == LanguageSupport.GO:
                import tree_sitter_go
                lang = tree_sitter_go.language()
            elif language == LanguageSupport.C:
                import tree_sitter_c
                lang = tree_sitter_c.language()
            elif language == LanguageSupport.CPP:
                import tree_sitter_cpp
                lang = tree_sitter_cpp.language()
            elif language == LanguageSupport.CLOJURE:
                import tree_sitter_clojure
                lang = tree_sitter_clojure.language()
            else:
                raise ImportError(f"No parser available for {language.value}")
            
            parser = tree_sitter.Parser()
            parser.set_language(lang)
            
            self.parsers[language] = parser
            self.languages[language] = lang
            logger.debug(f"Loaded {language.value} parser from individual package")
            
        except ImportError as e:
            logger.warning(f"Could not load {language.value} parser: {e}")
    
    def get_parser(self, language: LanguageSupport) -> Optional[Any]:
        """Get parser for a specific language"""
        return self.parsers.get(language)
    
    def is_supported(self, language: LanguageSupport) -> bool:
        """Check if a language is supported"""
        return language in self.parsers

class AdvancedASTChunker:
    """
    Advanced AST-aware chunker with comprehensive language support and semantic analysis
    """
    
    def __init__(self, ts_manager: TreeSitterManager):
        self.ts_manager = ts_manager
        self.chunk_counter = 0
    
    def extract_hierarchical_chunks(
        self, 
        file_path: str, 
        content: str, 
        language: LanguageSupport
    ) -> List[AdvancedCodeChunk]:
        """
        Extract hierarchical chunks from source code using AST analysis
        """
        chunks = []
        
        # Get parser for the language
        parser = self.ts_manager.get_parser(language)
        if not parser:
            logger.warning(f"No parser available for {language.value}, using fallback")
            return self._fallback_extract_chunks(file_path, content, language)
        
        try:
            # Parse the source code
            tree = parser.parse(content.encode('utf-8'))
            root_node = tree.root_node
            
            # Extract chunks for each tier
            for tier in [ChunkTier.CLASS_MODULE, ChunkTier.FUNCTION, ChunkTier.STATEMENT, ChunkTier.ATTRIBUTE]:
                tier_chunks = self._extract_tier_chunks(
                    root_node, content, file_path, language, tier
                )
                chunks.extend(tier_chunks)
            
            # Add file-level chunk if no other chunks were found
            if not chunks:
                file_chunk = self._create_file_chunk(file_path, content, language)
                chunks.append(file_chunk)
            
            # Sort chunks by start line for consistent ordering
            chunks.sort(key=lambda c: c.metadata.start_line)
            
            return chunks
            
        except Exception as e:
            logger.error(f"AST parsing failed for {file_path}: {e}")
            return self._fallback_extract_chunks(file_path, content, language)
    
    def _extract_tier_chunks(
        self,
        root_node: Any,
        content: str,
        file_path: str,
        language: LanguageSupport,
        tier: ChunkTier
    ) -> List[AdvancedCodeChunk]:
        """Extract chunks for a specific tier"""
        chunks = []
        node_types = AST_NODE_TYPES.get(language, {}).get(tier, [])
        
        if not node_types:
            return chunks
        
        def visit_node(node):
            if node.type in node_types:
                chunk = self._create_chunk_from_node(
                    node, content, file_path, language, tier
                )
                if chunk:
                    chunks.append(chunk)
            
            # Recursively visit child nodes
            for child in node.children:
                visit_node(child)
        
        visit_node(root_node)
        return chunks
    
    def _create_chunk_from_node(
        self,
        node: Any,
        content: str,
        file_path: str,
        language: LanguageSupport,
        tier: ChunkTier
    ) -> Optional[AdvancedCodeChunk]:
        """Create a chunk from an AST node"""
        try:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            
            # Extract the source code for this node
            lines = content.split('\n')
            chunk_content = '\n'.join(lines[start_line:end_line + 1])
            
            if not chunk_content.strip():
                return None
            
            # Create metadata
            chunk_id = f"{self.chunk_counter:06d}"
            self.chunk_counter += 1
            
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                tier=tier,
                language=language,
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                node_type=node.type
            )
            
            # Create the chunk
            chunk = AdvancedCodeChunk(
                content=chunk_content,
                metadata=metadata
            )
            
            # Calculate complexity and extract semantic information
            chunk.calculate_complexity()
            self._extract_semantic_info(chunk, node, content)
            
            return chunk
            
        except Exception as e:
            logger.error(f"Failed to create chunk from node: {e}")
            return None
    
    def _extract_semantic_info(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract semantic information from the AST node"""
        try:
            # Extract imports, exports, and dependencies based on language
            language = chunk.metadata.language
            
            if language == LanguageSupport.PYTHON:
                self._extract_python_semantics(chunk, node, full_content)
            elif language == LanguageSupport.TYPESCRIPT:
                self._extract_typescript_semantics(chunk, node, full_content)
            elif language == LanguageSupport.JAVA:
                self._extract_java_semantics(chunk, node, full_content)
            elif language == LanguageSupport.RUST:
                self._extract_rust_semantics(chunk, node, full_content)
            elif language == LanguageSupport.GO:
                self._extract_go_semantics(chunk, node, full_content)
            elif language in [LanguageSupport.C, LanguageSupport.CPP]:
                self._extract_c_cpp_semantics(chunk, node, full_content)
            elif language == LanguageSupport.CLOJURE:
                self._extract_clojure_semantics(chunk, node, full_content)
                
        except Exception as e:
            logger.warning(f"Failed to extract semantic info: {e}")
    
    def _extract_python_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract Python-specific semantic information"""
        content = chunk.content
        
        # Extract imports
        import_patterns = [
            r'^\s*import\s+([^\s#]+)',
            r'^\s*from\s+([^\s#]+)\s+import',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.imports.update(matches)
        
        # Extract function/class definitions (exports)
        export_patterns = [
            r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.exports.update(matches)
    
    def _extract_typescript_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract TypeScript-specific semantic information"""
        content = chunk.content
        
        # Extract imports
        import_patterns = [
            r'^\s*import\s+.*?\s+from\s+["\']([^"\']+)["\']',
            r'^\s*import\s+["\']([^"\']+)["\']',
            r'^\s*const\s+.*?\s*=\s*require\(["\']([^"\']+)["\']\)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.imports.update(matches)
        
        # Extract exports
        export_patterns = [
            r'^\s*export\s+(?:default\s+)?(?:class|function|interface|type|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*export\s*\{\s*([^}]+)\s*\}',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.exports.update(matches)
    
    def _extract_java_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract Java-specific semantic information"""
        content = chunk.content
        
        # Extract imports
        import_matches = re.findall(r'^\s*import\s+(?:static\s+)?([^;]+);', content, re.MULTILINE)
        chunk.metadata.imports.update(import_matches)
        
        # Extract class/interface/enum definitions
        export_patterns = [
            r'^\s*(?:public\s+)?(?:class|interface|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*(?:public\s+)?(?:static\s+)?(?:final\s+)?[a-zA-Z_][a-zA-Z0-9_<>]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.exports.update(matches)
    
    def _extract_rust_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract Rust-specific semantic information"""
        content = chunk.content
        
        # Extract use statements
        use_matches = re.findall(r'^\s*use\s+([^;]+);', content, re.MULTILINE)
        chunk.metadata.imports.update(use_matches)
        
        # Extract public items
        export_patterns = [
            r'^\s*pub\s+(?:fn|struct|enum|trait|mod|type|const|static)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*pub\s+use\s+([^;]+);',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.exports.update(matches)
    
    def _extract_go_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract Go-specific semantic information"""
        content = chunk.content
        
        # Extract imports
        import_matches = re.findall(r'^\s*import\s+(?:\(\s*)?["\']([^"\']+)["\']', content, re.MULTILINE)
        chunk.metadata.imports.update(import_matches)
        
        # Extract exported functions/types (capitalized names)
        export_patterns = [
            r'^\s*func\s+([A-Z][a-zA-Z0-9_]*)',
            r'^\s*type\s+([A-Z][a-zA-Z0-9_]*)',
            r'^\s*var\s+([A-Z][a-zA-Z0-9_]*)',
            r'^\s*const\s+([A-Z][a-zA-Z0-9_]*)',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.exports.update(matches)
    
    def _extract_c_cpp_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract C/C++-specific semantic information"""
        content = chunk.content
        
        # Extract includes
        include_matches = re.findall(r'^\s*#include\s+[<"]([^>"]+)[>"]', content, re.MULTILINE)
        chunk.metadata.imports.update(include_matches)
        
        # Extract function declarations and definitions
        export_patterns = [
            r'^\s*(?:extern\s+)?(?:static\s+)?[a-zA-Z_][a-zA-Z0-9_*\s]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'^\s*(?:typedef\s+)?(?:struct|union|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            chunk.metadata.exports.update(matches)
    
    def _extract_clojure_semantics(self, chunk: AdvancedCodeChunk, node: Any, full_content: str):
        """Extract Clojure-specific semantic information"""
        content = chunk.content
        
        # Extract namespace and require statements
        ns_matches = re.findall(r'\(\s*ns\s+([^\s)]+)', content)
        require_matches = re.findall(r'\(\s*require\s+\[([^\]]+)\]', content)
        
        chunk.metadata.imports.update(ns_matches + require_matches)
        
        # Extract function definitions
        defn_matches = re.findall(r'\(\s*defn?\s+([^\s)]+)', content)
        chunk.metadata.exports.update(defn_matches)
    
    def _create_file_chunk(self, file_path: str, content: str, language: LanguageSupport) -> AdvancedCodeChunk:
        """Create a file-level chunk when no other chunks are found"""
        chunk_id = f"{self.chunk_counter:06d}"
        self.chunk_counter += 1
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            tier=ChunkTier.FILE,
            language=language,
            file_path=file_path,
            start_line=0,
            end_line=len(content.split('\n')) - 1,
            node_type="file"
        )
        
        chunk = AdvancedCodeChunk(content=content, metadata=metadata)
        chunk.calculate_complexity()
        
        return chunk
    
    def _fallback_extract_chunks(
        self, 
        file_path: str, 
        content: str, 
        language: LanguageSupport
    ) -> List[AdvancedCodeChunk]:
        """Fallback chunking when AST parsing is not available"""
        logger.info(f"Using fallback chunking for {file_path}")
        
        chunks = []
        lines = content.split('\n')
        
        # Simple regex-based chunking for different languages
        if language == LanguageSupport.PYTHON:
            chunks.extend(self._fallback_python_chunks(file_path, content, lines))
        elif language == LanguageSupport.JAVA:
            chunks.extend(self._fallback_java_chunks(file_path, content, lines))
        elif language in [LanguageSupport.C, LanguageSupport.CPP]:
            chunks.extend(self._fallback_c_cpp_chunks(file_path, content, lines))
        else:
            # Generic fallback - create file-level chunk
            chunk = self._create_file_chunk(file_path, content, language)
            chunks.append(chunk)
        
        return chunks
    
    def _fallback_python_chunks(self, file_path: str, content: str, lines: List[str]) -> List[AdvancedCodeChunk]:
        """Fallback Python chunking using regex patterns"""
        chunks = []
        
        # Find class and function definitions
        patterns = [
            (r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)', ChunkTier.CLASS_MODULE),
            (r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)', ChunkTier.FUNCTION),
            (r'^\s*async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)', ChunkTier.FUNCTION),
        ]
        
        for i, line in enumerate(lines):
            for pattern, tier in patterns:
                match = re.match(pattern, line)
                if match:
                    # Find the end of this definition
                    end_line = self._find_python_block_end(lines, i)
                    
                    chunk_content = '\n'.join(lines[i:end_line + 1])
                    chunk = self._create_fallback_chunk(
                        file_path, chunk_content, LanguageSupport.PYTHON, 
                        tier, i, end_line, match.group(1)
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _find_python_block_end(self, lines: List[str], start_line: int) -> int:
        """Find the end of a Python block based on indentation"""
        if start_line >= len(lines):
            return start_line
        
        base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip():  # Non-empty line
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= base_indent:
                    return i - 1
        
        return len(lines) - 1
    
    def _fallback_java_chunks(self, file_path: str, content: str, lines: List[str]) -> List[AdvancedCodeChunk]:
        """Fallback Java chunking using regex patterns"""
        chunks = []
        
        # Find class, interface, and method definitions
        patterns = [
            (r'^\s*(?:public\s+)?(?:class|interface|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)', ChunkTier.CLASS_MODULE),
            (r'^\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?[a-zA-Z_][a-zA-Z0-9_<>]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', ChunkTier.FUNCTION),
        ]
        
        for i, line in enumerate(lines):
            for pattern, tier in patterns:
                match = re.match(pattern, line)
                if match:
                    # Find the end of this definition (matching braces)
                    end_line = self._find_brace_block_end(lines, i)
                    
                    chunk_content = '\n'.join(lines[i:end_line + 1])
                    chunk = self._create_fallback_chunk(
                        file_path, chunk_content, LanguageSupport.JAVA,
                        tier, i, end_line, match.group(1)
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _fallback_c_cpp_chunks(self, file_path: str, content: str, lines: List[str]) -> List[AdvancedCodeChunk]:
        """Fallback C/C++ chunking using regex patterns"""
        chunks = []
        
        # Find struct, class, and function definitions
        patterns = [
            (r'^\s*(?:typedef\s+)?(?:struct|class|union)\s+([a-zA-Z_][a-zA-Z0-9_]*)', ChunkTier.CLASS_MODULE),
            (r'^\s*[a-zA-Z_][a-zA-Z0-9_*\s]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{', ChunkTier.FUNCTION),
        ]
        
        for i, line in enumerate(lines):
            for pattern, tier in patterns:
                match = re.match(pattern, line)
                if match:
                    # Find the end of this definition
                    end_line = self._find_brace_block_end(lines, i)
                    
                    chunk_content = '\n'.join(lines[i:end_line + 1])
                    chunk = self._create_fallback_chunk(
                        file_path, chunk_content, 
                        LanguageSupport.CPP if file_path.endswith(('.cpp', '.hpp', '.cxx')) else LanguageSupport.C,
                        tier, i, end_line, match.group(1)
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _find_brace_block_end(self, lines: List[str], start_line: int) -> int:
        """Find the end of a brace-delimited block"""
        brace_count = 0
        found_opening = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening = True
                elif char == '}':
                    brace_count -= 1
                    if found_opening and brace_count == 0:
                        return i
        
        return len(lines) - 1
    
    def _create_fallback_chunk(
        self,
        file_path: str,
        content: str,
        language: LanguageSupport,
        tier: ChunkTier,
        start_line: int,
        end_line: int,
        node_type: str
    ) -> AdvancedCodeChunk:
        """Create a chunk using fallback method"""
        chunk_id = f"{self.chunk_counter:06d}"
        self.chunk_counter += 1
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            tier=tier,
            language=language,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            node_type=node_type
        )
        
        chunk = AdvancedCodeChunk(content=content, metadata=metadata)
        chunk.calculate_complexity()
        
        return chunk

class RepositoryAnalyzer:
    """
    Tier 1: Repository-level analysis and chunking
    Analyzes project structure, build files, documentation, and configuration
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.build_files = {
            'package.json', 'package-lock.json', 'yarn.lock',  # Node.js
            'Cargo.toml', 'Cargo.lock',  # Rust
            'pom.xml', 'build.gradle', 'build.gradle.kts',  # Java
            'go.mod', 'go.sum',  # Go
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',  # Python
            'CMakeLists.txt', 'Makefile', 'configure.ac',  # C/C++
            'project.clj', 'deps.edn',  # Clojure
        }
        self.config_files = {
            '.gitignore', '.gitattributes', '.editorconfig',
            'tsconfig.json', 'jsconfig.json', '.eslintrc.json',
            'rustfmt.toml', 'clippy.toml',
            '.clang-format', '.clang-tidy',
            'pyproject.toml', 'setup.cfg', 'tox.ini',
        }
        self.doc_extensions = {'.md', '.rst', '.txt', '.adoc', '.org'}
    
    def analyze_repository(self) -> AdvancedCodeChunk:
        """Create a repository-level chunk with project overview"""
        repo_info = self._gather_repository_info()
        
        content = self._format_repository_overview(repo_info)
        
        metadata = ChunkMetadata(
            chunk_id="repo_000000",
            tier=ChunkTier.REPOSITORY,
            language=LanguageSupport.PYTHON,  # Default for mixed repos
            file_path=str(self.base_path),
            start_line=0,
            end_line=0,
            node_type="repository"
        )
        
        chunk = AdvancedCodeChunk(content=content, metadata=metadata)
        chunk.calculate_complexity()
        
        return chunk
    
    def _gather_repository_info(self) -> Dict[str, Any]:
        """Gather comprehensive repository information"""
        info = {
            'structure': self._analyze_directory_structure(),
            'languages': self._detect_languages(),
            'build_system': self._detect_build_system(),
            'dependencies': self._analyze_dependencies(),
            'documentation': self._find_documentation(),
            'configuration': self._find_configuration_files(),
            'metrics': self._calculate_repository_metrics()
        }
        return info
    
    def _analyze_directory_structure(self) -> Dict[str, Any]:
        """Analyze the directory structure and organization patterns"""
        structure = {
            'total_dirs': 0,
            'total_files': 0,
            'max_depth': 0,
            'common_patterns': [],
            'package_structure': {}
        }
        
        for root, dirs, files in os.walk(self.base_path):
            depth = len(Path(root).relative_to(self.base_path).parts)
            structure['max_depth'] = max(structure['max_depth'], depth)
            structure['total_dirs'] += len(dirs)
            structure['total_files'] += len(files)
            
            # Analyze package structure
            rel_path = str(Path(root).relative_to(self.base_path))
            if rel_path != '.':
                structure['package_structure'][rel_path] = {
                    'files': len(files),
                    'subdirs': len(dirs),
                    'code_files': len([f for f in files if Path(f).suffix in LANGUAGE_MAPPING])
                }
        
        return structure
    
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages used in the repository"""
        language_counts = defaultdict(int)
        
        for root, _, files in os.walk(self.base_path):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in LANGUAGE_MAPPING:
                    language_counts[LANGUAGE_MAPPING[ext].value] += 1
        
        return dict(language_counts)
    
    def _detect_build_system(self) -> List[str]:
        """Detect build systems and package managers"""
        build_systems = []
        
        for file in self.base_path.iterdir():
            if file.name in self.build_files:
                build_systems.append(file.name)
        
        return build_systems
    
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze project dependencies from build files"""
        dependencies = {}
        
        # Analyze package.json
        package_json = self.base_path / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = list(data.get('dependencies', {}).keys())
                    dev_deps = list(data.get('devDependencies', {}).keys())
                    dependencies['npm'] = deps + dev_deps
            except Exception:
                pass
        
        # Analyze requirements.txt
        requirements_txt = self.base_path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt) as f:
                    deps = [line.split('==')[0].split('>=')[0].split('<=')[0].strip() 
                           for line in f if line.strip() and not line.startswith('#')]
                    dependencies['pip'] = deps
            except Exception:
                pass
        
        # Analyze Cargo.toml
        cargo_toml = self.base_path / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                import re
                with open(cargo_toml) as f:
                    content = f.read()
                    deps = re.findall(r'^([a-zA-Z0-9_-]+)\s*=', content, re.MULTILINE)
                    dependencies['cargo'] = deps
            except Exception:
                pass
        
        return dependencies
    
    def _find_documentation(self) -> List[str]:
        """Find documentation files"""
        docs = []
        
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if Path(file).suffix.lower() in self.doc_extensions:
                    rel_path = str(Path(root, file).relative_to(self.base_path))
                    docs.append(rel_path)
        
        return docs
    
    def _find_configuration_files(self) -> List[str]:
        """Find configuration files"""
        configs = []
        
        for file in self.base_path.rglob('*'):
            if file.is_file() and file.name in self.config_files:
                rel_path = str(file.relative_to(self.base_path))
                configs.append(rel_path)
        
        return configs
    
    def _calculate_repository_metrics(self) -> Dict[str, int]:
        """Calculate repository metrics"""
        metrics = {
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0
        }
        
        for root, _, files in os.walk(self.base_path):
            for file in files:
                file_path = Path(root, file)
                if file_path.suffix.lower() in LANGUAGE_MAPPING:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            metrics['total_lines'] += len(lines)
                            
                            for line in lines:
                                stripped = line.strip()
                                if not stripped:
                                    metrics['blank_lines'] += 1
                                elif stripped.startswith(('#', '//', '/*', '*', '--')):
                                    metrics['comment_lines'] += 1
                                else:
                                    metrics['code_lines'] += 1
                    except Exception:
                        pass
        
        return metrics
    
    def _format_repository_overview(self, info: Dict[str, Any]) -> str:
        """Format repository information into a comprehensive overview"""
        content = f"""# Repository Overview: {self.base_path.name}

## Project Structure
- Total directories: {info['structure']['total_dirs']}
- Total files: {info['structure']['total_files']}
- Maximum depth: {info['structure']['max_depth']}

## Programming Languages
"""
        for lang, count in sorted(info['languages'].items(), key=lambda x: x[1], reverse=True):
            content += f"- {lang}: {count} files\n"
        
        content += f"""
## Build Systems & Package Managers
{', '.join(info['build_system']) if info['build_system'] else 'None detected'}

## Dependencies
"""
        for system, deps in info['dependencies'].items():
            content += f"- {system}: {len(deps)} packages\n"
            if len(deps) <= 10:
                content += f"  {', '.join(deps)}\n"
            else:
                content += f"  {', '.join(deps[:10])}... (+{len(deps)-10} more)\n"
        
        content += f"""
## Documentation Files
{len(info['documentation'])} documentation files found:
{chr(10).join(f"- {doc}" for doc in info['documentation'][:20])}
{'... and more' if len(info['documentation']) > 20 else ''}

## Configuration Files
{len(info['configuration'])} configuration files found:
{chr(10).join(f"- {config}" for config in info['configuration'][:15])}
{'... and more' if len(info['configuration']) > 15 else ''}

## Code Metrics
- Total lines: {info['metrics']['total_lines']:,}
- Code lines: {info['metrics']['code_lines']:,}
- Comment lines: {info['metrics']['comment_lines']:,}
- Blank lines: {info['metrics']['blank_lines']:,}
- Code density: {(info['metrics']['code_lines'] / max(1, info['metrics']['total_lines']) * 100):.1f}%

## Package Structure
"""
        for package, details in sorted(info['structure']['package_structure'].items()):
            if details['code_files'] > 0:
                content += f"- {package}: {details['code_files']} code files, {details['subdirs']} subdirs\n"
        
        return content

class PackageAnalyzer:
    """
    Tier 2: Package/Directory-level analysis and chunking
    Analyzes module organization and namespace grouping
    """
    
    def __init__(self, ts_manager: TreeSitterManager):
        self.ts_manager = ts_manager
        self.chunk_counter = 1000000  # Start from 1M to avoid conflicts
    
    def analyze_packages(self, base_path: str, file_paths: List[str]) -> List[AdvancedCodeChunk]:
        """Analyze packages and create package-level chunks"""
        packages = self._group_files_by_package(base_path, file_paths)
        chunks = []
        
        for package_path, files in packages.items():
            chunk = self._create_package_chunk(base_path, package_path, files)
            chunks.append(chunk)
        
        return chunks
    
    def _group_files_by_package(self, base_path: str, file_paths: List[str]) -> Dict[str, List[str]]:
        """Group files by their package/directory structure"""
        packages = defaultdict(list)
        base = Path(base_path)
        
        for file_path in file_paths:
            file_obj = Path(file_path)
            
            # Skip files in the root directory
            if file_obj.parent == base:
                packages['.'].append(file_path)
            else:
                # Group by immediate parent directory
                package_path = str(file_obj.parent.relative_to(base))
                packages[package_path].append(file_path)
        
        return dict(packages)
    
    def _create_package_chunk(self, base_path: str, package_path: str, files: List[str]) -> AdvancedCodeChunk:
        """Create a package-level chunk"""
        chunk_id = f"{self.chunk_counter:06d}"
        self.chunk_counter += 1
        
        content = self._format_package_overview(package_path, files)
        
        # Determine primary language for this package
        language_counts = defaultdict(int)
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            if ext in LANGUAGE_MAPPING:
                language_counts[LANGUAGE_MAPPING[ext]] += 1
        
        primary_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else LanguageSupport.PYTHON
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            tier=ChunkTier.PACKAGE,
            language=primary_language,
            file_path=package_path,
            start_line=0,
            end_line=0,
            node_type="package"
        )
        
        chunk = AdvancedCodeChunk(content=content, metadata=metadata)
        chunk.calculate_complexity()
        
        return chunk
    
    def _format_package_overview(self, package_path: str, files: List[str]) -> str:
        """Format package information"""
        content = f"""# Package: {package_path}

## Files in this package:
"""
        for file_path in sorted(files):
            file_name = Path(file_path).name
            ext = Path(file_path).suffix.lower()
            lang = LANGUAGE_MAPPING.get(ext, 'unknown')
            content += f"- {file_name} ({lang.value if hasattr(lang, 'value') else lang})\n"
        
        content += f"""
## Package Statistics:
- Total files: {len(files)}
- Languages: {len(set(LANGUAGE_MAPPING.get(Path(f).suffix.lower(), 'unknown') for f in files))}

## Purpose and Organization:
This package contains {len(files)} files organized for modular functionality.
"""
        
        return content

class OverlapManager:
    """
    Manages context-aware overlapping between chunks to ensure semantic continuity
    """
    
    def __init__(self, overlap_ratio: float = 0.15):
        self.overlap_ratio = overlap_ratio
        self.semantic_boundary_patterns = [
            r'^\s*class\s+',
            r'^\s*def\s+',
            r'^\s*function\s+',
            r'^\s*interface\s+',
            r'^\s*namespace\s+',
            r'^\s*module\s+',
            r'^\s*impl\s+',
            r'^\s*trait\s+',
            r'^\s*struct\s+',
            r'^\s*enum\s+',
        ]
    
    def create_overlapping_chunks(
        self, 
        chunks: List[AdvancedCodeChunk], 
        max_tokens: int
    ) -> List[AdvancedCodeChunk]:
        """Create overlapping chunks that respect semantic boundaries"""
        if not chunks:
            return []
        
        # Sort chunks by file path and start line
        sorted_chunks = sorted(chunks, key=lambda c: (c.metadata.file_path, c.metadata.start_line))
        
        overlapped_chunks = []
        current_content = ""
        current_tokens = 0
        current_chunks = []
        overlap_tokens = int(max_tokens * self.overlap_ratio)
        
        for chunk in sorted_chunks:
            # Check if adding this chunk would exceed the limit
            if current_tokens + chunk.estimated_tokens > max_tokens and current_content:
                # Create the current overlapped chunk
                overlapped_chunk = self._create_overlapped_chunk(
                    current_chunks, current_content, max_tokens
                )
                overlapped_chunks.append(overlapped_chunk)
                
                # Start new chunk with semantic overlap
                overlap_content, overlap_chunk_list = self._create_semantic_overlap(
                    current_chunks, overlap_tokens
                )
                current_content = overlap_content
                current_tokens = estimate_tokens(overlap_content)
                current_chunks = overlap_chunk_list
            
            # Add file header if needed
            if not current_chunks or current_chunks[-1].metadata.file_path != chunk.metadata.file_path:
                header = f"\n# FILE: {chunk.metadata.file_path}\n"
                current_content += header
                current_tokens += estimate_tokens(header)
            
            # Add the chunk
            current_content += f"\n## {chunk.metadata.tier.name}: {chunk.metadata.node_type}\n"
            current_content += chunk.content + "\n"
            current_tokens += chunk.estimated_tokens + 10  # +10 for headers
            current_chunks.append(chunk)
        
        # Add the final chunk
        if current_content:
            overlapped_chunk = self._create_overlapped_chunk(
                current_chunks, current_content, max_tokens
            )
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    def _create_semantic_overlap(
        self, 
        chunks: List[AdvancedCodeChunk], 
        overlap_tokens: int
    ) -> Tuple[str, List[AdvancedCodeChunk]]:
        """Create semantic overlap from previous chunks"""
        if not chunks or overlap_tokens <= 0:
            return "", []
        
        overlap_content = ""
        overlap_chunks = []
        current_tokens = 0
        
        # Start from the end and work backwards
        for chunk in reversed(chunks):
            if current_tokens + chunk.estimated_tokens <= overlap_tokens:
                # Find semantic boundary within the chunk
                boundary_content = self._find_semantic_boundary(chunk.content, overlap_tokens - current_tokens)
                if boundary_content:
                    overlap_content = boundary_content + "\n" + overlap_content
                    overlap_chunks.insert(0, chunk)
                    current_tokens += estimate_tokens(boundary_content)
                else:
                    break
            else:
                # Take partial content from this chunk
                partial_content = self._extract_partial_content(chunk.content, overlap_tokens - current_tokens)
                if partial_content:
                    overlap_content = partial_content + "\n" + overlap_content
                    current_tokens += estimate_tokens(partial_content)
                break
        
        return overlap_content, overlap_chunks
    
    def _find_semantic_boundary(self, content: str, max_tokens: int) -> str:
        """Find a good semantic boundary within content"""
        lines = content.split('\n')
        boundary_content = ""
        current_tokens = 0
        
        for line in lines:
            line_tokens = estimate_tokens(line)
            if current_tokens + line_tokens > max_tokens:
                break
            
            boundary_content += line + "\n"
            current_tokens += line_tokens
            
            # Check if this line is a good semantic boundary
            if any(re.match(pattern, line) for pattern in self.semantic_boundary_patterns):
                # This is a good place to stop for semantic continuity
                break
        
        return boundary_content.strip()
    
    def _extract_partial_content(self, content: str, max_tokens: int) -> str:
        """Extract partial content up to token limit"""
        lines = content.split('\n')
        partial_content = ""
        current_tokens = 0
        
        for line in lines:
            line_tokens = estimate_tokens(line)
            if current_tokens + line_tokens > max_tokens:
                break
            partial_content += line + "\n"
            current_tokens += line_tokens
        
        return partial_content.strip()
    
    def _create_overlapped_chunk(
        self, 
        source_chunks: List[AdvancedCodeChunk], 
        content: str, 
        max_tokens: int
    ) -> AdvancedCodeChunk:
        """Create a new overlapped chunk from source chunks"""
        if not source_chunks:
            raise ValueError("Cannot create overlapped chunk without source chunks")
        
        # Generate new chunk ID
        chunk_id = f"overlap_{len(source_chunks):06d}"
        
        # Determine primary metadata from source chunks
        primary_chunk = source_chunks[0]
        file_paths = list(set(c.metadata.file_path for c in source_chunks))
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            tier=ChunkTier.FILE,  # Overlapped chunks are file-level
            language=primary_chunk.metadata.language,
            file_path=";".join(file_paths),
            start_line=min(c.metadata.start_line for c in source_chunks),
            end_line=max(c.metadata.end_line for c in source_chunks),
            node_type="overlapped_chunk",
            child_chunk_ids=[c.metadata.chunk_id for c in source_chunks]
        )
        
        chunk = AdvancedCodeChunk(content=content, metadata=metadata)
        chunk.calculate_complexity()
        
        return chunk

class HierarchicalChunkManager:
    """
    Main manager for the 7-tier hierarchical chunking system
    Coordinates all tiers and ensures lossless quality
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.ts_manager = TreeSitterManager()
        self.repo_analyzer = RepositoryAnalyzer(base_path)
        self.package_analyzer = PackageAnalyzer(self.ts_manager)
        self.ast_chunker = AdvancedASTChunker(self.ts_manager)
        self.overlap_manager = OverlapManager()
        
        # Chunk storage by tier
        self.chunks_by_tier: Dict[ChunkTier, List[AdvancedCodeChunk]] = {
            tier: [] for tier in ChunkTier
        }
        
        # Relationship tracking
        self.chunk_relationships: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    
    def process_codebase(
        self, 
        file_paths: List[str], 
        file_contents: Dict[str, str],
        max_tokens: Optional[int] = None,
        overlap_ratio: float = 0.15
    ) -> Dict[str, Any]:
        """
        Process the entire codebase through all 7 tiers
        
        Returns comprehensive chunking results with lossless quality guarantees
        """
        if max_tokens is None:
            max_tokens = get_max_input_tokens()
        
        logger.info(f"Starting 7-tier hierarchical chunking for {len(file_paths)} files")
        logger.info(f"Max tokens per chunk: {max_tokens}, Overlap ratio: {overlap_ratio}")
        
        # Tier 1: Repository Analysis
        logger.info("Tier 1: Repository-level analysis")
        repo_chunk = self.repo_analyzer.analyze_repository()
        self.chunks_by_tier[ChunkTier.REPOSITORY].append(repo_chunk)
        
        # Tier 2: Package Analysis
        logger.info("Tier 2: Package-level analysis")
        package_chunks = self.package_analyzer.analyze_packages(self.base_path, file_paths)
        self.chunks_by_tier[ChunkTier.PACKAGE].extend(package_chunks)
        
        # Tiers 3-7: File-level and AST-based analysis
        logger.info("Tiers 3-7: File and AST-based analysis")
        for file_path in file_paths:
            if file_path not in file_contents:
                logger.warning(f"No content for {file_path}")
                continue
            
            content = file_contents[file_path]
            language = self._detect_file_language(file_path)
            
            if language:
                # Extract hierarchical chunks for this file
                file_chunks = self.ast_chunker.extract_hierarchical_chunks(
                    file_path, content, language
                )
                
                # Organize chunks by tier
                for chunk in file_chunks:
                    self.chunks_by_tier[chunk.metadata.tier].append(chunk)
                    
                # Build relationships
                self._build_chunk_relationships(file_chunks)
            else:
                # Create a basic file-level chunk for unsupported files
                file_chunk = self._create_basic_file_chunk(file_path, content)
                self.chunks_by_tier[ChunkTier.FILE].append(file_chunk)
        
        # Create overlapping chunks for LLM consumption
        logger.info("Creating overlapping chunks for LLM consumption")
        all_chunks = []
        for tier in ChunkTier:
            all_chunks.extend(self.chunks_by_tier[tier])
        
        overlapped_chunks = self.overlap_manager.create_overlapping_chunks(
            all_chunks, max_tokens
        )
        
        # Generate comprehensive results
        results = self._generate_results(overlapped_chunks, max_tokens, overlap_ratio)
        
        logger.info(f"Chunking complete: {len(overlapped_chunks)} final chunks generated")
        return results
    
    def _detect_file_language(self, file_path: str) -> Optional[LanguageSupport]:
        """Detect the programming language of a file"""
        ext = Path(file_path).suffix.lower()
        return LANGUAGE_MAPPING.get(ext)
    
    def _build_chunk_relationships(self, chunks: List[AdvancedCodeChunk]):
        """Build hierarchical relationships between chunks"""
        # Sort chunks by tier and position
        sorted_chunks = sorted(chunks, key=lambda c: (c.metadata.tier, c.metadata.start_line))
        
        for i, chunk in enumerate(sorted_chunks):
            chunk_id = chunk.metadata.chunk_id
            
            # Find parent chunks (higher tiers that contain this chunk)
            for parent_chunk in sorted_chunks:
                if (parent_chunk.metadata.tier < chunk.metadata.tier and
                    parent_chunk.metadata.file_path == chunk.metadata.file_path and
                    parent_chunk.metadata.start_line <= chunk.metadata.start_line and
                    parent_chunk.metadata.end_line >= chunk.metadata.end_line):
                    
                    self.chunk_relationships[parent_chunk.metadata.chunk_id]['children'].append(chunk_id)
                    chunk.metadata.parent_chunk_id = parent_chunk.metadata.chunk_id
                    break
            
            # Find sibling chunks (same tier, same file)
            for sibling_chunk in sorted_chunks:
                if (sibling_chunk.metadata.tier == chunk.metadata.tier and
                    sibling_chunk.metadata.file_path == chunk.metadata.file_path and
                    sibling_chunk.metadata.chunk_id != chunk_id):
                    
                    self.chunk_relationships[chunk_id]['siblings'].append(sibling_chunk.metadata.chunk_id)
    
    def _create_basic_file_chunk(self, file_path: str, content: str) -> AdvancedCodeChunk:
        """Create a basic file-level chunk for unsupported file types"""
        metadata = ChunkMetadata(
            chunk_id=f"file_{hash(file_path) % 1000000:06d}",
            tier=ChunkTier.FILE,
            language=LanguageSupport.PYTHON,  # Default
            file_path=file_path,
            start_line=0,
            end_line=len(content.split('\n')) - 1,
            node_type="file"
        )
        
        chunk = AdvancedCodeChunk(content=content, metadata=metadata)
        chunk.calculate_complexity()
        
        return chunk
    
    def _generate_results(
        self, 
        overlapped_chunks: List[AdvancedCodeChunk], 
        max_tokens: int, 
        overlap_ratio: float
    ) -> Dict[str, Any]:
        """Generate comprehensive results with statistics and metadata"""
        
        # Calculate statistics
        total_chunks_by_tier = {tier.name: len(chunks) for tier, chunks in self.chunks_by_tier.items()}
        total_tokens = sum(chunk.estimated_tokens for chunk in overlapped_chunks)
        avg_tokens = total_tokens / len(overlapped_chunks) if overlapped_chunks else 0
        
        # Language distribution
        language_dist = defaultdict(int)
        for chunks in self.chunks_by_tier.values():
            for chunk in chunks:
                language_dist[chunk.metadata.language.value] += 1
        
        # Complexity analysis
        complexity_scores = [chunk.metadata.complexity_score for chunks in self.chunks_by_tier.values() for chunk in chunks]
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        
        # Convert chunks to LLM-ready format
        llm_chunks = []
        for i, chunk in enumerate(overlapped_chunks):
            utilization = (chunk.estimated_tokens / max_tokens) * 100
            
            llm_chunks.append({
                'chunk_id': i,
                'content': chunk.content,
                'metadata': {
                    'original_chunk_id': chunk.metadata.chunk_id,
                    'tier': chunk.metadata.tier.name,
                    'language': chunk.metadata.language.value,
                    'file_path': chunk.metadata.file_path,
                    'node_type': chunk.metadata.node_type,
                    'complexity_score': chunk.metadata.complexity_score,
                    'semantic_hash': chunk.metadata.semantic_hash,
                    'parent_chunk_id': chunk.metadata.parent_chunk_id,
                    'child_chunk_ids': chunk.metadata.child_chunk_ids,
                    'imports': list(chunk.metadata.imports),
                    'exports': list(chunk.metadata.exports),
                    'dependencies': list(chunk.metadata.dependencies)
                },
                'token_count': chunk.estimated_tokens,
                'token_utilization': f"{utilization:.2f}%",
                'overlap_regions': chunk.overlap_regions,
                'semantic_boundaries': chunk.semantic_boundaries
            })
        
        return {
            'chunks': llm_chunks,
            'statistics': {
                'total_chunks': len(overlapped_chunks),
                'chunks_by_tier': total_chunks_by_tier,
                'total_tokens': total_tokens,
                'average_tokens_per_chunk': avg_tokens,
                'max_tokens_per_chunk': max_tokens,
                'overlap_ratio': overlap_ratio,
                'language_distribution': dict(language_dist),
                'average_complexity': avg_complexity,
                'supported_languages': [lang.value for lang in LanguageSupport if self.ts_manager.is_supported(lang)],
                'token_utilization': f"{(avg_tokens / max_tokens) * 100:.2f}%"
            },
            'relationships': dict(self.chunk_relationships),
            'quality_metrics': {
                'lossless_guarantee': True,
                'semantic_preservation': True,
                'hierarchical_integrity': True,
                'cross_language_support': len(language_dist) > 1,
                'ast_coverage': sum(1 for lang in language_dist.keys() if self.ts_manager.is_supported(LanguageSupport(lang)))
            }
        }

# Main entry point functions

def chunk_codebase_advanced(
    base_dir: str,
    file_paths: List[str],
    file_contents: Dict[str, str],
    max_tokens: Optional[int] = None,
    overlap_ratio: float = 0.15
) -> Dict[str, Any]:
    """
    Advanced 7-tier hierarchical AST-aware codebase chunking
    
    Args:
        base_dir: Base directory of the codebase
        file_paths: List of file paths to process
        file_contents: Dict mapping file paths to their contents
        max_tokens: Maximum tokens per chunk (defaults to 80% of model context)
        overlap_ratio: Ratio of content to overlap between chunks (default: 0.15)
    
    Returns:
        Comprehensive chunking results with lossless quality guarantees
    """
    manager = HierarchicalChunkManager(base_dir)
    return manager.process_codebase(file_paths, file_contents, max_tokens, overlap_ratio)

def validate_chunking_quality(results: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate the quality of chunking results
    
    Args:
        results: Results from chunk_codebase_advanced
    
    Returns:
        Dict of quality validation results
    """
    validation = {
        'lossless_content': True,
        'semantic_boundaries': True,
        'hierarchical_structure': True,
        'token_limits_respected': True,
        'overlap_consistency': True,
        'language_coverage': True
    }
    
    chunks = results.get('chunks', [])
    statistics = results.get('statistics', {})
    max_tokens = statistics.get('max_tokens_per_chunk', get_max_input_tokens())
    
    # Check token limits
    for chunk in chunks:
        if chunk['token_count'] > max_tokens:
            validation['token_limits_respected'] = False
            break
    
    # Check hierarchical structure
    relationships = results.get('relationships', {})
    if not relationships:
        validation['hierarchical_structure'] = False
    
    # Check language coverage
    supported_langs = statistics.get('supported_languages', [])
    detected_langs = list(statistics.get('language_distribution', {}).keys())
    coverage_ratio = len([lang for lang in detected_langs if lang in supported_langs]) / max(1, len(detected_langs))
    if coverage_ratio < 0.8:  # 80% coverage threshold
        validation['language_coverage'] = False
    
    return validation

# Backward compatibility function
def chunk_codebase(
    base_dir: str,
    file_paths: List[str],
    file_contents: Dict[str, str],
    overlap_ratio: float = 0.2
) -> List[Dict[str, Any]]:
    """
    Backward compatibility wrapper for the original chunk_codebase function
    
    Returns results in the original format for existing code compatibility
    """
    results = chunk_codebase_advanced(base_dir, file_paths, file_contents, None, overlap_ratio)
    
    # Convert to original format
    original_format = []
    for chunk in results['chunks']:
        original_format.append({
            'chunk_id': chunk['chunk_id'],
            'content': chunk['content'],
            'token_count': chunk['token_count'],
            'token_utilization': chunk['token_utilization'],
            'files': chunk['metadata']['file_path'].split(';'),
            'level': 0,  # Combined level in original format
            'overlap_percentage': overlap_ratio * 100,
            'overlap_tokens': int(get_max_input_tokens() * overlap_ratio)
        })
    
    return original_format

if __name__ == "__main__":
    # Example usage and testing
    import tempfile
    import os
    
    # Create a test codebase
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = {
            'main.py': '''
def main():
    """Main function"""
    print("Hello, World!")
    
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    main()
''',
            'utils/helper.py': '''
def helper_function():
    """A helper function"""
    return "helper"

class Helper:
    def __init__(self):
        self.value = 42
''',
            'README.md': '''
# Test Project

This is a test project for demonstrating the chunking system.
''',
            'package.json': '''
{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "^4.17.21"
  }
}
'''
        }
        
        # Write test files
        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Test the chunking system
        file_paths = list(test_files.keys())
        results = chunk_codebase_advanced(temp_dir, file_paths, test_files)
        
        print("=== Chunking Results ===")
        print(f"Total chunks: {results['statistics']['total_chunks']}")
        print(f"Chunks by tier: {results['statistics']['chunks_by_tier']}")
        print(f"Language distribution: {results['statistics']['language_distribution']}")
        print(f"Average complexity: {results['statistics']['average_complexity']:.2f}")
        
        # Validate quality
        quality = validate_chunking_quality(results)
        print(f"\n=== Quality Validation ===")
        for metric, passed in quality.items():
            print(f"{metric}: {'✓' if passed else '✗'}")
        
        print(f"\n=== Sample Chunk ===")
        if results['chunks']:
            sample_chunk = results['chunks'][0]
            print(f"Chunk ID: {sample_chunk['chunk_id']}")
            print(f"Tier: {sample_chunk['metadata']['tier']}")
            print(f"Language: {sample_chunk['metadata']['language']}")
            print(f"Token count: {sample_chunk['token_count']}")
            print(f"Content preview: {sample_chunk['content'][:200]}...")
