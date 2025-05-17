from utils.typescript_support import get_typescript_parser, test_typescript_parsing
import logging

# Configure logging for standalone testing
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Basic test
print("Testing basic TypeScript support...")
ts_parser, ts_language = get_typescript_parser()
if ts_parser:
    print("✓ TypeScript parser initialized successfully")
    test_result = test_typescript_parsing()
    print(f"Basic TypeScript parsing test: {'✓ Passed' if test_result else '✗ Failed'}")
else:
    print("✗ Could not initialize TypeScript parser")

# Test more complex TypeScript syntax to identify limitations
complex_typescript_code = """
// Complex TypeScript example to test parser limitations

// 1. Type definitions
type User = {
    id: number;
    name: string;
    isActive: boolean;
    metadata?: Record<string, unknown>;
};

// 2. Generic interfaces
interface Repository<T> {
    getById(id: number): Promise<T>;
    getAll(): Promise<T[]>;
    save(item: T): Promise<void>;
}

// 3. Classes with decorators
@Component({
    selector: 'app-root',
    template: '<div>{{title}}</div>'
})
class AppComponent implements OnInit {
    @Input() title: string = "Default Title";
    
    constructor(private service: UserService) {}
    
    ngOnInit(): void {
        this.service.getUser().then(user => {
            console.log(`User loaded: ${user.name}`);
        });
    }
    
    @HostListener('click')
    handleClick(): void {
        alert('Clicked!');
    }
}

// 4. Advanced type operations
type ExtractKeys<T> = keyof T;
type UserKeys = ExtractKeys<User>;

// 5. Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;

// 6. Mapped types
type ReadonlyUser = {
    readonly [K in keyof User]: User[K];
};

// 7. Utility types usage
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;

// 8. Template literal types
type EventName<T extends string> = `on${Capitalize<T>}`;
type UserEvents = EventName<'load' | 'save' | 'delete'>;

// 9. Namespaces
namespace Validation {
    export interface StringValidator {
        isValid(s: string): boolean;
    }
    
    export class RegexValidator implements StringValidator {
        constructor(private regex: RegExp) {}
        
        isValid(s: string): boolean {
            return this.regex.test(s);
        }
    }
}

// 10. Async/await with type annotations
async function fetchData<T>(url: string): Promise<T> {
    const response = await fetch(url);
    return await response.json() as T;
}
"""

print("\nTesting complex TypeScript parsing with simplified parser...")
try:
    tree = ts_parser.parse(bytes(complex_typescript_code, "utf8"))
    root_node = tree.root_node
    print(f"✓ Successfully parsed complex TypeScript code. Root node type: {root_node.type}")
    
    print("\nExploring simplified AST structure...")
    def print_node(node, depth=0):
        indent = "  " * depth
        print(f"{indent}- {node.type} [{node.start_point[0]}:{node.start_point[1]} - {node.end_point[0]}:{node.end_point[1]}]")
        for child in node.children:
            print_node(child, depth + 1)
    
    # Print only top-level nodes to avoid overwhelming output
    for child in root_node.children:
        print_node(child, 1)
    
except Exception as e:
    print(f"✗ Error parsing complex TypeScript with simplified parser: {e}")

# Compare with tree-sitter-language-pack if installed
try:
    from tree_sitter_language_pack import get_parser as get_ts_parser
    print("\nTesting with tree-sitter-language-pack...")
    ts_parser_official = get_ts_parser("typescript")
    if ts_parser_official:
        try:
            tree_official = ts_parser_official.parse(bytes(complex_typescript_code, "utf8"))
            root_node_official = tree_official.root_node
            print(f"✓ Successfully parsed with tree-sitter-language-pack. Root node type: {root_node_official.type}")
            
            print("\nTop-level nodes from tree-sitter-language-pack:")
            for child in root_node_official.children:
                print(f"- {child.type}")
                
            # Count nodes using a recursive function
            def count_nodes(node):
                count = 1  # Count this node
                for child in node.children:
                    count += count_nodes(child)
                return count
                
            node_count = count_nodes(root_node_official)
            print(f"\nTotal nodes in official parser tree: {node_count}")
            
            # Print some detailed information about specific nodes
            print("\nDetailed information about key structures:")
            for child in root_node_official.children:
                if child.type in ["type_alias_declaration", "interface_declaration", "class_declaration", "function_declaration"]:
                    print(f"\n{child.type}:")
                    # Get the text representation
                    start_byte = child.start_byte
                    end_byte = child.end_byte
                    node_text = complex_typescript_code.encode('utf8')[start_byte:end_byte].decode('utf8')
                    # Truncate if too long
                    if len(node_text) > 100:
                        node_text = node_text[:97] + "..."
                    print(f"  Text: {node_text}")
                    # Print first-level children types
                    child_types = [c.type for c in child.children]
                    print(f"  Children types: {child_types}")
            
        except Exception as e:
            print(f"✗ Error with tree-sitter-language-pack: {e}")
    else:
        print("✗ Could not initialize tree-sitter-language-pack TypeScript parser")
except ImportError:
    print("\n✗ tree-sitter-language-pack not installed or couldn't be imported") 