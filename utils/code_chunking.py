"""
Hierarchical AST-aware code chunking for large codebases.

This module implements a 5-level hierarchical, AST-aware, overlapped chunking strategy
for large codebases with dedicated support for various programming languages.

Levels:
1. Directory level - Project structure chunking
2. File level - Entire file as a chunk
3. Class/Module level - Classes, modules, namespaces
4. Function/Method level - Functions, methods, procedures
5. Statement level - Individual statements, expressions

It uses tree-sitter for parsing and preserves semantic structure in chunks.
"""

import os
import logging
from typing import List, Dict, Set, Tuple, Optional, Any, Union
import math
import re

# Set up logging
logger = logging.getLogger("code_chunker")

# Default model context length if not specified in environment
DEFAULT_MODEL_CONTEXT_LENGTH = 8192

# Get model context length from environment
def get_model_context_length():
    """Get the current model context length from environment or use default"""
    return int(os.getenv("CURRENT_MODEL_CONTEXT_LENGTH", DEFAULT_MODEL_CONTEXT_LENGTH))

# Reserve 20% of context for model response
def get_max_input_tokens():
    """Calculate max input tokens based on current model context length"""
    return int(get_model_context_length() * 0.8)

# For backward compatibility - these values will be used by other modules
# but we'll override the MODEL_CONTEXT_LENGTH and MAX_INPUT_TOKENS at runtime
MODEL_CONTEXT_LENGTH = get_model_context_length()
MAX_INPUT_TOKENS = get_max_input_tokens()

# Language mapping from file extensions to tree-sitter language names
LANGUAGE_MAPPING = {
    # Python
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    
    # Java
    ".java": "java",
    
    # Rust
    ".rs": "rust",
    
    # Go
    ".go": "go",
    
    # Scala
    ".scala": "scala",
    
    # Clojure
    ".clj": "clojure",
    ".cljc": "clojure",
    ".cljs": "clojure",
    
    # TypeScript/JavaScript
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "javascript",
    
    # C#
    ".cs": "c_sharp",
    
    # F#
    ".fs": "f_sharp",
    ".fsx": "f_sharp",
    
    # C/C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    
    # Other common languages
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
}

# Try to import tree-sitter and set up available languages
try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
    AVAILABLE_LANGUAGES = set()
    
    # Try to import typescript support using our custom wrapper
    try:
        from utils.typescript_support import get_typescript_parser, get_tsx_parser
        
        # Test if we can actually get TypeScript parser
        ts_parser, _ = get_typescript_parser()
        if ts_parser is not None:
            AVAILABLE_LANGUAGES.add('typescript')
            logger.info("Tree-sitter TypeScript support loaded successfully")
        
        # Test if we can actually get TSX parser
        tsx_parser, _ = get_tsx_parser()
        if tsx_parser is not None:
            AVAILABLE_LANGUAGES.add('tsx')
            logger.info("Tree-sitter TSX support loaded successfully")
            
        if not AVAILABLE_LANGUAGES:
            logger.warning("TypeScript/TSX parsers could not be initialized")
    except ImportError as e:
        logger.warning(f"TypeScript support module not found: {e}")
        
    # Additional languages support - attempt to load tree-sitter-language-pack
    try:
        from tree_sitter_language_pack import get_parser, get_language
        
        # For each language in LANGUAGE_MAPPING, try to load it from tree-sitter-language-pack
        for ext, lang in LANGUAGE_MAPPING.items():
            if lang not in AVAILABLE_LANGUAGES:
                try:
                    parser = get_parser(lang)
                    if parser is not None:
                        AVAILABLE_LANGUAGES.add(lang)
                        logger.info(f"Tree-sitter {lang} support loaded successfully")
                except (ImportError, ValueError, AttributeError, Exception) as e:
                    # Silently continue if a language isn't available
                    pass
                
        logger.info(f"Total available languages: {len(AVAILABLE_LANGUAGES)}")
        
    except ImportError:
        logger.warning("tree-sitter-language-pack not available, only TypeScript and TSX supported")
        
