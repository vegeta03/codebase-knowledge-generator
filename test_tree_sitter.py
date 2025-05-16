#!/usr/bin/env python
"""
Diagnostic script to test tree-sitter installation and TypeScript support
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tree_sitter_test")

def test_base_tree_sitter():
    """Test basic tree-sitter import and version"""
    logger.info("Testing basic tree-sitter...")
    try:
        import tree_sitter
        import pkg_resources
        
        # Get version
        try:
            version = pkg_resources.get_distribution("tree-sitter").version
            logger.info(f"✓ tree-sitter installed: version {version}")
            
            # Check if we need compatibility mode
            needs_compat = version.startswith("0.2") and int(version.split('.')[1]) >= 22
            if needs_compat:
                logger.info(f"✓ Tree-sitter version {version} requires compatibility mode")
            return True
        except Exception as e:
            logger.error(f"✗ Error getting tree-sitter version: {e}")
            return False
    except ImportError:
        logger.error("✗ tree-sitter not installed")
        return False

def test_tree_sitter_languages():
    """Test tree-sitter-languages package"""
    logger.info("Testing tree-sitter-languages...")
    try:
        from tree_sitter_languages import get_language, get_parser
        import pkg_resources
        
        try:
            version = pkg_resources.get_distribution("tree-sitter-languages").version
            logger.info(f"✓ tree-sitter-languages installed: version {version}")
            
            # Try to access common languages
            try:
                python_parser = get_parser("python")
                logger.info("✓ Successfully got Python parser")
                
                # Try JavaScript as it's close to TypeScript
                js_parser = get_parser("javascript")
                logger.info("✓ Successfully got JavaScript parser")
                
                return True
            except Exception as e:
                logger.error(f"✗ Error getting language parsers: {e}")
                return False
        except Exception as e:
            logger.error(f"✗ Error getting tree-sitter-languages version: {e}")
            return False
    except ImportError:
        logger.error("✗ tree-sitter-languages not installed")
        return False

def test_typescript_support():
    """Test TypeScript-specific support"""
    logger.info("Testing TypeScript support...")
    try:
        import tree_sitter_typescript
        logger.info("✓ tree-sitter-typescript package found")
        
        # Get version if possible
        try:
            import pkg_resources
            version = pkg_resources.get_distribution("tree-sitter-typescript").version
            logger.info(f"✓ tree-sitter-typescript version: {version}")
        except Exception:
            logger.info("? Unable to determine tree-sitter-typescript version")
        
        # Test access to TypeScript language
        try:
            ts_language = tree_sitter_typescript.language()
            logger.info("✓ Successfully got TypeScript language")
            
            # Create a parser with the TypeScript language
            import tree_sitter
            parser = tree_sitter.Parser()
            parser.set_language(ts_language)
            logger.info("✓ Successfully created TypeScript parser")
            
            # Test with a simple TypeScript snippet
            typescript_code = """
            interface Person {
                name: string;
                age: number;
            }
            
            class Employee implements Person {
                name: string;
                age: number;
                salary: number;
                
                constructor(name: string, age: number, salary: number) {
                    this.name = name;
                    this.age = age;
                    this.salary = salary;
                }
            }
            """
            
            tree = parser.parse(bytes(typescript_code, "utf8"))
            root_node = tree.root_node
            logger.info(f"✓ Successfully parsed TypeScript: {root_node.type}")
            
            # Test TSX support as well
            try:
                tsx_language = tree_sitter_typescript.language("tsx")
                logger.info("✓ Successfully got TSX language")
                
                parser = tree_sitter.Parser()
                parser.set_language(tsx_language)
                logger.info("✓ Successfully created TSX parser")
                
                tsx_code = """
                interface Props {
                    name: string;
                }
                
                function Greeting({ name }: Props) {
                    return <h1>Hello, {name}!</h1>;
                }
                
                export default function App() {
                    return <Greeting name="World" />;
                }
                """
                
                tree = parser.parse(bytes(tsx_code, "utf8"))
                root_node = tree.root_node
                logger.info(f"✓ Successfully parsed TSX: {root_node.type}")
                
                return True
            except Exception as e:
                logger.error(f"✗ Error with TSX support: {e}")
                # TypeScript might still be fine even if TSX fails
                return True
                
        except Exception as e:
            logger.error(f"✗ Error using TypeScript language: {e}")
            return False
            
    except ImportError:
        logger.error("✗ tree-sitter-typescript not installed")
        return False

def test_code_chunking_integration():
    """Test the integration with your code_chunking module"""
    logger.info("Testing integration with code_chunking module...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from utils.code_chunking import TREE_SITTER_AVAILABLE, AVAILABLE_LANGUAGES
        
        logger.info(f"TREE_SITTER_AVAILABLE = {TREE_SITTER_AVAILABLE}")
        logger.info(f"AVAILABLE_LANGUAGES = {AVAILABLE_LANGUAGES}")
        
        # Test if TypeScript is in available languages
        if 'typescript' in AVAILABLE_LANGUAGES:
            logger.info("✓ TypeScript is in AVAILABLE_LANGUAGES")
        else:
            logger.error("✗ TypeScript is NOT in AVAILABLE_LANGUAGES")
        
        # Test tree-sitter chunker initialization for TypeScript
        from utils.code_chunking import TreeSitterChunker
        try:
            ts_chunker = TreeSitterChunker('typescript')
            if ts_chunker.parser is not None:
                logger.info("✓ Successfully created TypeScript chunker with a parser")
                return True
            else:
                logger.error("✗ TypeScript chunker created but parser is None")
                return False
        except Exception as e:
            logger.error(f"✗ Error creating TypeScript chunker: {e}")
            return False
        
    except ImportError as e:
        logger.error(f"✗ Error importing from code_chunking: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error with code_chunking integration: {e}")
        return False

def main():
    """Main test function"""
    print("=== Tree-Sitter Diagnostic Tests ===")
    print()
    
    # Test base tree-sitter
    base_ok = test_base_tree_sitter()
    print()
    
    # Test tree-sitter-languages
    langs_ok = test_tree_sitter_languages()
    print()
    
    # Test TypeScript support
    ts_ok = test_typescript_support()
    print()
    
    # Test integration with code_chunking
    integration_ok = test_code_chunking_integration()
    print()
    
    # Summary
    print("=== Test Summary ===")
    print(f"Base tree-sitter: {'✓ OK' if base_ok else '✗ FAILED'}")
    print(f"tree-sitter-languages: {'✓ OK' if langs_ok else '✗ FAILED'}")
    print(f"TypeScript support: {'✓ OK' if ts_ok else '✗ FAILED'}")
    print(f"Code chunking integration: {'✓ OK' if integration_ok else '✗ FAILED'}")
    
    # Overall status
    if all([base_ok, langs_ok, ts_ok, integration_ok]):
        print("\nAll tests PASSED! Everything should work correctly.")
    else:
        print("\nSome tests FAILED. Check the logs for details.")

if __name__ == "__main__":
    main()