except ImportError:
    TREE_SITTER_AVAILABLE = False
    AVAILABLE_LANGUAGES = set()
    logger.warning("Tree-sitter not available - using fallback code chunking mechanism instead")

# Node types that represent different hierarchical levels for different languages
# Level 3: Class/Module level
CLASS_MODULE_TYPES = {
    "python": ["class_definition", "module"],
    "java": ["class_declaration", "interface_declaration", "enum_declaration"],
    "typescript": ["class_declaration", "interface_declaration", "namespace_declaration", "module", "type_alias_declaration"],
    "tsx": ["class_declaration", "interface_declaration", "namespace_declaration", "module", "type_alias_declaration"],
    "javascript": ["class_declaration", "program"],
    "c_sharp": ["class_declaration", "interface_declaration", "namespace_declaration"],
    "rust": ["impl_item", "trait_definition", "mod_item"],
    "go": ["type_declaration", "package_clause"],
    "scala": ["class_definition", "object_definition", "trait_declaration"],
    "clojure": ["list", "vector"],
    "f_sharp": ["module_declaration", "namespace_declaration", "type_definition"],
    "c": ["struct_specifier", "enum_specifier", "union_specifier"],
    "cpp": ["class_specifier", "namespace_definition", "struct_specifier"],
}

# Level 4: Function/Method level
FUNCTION_METHOD_TYPES = {
    "python": ["function_definition", "decorated_definition"],
    "java": ["method_declaration", "constructor_declaration"],
    "typescript": ["function_declaration", "method_definition", "arrow_function", "constructor_declaration"],
    "tsx": ["function_declaration", "method_definition", "arrow_function", "constructor_declaration"],
    "javascript": ["function_declaration", "method_definition", "arrow_function"],
    "c_sharp": ["method_declaration", "constructor_declaration"],
    "rust": ["function_item", "function_signature_item", "impl_function_statement"],
    "go": ["function_declaration", "method_declaration"],
    "scala": ["function_definition", "def_declaration", "val_declaration"],
    "clojure": ["list"],  # Qualified by content analysis 
    "f_sharp": ["member_definition", "let_declaration", "function_definition"],
    "c": ["function_definition", "declaration"],
    "cpp": ["function_definition", "method_definition", "declaration"],
}

# Level 5: Statement level
STATEMENT_TYPES = {
    "python": ["if_statement", "for_statement", "while_statement", "try_statement", "with_statement", 
               "return_statement", "expression_statement", "assert_statement"],
    "java": ["if_statement", "for_statement", "while_statement", "try_statement", "switch_statement", 
             "return_statement", "expression_statement", "assert_statement"],
    "typescript": ["if_statement", "for_statement", "while_statement", "try_statement", "switch_statement", 
                  "return_statement", "expression_statement", "variable_declaration", "await_expression"],
    "tsx": ["if_statement", "for_statement", "while_statement", "try_statement", "switch_statement", 
           "return_statement", "expression_statement", "variable_declaration", "jsx_element", "jsx_fragment"],
    "javascript": ["if_statement", "for_statement", "while_statement", "try_statement", "switch_statement", 
                  "return_statement", "expression_statement"],
    "c_sharp": ["if_statement", "for_statement", "foreach_statement", "while_statement", "try_statement", 
               "switch_statement", "return_statement", "expression_statement"],
    "rust": ["if_expression", "for_expression", "while_expression", "block_expression", "return_expression",
            "match_expression", "expression_statement"],
    "go": ["if_statement", "for_statement", "range_clause", "return_statement", "expression_statement", 
          "assignment_statement"],
    "scala": ["if_expression", "for_expression", "while_expression", "match_expression", "try_expression",
             "return_expression", "expression_statement"],
    "clojure": ["list"],  # Qualified by content analysis
    "f_sharp": ["match_expression", "if_expression", "for_expression", "while_expression", "try_expression"],
    "c": ["if_statement", "for_statement", "while_statement", "do_statement", "switch_statement", 
         "return_statement", "expression_statement"],
    "cpp": ["if_statement", "for_statement", "while_statement", "do_statement", "switch_statement", 
           "return_statement", "expression_statement"],
}

# Token count estimator - simple approximation based on whitespace splitting
def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in text.
    This is a simple approximation based on whitespace and punctuation.
    """
    text = text.strip()
    if not text:
        return 0
    
    # Split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(tokens)

class CodeChunk:
    """Represents a chunk of code with metadata about its origin and hierarchical level."""
    
    def __init__(self, content: str, file_path: str, lang: str, level: int, 
                 start_line: int = 0, end_line: int = 0, node_type: str = "", 
                 parent_chunk: Optional['CodeChunk'] = None):
        self.content = content
        self.file_path = file_path
        self.lang = lang
        self.level = level  # 1=dir, 2=file, 3=class, 4=function, 5=statement
        self.start_line = start_line
        self.end_line = end_line
        self.node_type = node_type
        self.parent_chunk = parent_chunk
        self.est_tokens = estimate_tokens(content)
    
    def __repr__(self):
        path = os.path.basename(self.file_path)
        return f"CodeChunk(level={self.level}, path='{path}', lines={self.start_line}-{self.end_line}, type={self.node_type}, tokens={self.est_tokens})"
    
    def get_hierarchy_path(self) -> str:
        """Get the hierarchical path for this chunk."""
        if self.parent_chunk:
            parent_path = self.parent_chunk.get_hierarchy_path()
            return f"{parent_path} > {self.node_type}[{self.start_line}-{self.end_line}]"
        return f"{os.path.basename(self.file_path)}:{self.node_type}[{self.start_line}-{self.end_line}]"

class ASTChunker:
    """Abstract base class for AST-based code chunkers."""
    
    def __init__(self):
        pass
    
    def extract_chunks(self, file_path: str, content: str) -> List[CodeChunk]:
        """Extract chunks from the given content."""
        raise NotImplementedError("Subclasses must implement extract_chunks")
    
    def _line_col_to_position(self, content: str, line: int, col: int) -> int:
        """Convert line and column to a position within the string."""
        lines = content.split('\n')
        position = sum(len(lines[i]) + 1 for i in range(line))
        position += col
        return position
    
    def _get_source_lines(self, content: str, start_line: int, end_line: int) -> str:
        """Extract lines from the content."""
        lines = content.split('\n')
        return '\n'.join(lines[start_line:end_line + 1])

class TreeSitterChunker(ASTChunker):
    """
    Tree-sitter based implementation of the AST chunker.
    Supports multiple languages through tree-sitter parsers.
    """
    
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang
        self.parser = None
        self.language = None
        
        if not TREE_SITTER_AVAILABLE:
            logger.warning(f"Tree-sitter not available, using fallback for {lang}")
            return
            
        # Check if this language is in our list of available languages
        if lang not in AVAILABLE_LANGUAGES:
            logger.warning(f"Tree-sitter parser for language '{lang}' not available, using fallback chunking")
            return
            
        try:
            # Special handling for TypeScript/TSX which has a dedicated package
            if lang in ['typescript', 'tsx']:
                try:
                    # Use our custom TypeScript support module
                    from utils.typescript_support import get_typescript_parser, get_tsx_parser
                    
                    if lang == 'typescript':
                        parser, language_obj = get_typescript_parser()
                        logger.info(f"Using typescript_support.get_typescript_parser() for {lang}")
                    else:  # tsx
                        parser, language_obj = get_tsx_parser()
                        logger.info(f"Using typescript_support.get_tsx_parser() for {lang}")
                    
                    if parser is None or language_obj is None:
                        logger.warning(f"Could not initialize parser for {lang}")
                        logger.warning(f"Using fallback for {lang}")
                        return
                    
                    self.parser = parser
                    self.language = language_obj
                    logger.info(f"Successfully initialized parser for {lang}")
                except ImportError as e:
                    logger.warning(f"TypeScript support module failed to load: {e}")
                    logger.warning(f"Using fallback for {lang}")
                    return
                except Exception as e:
                    logger.error(f"Failed to initialize {lang} parser: {e}")
                    logger.warning(f"Using fallback for {lang}")
                    return
            else:
                # For other languages, try to use tree-sitter-language-pack
                try:
                    from tree_sitter_language_pack import get_parser, get_language
                    
                    # Map language ID to tree-sitter language name for other languages
                    ts_lang_map = {
                        'javascript': 'javascript',
                        'python': 'python',
                        'java': 'java',
                        'c_sharp': 'c_sharp',
                        'go': 'go',
                        'rust': 'rust',
                        'cpp': 'cpp',
                        'c': 'c',
                        # Add more mappings as needed
                    }
                    
                    # Use the mapped language name or the original if not in map
                    ts_lang = ts_lang_map.get(lang, lang)
                    
                    # Get parser and language using tree-sitter-language-pack
                    self.parser = get_parser(ts_lang)
                    self.language = get_language(ts_lang)
                    logger.info(f"Using tree-sitter-language-pack for {lang}")
                    
                except (ImportError, ValueError, AttributeError) as e:
                    logger.warning(f"Failed to get parser/language from tree-sitter-language-pack: {e}")
                    logger.warning(f"Using fallback for {lang}")
                    return
                except Exception as e:
                    logger.error(f"Failed to get parser/language for {ts_lang}: {e}")
                    logger.warning(f"Using fallback for {lang}")
                    return
            
            logger.info(f"Successfully initialized TreeSitterChunker for language '{lang}'")
        except Exception as e:
            logger.error(f"Failed to initialize TreeSitterChunker for language '{lang}': {e}")
            logger.warning(f"Using fallback text-based chunking for language '{lang}'")
            # parser remains None to trigger fallback processing

    def extract_chunks(self, file_path: str, content: str) -> List[CodeChunk]:
        """
        Extract hierarchical chunks from the given file content using tree-sitter.
        
        Args:
            file_path: Path to the file being processed
            content: Source code content
            
        Returns:
            List of CodeChunk objects representing different levels of hierarchy
        """
        if not content.strip():
            return []
        
        # Start with a file-level chunk (level 2)
        chunks = [
            CodeChunk(
                content=content,
                file_path=file_path,
                lang=self.lang,
                level=2,  # File level
                start_line=0,
                end_line=content.count('\n'),
                node_type="file"
            )
        ]
        
        # If parser initialization failed, use a fallback line-based chunking approach
        if self.parser is None:
            logger.info(f"Using fallback line-based chunking for {file_path}")
            return self._fallback_extract_chunks(file_path, content, chunks)
        
        # Parse the content into a tree
        try:
            tree = self.parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node
        except Exception as e:
            logger.error(f"Error parsing {file_path} with tree-sitter: {e}")
            return self._fallback_extract_chunks(file_path, content, chunks)
        
        # Extract class/module level chunks (level 3)
        class_chunks = self._extract_level_chunks(
            root_node, 
            content, 
            file_path, 
            3, 
            CLASS_MODULE_TYPES.get(self.lang, [])
        )
        chunks.extend(class_chunks)
        
        # For each class/module, extract function/method level chunks (level 4)
        for class_chunk in class_chunks:
            class_node = self._find_node_by_range(
                root_node, 
                class_chunk.start_line, 
                class_chunk.end_line
            )
            if class_node:
                function_chunks = self._extract_level_chunks(
                    class_node, 
                    content, 
                    file_path, 
                    4, 
                    FUNCTION_METHOD_TYPES.get(self.lang, []),
                    parent_chunk=class_chunk
                )
                chunks.extend(function_chunks)
        
        # Also extract top-level functions (not inside classes)
        function_chunks = self._extract_level_chunks(
            root_node, 
            content, 
            file_path, 
            4, 
            FUNCTION_METHOD_TYPES.get(self.lang, [])
        )
        
        # Filter out functions that are inside classes (to avoid duplicates)
        top_level_functions = []
        for func in function_chunks:
            if not any(
                c.start_line <= func.start_line and c.end_line >= func.end_line
                for c in class_chunks
            ):
                top_level_functions.append(func)
                
        chunks.extend(top_level_functions)
        
        # For each function/method, extract statement level chunks (level 5)
        all_func_chunks = function_chunks + [f for f in chunks if f.level == 4]
        for func_chunk in all_func_chunks:
            func_node = self._find_node_by_range(
                root_node, 
                func_chunk.start_line, 
                func_chunk.end_line
            )
            if func_node:
                statement_chunks = self._extract_level_chunks(
                    func_node, 
                    content, 
                    file_path, 
                    5, 
                    STATEMENT_TYPES.get(self.lang, []),
                    parent_chunk=func_chunk
                )
                chunks.extend(statement_chunks)
        
        return chunks
        
    def _fallback_extract_chunks(self, file_path: str, content: str, base_chunks: List[CodeChunk]) -> List[CodeChunk]:
        """
        Fallback chunking method when tree-sitter parsing fails.
        Uses a simple line-based approach to extract potential code structures.
        
        Args:
            file_path: Path to the file being processed
            content: Source code content
            base_chunks: Existing base chunks (file level)
            
        Returns:
            List of CodeChunk objects with best-effort hierarchy detection
        """
        chunks = list(base_chunks)  # Start with base chunks (file level)
        lines = content.split('\n')
        
        # Simple heuristic patterns for detecting structures
        class_pattern = r'^\s*(class|interface|namespace|module|enum)\s+([\w\d_]+)'
        function_pattern = r'^\s*(function|def|fn|method|\w+\s+\w+\()\s*([\w\d_]+)'
        
        # Track current chunk info
        current_class = None
        current_class_lines = []
        current_function = None
        current_function_lines = []
        
        for i, line in enumerate(lines):
            # Look for class/module definitions
            class_match = re.search(class_pattern, line)
            if class_match and not current_function:  # Don't start a class inside a function
                # If we were in a class, finish it
                if current_class:
                    class_content = '\n'.join(current_class_lines)
                    chunks.append(CodeChunk(
                        content=class_content,
                        file_path=file_path,
                        lang=self.lang,
                        level=3,  # Class/module level
                        start_line=current_class[0],
                        end_line=i-1,
                        node_type=f"class_{current_class[1]}"
                    ))
                
                # Start new class
                current_class = (i, class_match.group(2))
                current_class_lines = [line]
                continue
            
            # Look for function/method definitions
            function_match = re.search(function_pattern, line)
            if function_match:
                # If we were in a function, finish it
                if current_function:
                    function_content = '\n'.join(current_function_lines)
                    parent = None
                    if current_class:  # This function is inside a class
                        # Find the class chunk as parent
                        for chunk in chunks:
                            if chunk.level == 3 and chunk.node_type == f"class_{current_class[1]}":
                                parent = chunk
                                break
                    
                    chunks.append(CodeChunk(
                        content=function_content,
                        file_path=file_path,
                        lang=self.lang,
                        level=4,  # Function/method level
                        start_line=current_function[0],
                        end_line=i-1,
                        node_type=f"function_{current_function[1]}",
                        parent_chunk=parent
                    ))
                
                # Start new function
                current_function = (i, function_match.group(2))
                current_function_lines = [line]
                if current_class:
                    current_class_lines.append(line)
                continue
            
            # Add line to current chunks
            if current_function:
                current_function_lines.append(line)
            if current_class:
                current_class_lines.append(line)
        
        # Close any open chunks
        if current_function:
            function_content = '\n'.join(current_function_lines)
            parent = None
            if current_class:  # This function is inside a class
                # Find the class chunk as parent
                for chunk in chunks:
                    if chunk.level == 3 and chunk.node_type == f"class_{current_class[1]}":
                        parent = chunk
                        break
            
            chunks.append(CodeChunk(
                content=function_content,
                file_path=file_path,
                lang=self.lang,
                level=4,  # Function/method level
                start_line=current_function[0],
                end_line=len(lines)-1,
                node_type=f"function_{current_function[1]}",
                parent_chunk=parent
            ))
        
        if current_class and not current_function:  # Only close class if not already closed with function
            class_content = '\n'.join(current_class_lines)
            chunks.append(CodeChunk(
                content=class_content,
                file_path=file_path,
                lang=self.lang,
                level=3,  # Class/module level
                start_line=current_class[0],
                end_line=len(lines)-1,
                node_type=f"class_{current_class[1]}"
            ))
        
        return chunks
    
    def _find_node_by_range(self, root_node, start_line, end_line):
        """Find a node that matches the given line range."""
        # Simple BFS to find the node
        queue = [root_node]
        while queue:
            node = queue.pop(0)
            if (node.start_point[0] == start_line and 
                node.end_point[0] == end_line):
                return node
            
            # Add children to queue
            for child in node.children:
                queue.append(child)
                
        return None
    
    def _extract_level_chunks(self, 
                             node, 
                             content: str, 
                             file_path: str, 
                             level: int, 
                             node_types: List[str],
                             parent_chunk: Optional[CodeChunk] = None):
        """
        Extract chunks for a specific level from the AST.
        
        Args:
            node: The AST node to extract from
            content: Source code content
            file_path: Path to the file being processed
            level: Hierarchical level (1-5)
            node_types: Node types to consider for this level
            parent_chunk: Optional parent chunk for hierarchy tracking
            
        Returns:
            List of CodeChunk objects for this level
        """
        chunks = []
        
        # Check if we're using a simplified parser implementation
        # If the node is missing expected methods, use fallback
        if not hasattr(node, 'goto_first_child') or hasattr(node, '_is_simplified_parser'):
            # Create a simple file-level chunk and return it
            # This is a minimal implementation that will work even with incompatible parsers
            file_chunk = CodeChunk(
                content=content,
                file_path=file_path,
                lang=self.lang,
                level=2,  # File level
                start_line=0,
                end_line=content.count('\n') + 1,
                node_type="file",
                parent_chunk=None
            )
            chunks.append(file_chunk)
            return chunks
        
        cursor = node.walk()
        
        def visit_node(node):
            if node.type in node_types:
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                
                # Extract the text range
                node_content = self._get_source_lines(content, start_line, end_line)
                
                chunk = CodeChunk(
                    content=node_content,
                    file_path=file_path,
                    lang=self.lang,
                    level=level,
                    start_line=start_line,
                    end_line=end_line,
                    node_type=node.type,
                    parent_chunk=parent_chunk
                )
                chunks.append(chunk)
        
        # Traverse the tree
        visit_node(node)
        if cursor.goto_first_child():
            while True:
                visit_node(cursor.node)
                
                # Depth-first traversal
                if cursor.goto_first_child():
                    continue
                
                if cursor.goto_next_sibling():
                    continue
                    
                retracing = True
                while retracing:
                    if not cursor.goto_parent():
                        retracing = False
                        return chunks
                    
                    if cursor.goto_next_sibling():
                        retracing = False
        
        return chunks


class DirectoryChunker:
    """
    Handles directory-level chunking (level 1) by organizing files into logical groups.
    """
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def chunk_directory(self, files: List[str]) -> List[CodeChunk]:
        """
        Group files into directory-level chunks.
        
        Args:
            files: List of file paths to process
            
        Returns:
            List of directory-level CodeChunk objects
        """
        # Group files by directory
        dir_files: Dict[str, List[str]] = {}
        for file_path in files:
            dir_path = os.path.dirname(file_path)
            if dir_path not in dir_files:
                dir_files[dir_path] = []
            dir_files[dir_path].append(file_path)
        
        # Create directory-level chunks
        chunks = []
        for dir_path, dir_file_paths in dir_files.items():
            # Create a summary of the directory structure
            rel_dir = os.path.relpath(dir_path, self.base_dir) if self.base_dir in dir_path else dir_path
            content = f"Directory: {rel_dir}\n\nFiles:\n"
            for file_path in dir_file_paths:
                rel_path = os.path.relpath(file_path, self.base_dir) if self.base_dir in file_path else file_path
                content += f"- {rel_path}\n"
            
            chunk = CodeChunk(
                content=content,
                file_path=dir_path,
                lang="text",  # Directory chunks are just text
                level=1,  # Directory level
                node_type="directory"
            )
            chunks.append(chunk)
        
        return chunks


class CodeChunkingManager:
    """
    Main class for managing code chunking across multiple languages.
    Implements the Adapter pattern to integrate with existing code.
    """
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.chunkers: Dict[str, TreeSitterChunker] = {}
        self.dir_chunker = DirectoryChunker(base_dir)
        
    def get_chunker_for_file(self, file_path: str) -> Optional[TreeSitterChunker]:
        """Get the appropriate chunker for a given file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in LANGUAGE_MAPPING:
            return None
        
        lang = LANGUAGE_MAPPING[ext]
        
        # Create a new chunker if we don't have one for this language
        if lang not in self.chunkers:
            try:
                self.chunkers[lang] = TreeSitterChunker(lang)
            except Exception as e:
                logger.warning(f"Failed to create chunker for {lang}: {e}")
                return None
                
        return self.chunkers[lang]
    
    def chunk_files(self, file_paths: List[str], file_contents: Dict[str, str]) -> List[CodeChunk]:
        """
        Process multiple files and generate hierarchical chunks.
        
        Args:
            file_paths: List of file paths to process
            file_contents: Dict mapping file paths to their contents
            
        Returns:
            List of hierarchical CodeChunk objects
        """
        all_chunks = []
        
        # First, create directory-level chunks (level 1)
        dir_chunks = self.dir_chunker.chunk_directory(file_paths)
        all_chunks.extend(dir_chunks)
        
        # Process each file
        for file_path in file_paths:
            if file_path not in file_contents:
                logger.warning(f"No content available for {file_path}")
                continue
                
            content = file_contents[file_path]
            chunker = self.get_chunker_for_file(file_path)
            
            if chunker:
                try:
                    file_chunks = chunker.extract_chunks(file_path, content)
                    all_chunks.extend(file_chunks)
                except Exception as e:
                    logger.error(f"Error chunking {file_path}: {e}")
            else:
                # For unsupported file types, just create a file-level chunk (level 2)
                chunk = CodeChunk(
                    content=content,
                    file_path=file_path,
                    lang="text",
                    level=2,  # File level
                    start_line=0,
                    end_line=content.count('\n'),
                    node_type="file"
                )
                all_chunks.append(chunk)
        
        return all_chunks
    
    def create_overlapping_chunks(self, chunks: List[CodeChunk], 
                                 max_tokens: int = None,
                                 overlap_ratio: float = 0.2) -> List[CodeChunk]:
        """
        Create overlapping chunks that fit within token limits.
        
        Args:
            chunks: List of original chunks
            max_tokens: Maximum tokens per chunk (80% of model context length)
            overlap_ratio: Ratio of content to overlap between chunks
            
        Returns:
            List of combined chunks that respect token limits with overlap
        """
        if not chunks:
            return []
            
        # If max_tokens is not provided, use the current value from environment
        if max_tokens is None:
            max_tokens = get_max_input_tokens()
            
        # Calculate max overlap tokens
        overlap_tokens = int(max_tokens * overlap_ratio)
            
        # Sort chunks by file_path and then by start_line to ensure
        # related chunks are grouped together
        sorted_chunks = sorted(
            chunks, 
            key=lambda c: (c.file_path, c.start_line)
        )
        
        combined_chunks = []
        current_chunk_content = ""
        current_chunk_tokens = 0
        current_files = set()
        current_hierarchy = []
        
        for chunk in sorted_chunks:
            # If adding this chunk would exceed the token limit,
            # save the current combined chunk and start a new one
            if current_chunk_tokens + chunk.est_tokens > max_tokens and current_chunk_content:
                # Create the combined chunk
                combined_chunk = CodeChunk(
                    content=current_chunk_content,
                    file_path=";".join(current_files),
                    lang="mixed",
                    level=0,  # Combined level
                    node_type="combined_chunk"
                )
                combined_chunks.append(combined_chunk)
                
                # Start a new chunk with overlap from the previous one
                overlap_chunks = []
                if overlap_tokens > 0:
                    overlap_token_count = 0
                    for prev_chunk in reversed(current_hierarchy):
                        if overlap_token_count + prev_chunk.est_tokens <= overlap_tokens:
                            overlap_chunks.insert(0, prev_chunk)
                            overlap_token_count += prev_chunk.est_tokens
                        else:
                            break
                else:
                    current_chunk_content = ""
                    current_files = set()
                    current_chunk_tokens = 0
                    current_hierarchy = []
            
            # Add file header if this is from a new file
            if chunk.file_path not in current_files or not current_chunk_content:
                header = f"\n# FILE: {os.path.basename(chunk.file_path)}\n"
                if current_chunk_content:
                    current_chunk_content += header
                    current_chunk_tokens += estimate_tokens(header)
            
            # Add this chunk to the current combined chunk
            current_chunk_content += chunk.content + "\n"
            current_files.add(chunk.file_path)
            current_chunk_tokens += chunk.est_tokens + 1  # +1 for newline
            current_hierarchy.append(chunk)
        
        # Don't forget to add the last combined chunk
        if current_chunk_content:
            combined_chunk = CodeChunk(
                content=current_chunk_content,
                file_path=";".join(current_files),
                lang="mixed",
                level=0,  # Combined level
                node_type="combined_chunk"
            )
            combined_chunks.append(combined_chunk)
        
        return combined_chunks


def chunk_codebase(base_dir: str, 
                  file_paths: List[str], 
                  file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Main entry point for codebase chunking.
    
    Args:
        base_dir: Base directory of the codebase
        file_paths: List of file paths to process
        file_contents: Dict mapping file paths to their contents
        
    Returns:
        List of dictionaries representing the final chunks, ready for LLM input
    """
    manager = CodeChunkingManager(base_dir)
    
    # Generate hierarchical chunks for all files
    all_chunks = manager.chunk_files(file_paths, file_contents)
    
    # Get the current model values
    current_model_context_length = get_model_context_length()
    current_max_input_tokens = get_max_input_tokens()
    
    # Create overlapping chunks that fit within token limits
    combined_chunks = manager.create_overlapping_chunks(
        all_chunks, 
        max_tokens=current_max_input_tokens
    )
    
    # Convert to a format suitable for LLM input
    result = []
    for i, chunk in enumerate(combined_chunks):
        result.append({
            "chunk_id": i,
            "content": chunk.content,
            "token_count": chunk.est_tokens,
            "files": chunk.file_path.split(";"),
        })
    
    return result


# Example usage (for demonstration)
if __name__ == "__main__":
    # Example with a single Python file
    file_path = "example.py"
    file_content = """
def hello(name):
    print(f"Hello, {name}!")
    
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    def greet(self):
        if self.age > 18:
            print(f"Hello, Mr/Ms {self.name}!")
        else:
            print(f"Hi, {self.name}!")
            
p = Person("Alice", 25)
p.greet()
hello("Bob")
"""
    
    files = [file_path]
    contents = {file_path: file_content}
    
    chunks = chunk_codebase(".", files, contents)
    
    for chunk in chunks:
        print(f"Chunk {chunk['chunk_id']} ({chunk['token_count']} tokens):")
        print("-" * 40)
        print(chunk['content'])
        print("-" * 40)
