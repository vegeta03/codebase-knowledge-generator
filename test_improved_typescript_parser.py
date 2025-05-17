"""
Test script to validate the improved TypeScript parser implementation.
This script tests both TypeScript and TSX parsing capabilities.
"""

import logging
import sys
from utils.typescript_support import get_typescript_parser, get_tsx_parser, test_typescript_parsing, test_tsx_parsing

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Advanced TypeScript code with complex features
complex_typescript_code = """
// Complex TypeScript features
// Type definitions with complex types
type User = {
    id: number;
    name: string;
    isActive: boolean;
    metadata?: Record<string, unknown>;
    roles: Array<{id: number; name: string}>;
};

// Generic interfaces with constraints
interface Repository<T extends {id: number}> {
    getById(id: number): Promise<T | null>;
    getAll(filter?: Partial<T>): Promise<T[]>;
    save(item: T): Promise<void>;
    delete(id: number): Promise<boolean>;
}

// Decorators
@Component({
    selector: 'app-user',
    template: '<user-profile [data]="userData"></user-profile>'
})
class UserComponent implements OnInit, OnDestroy {
    @Input() userId!: number;
    @Output() userChange = new EventEmitter<User>();
    
    private subscription?: Subscription;
    
    constructor(
        private userService: UserService,
        private logger: LoggingService
    ) {}
    
    ngOnInit(): void {
        this.subscription = this.userService.getUser(this.userId)
            .pipe(
                tap(user => this.logger.log(`User loaded: ${user.name}`)),
                catchError(err => {
                    this.logger.error('Failed to load user', err);
                    return EMPTY;
                })
            )
            .subscribe(user => this.userChange.emit(user));
    }
    
    ngOnDestroy(): void {
        this.subscription?.unsubscribe();
    }
    
    @HostListener('click')
    handleClick(): void {
        this.logger.debug('Component clicked');
    }
}

// Advanced type operations
type ExtractKeys<T> = keyof T;
type UserKeys = ExtractKeys<User>;

// Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;

// Recursive types
type NestedArrays<T> = T | NestedArrays<T>[];

// Advanced mapped types
type DeepReadonly<T> = {
    readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// Template literal types
type EventName<T extends string> = `on${Capitalize<T>}`;
type UserEvents = EventName<'load' | 'save' | 'delete'>;

// Namespaces and merging
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

// Declaration merging
interface User {
    login(): Promise<boolean>;
    logout(): void;
}

// Complex async code with type annotations
async function fetchData<T>(url: string, options?: RequestInit): Promise<T> {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return await response.json() as T;
    } catch (error) {
        console.error('Failed to fetch data:', error);
        throw error;
    }
}

// Type guards
function isUser(obj: unknown): obj is User {
    return (
        typeof obj === 'object' &&
        obj !== null &&
        'id' in obj &&
        'name' in obj
    );
}

// Complex generics with constraints and defaults
class DataService<
    T extends {id: number},
    U extends keyof T = keyof T
> {
    async getItemProperty(id: number, prop: U): Promise<T[U]> {
        const item = await this.getItem(id);
        return item[prop];
    }
    
    private async getItem(id: number): Promise<T> {
        // Implementation details
        return fetchData<T>(`/api/items/${id}`);
    }
}
"""

# Advanced TSX code
complex_tsx_code = """
import React, { useState, useEffect, useCallback, PropsWithChildren } from 'react';
import { useSelector, useDispatch } from 'react-redux';

// TypeScript interface for component props
interface UserProfileProps {
    userId: number;
    isEditable?: boolean;
    onUpdate?: (user: User) => void;
}

// Generic component with type parameters
function DataDisplay<T extends Record<string, any>>({ 
    data,
    fields
}: {
    data: T;
    fields: Array<{key: keyof T; label: string}>
}) {
    return (
        <div className="data-display">
            {fields.map(field => (
                <div key={field.key as string} className="field">
                    <span className="label">{field.label}: </span>
                    <span className="value">{String(data[field.key])}</span>
                </div>
            ))}
        </div>
    );
}

// Higher-order component with TypeScript
function withLogging<P extends object>(
    Component: React.ComponentType<P>
): React.FC<P> {
    return (props: P) => {
        useEffect(() => {
            console.log(`Component rendered with props:`, props);
            return () => console.log('Component will unmount');
        }, [props]);
        
        return <Component {...props} />;
    };
}

// Main component with hooks, conditional rendering, and event handling
const UserProfile: React.FC<UserProfileProps> = ({ 
    userId, 
    isEditable = false,
    onUpdate
}) => {
    // State hooks
    const [loading, setLoading] = useState<boolean>(true);
    const [user, setUser] = useState<User | null>(null);
    const [error, setError] = useState<string | null>(null);
    
    // Redux hooks
    const theme = useSelector((state: RootState) => state.theme);
    const dispatch = useDispatch();
    
    // Fetch user data
    const fetchUser = useCallback(async () => {
        try {
            setLoading(true);
            const userData = await fetch(`/api/users/${userId}`)
                .then(res => {
                    if (!res.ok) throw new Error('Failed to fetch user');
                    return res.json();
                });
            
            setUser(userData);
            setError(null);
        } catch (e) {
            setError(e instanceof Error ? e.message : 'An unknown error occurred');
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, [userId]);
    
    useEffect(() => {
        fetchUser();
    }, [fetchUser]);
    
    // Event handlers
    const handleEdit = () => {
        if (user && onUpdate) {
            // Show edit form, etc.
            console.log('Edit mode enabled');
        }
    };
    
    // JSX with conditional rendering
    return (
        <div className={`user-profile ${theme.darkMode ? 'dark' : 'light'}`}>
            {loading ? (
                <div className="loading">Loading user data...</div>
            ) : error ? (
                <div className="error">
                    <p>Error: {error}</p>
                    <button onClick={fetchUser}>Retry</button>
                </div>
            ) : user ? (
                <>
                    <h1>{user.name}</h1>
                    <DataDisplay 
                        data={user} 
                        fields={[
                            { key: 'id', label: 'ID' },
                            { key: 'email', label: 'Email' },
                            { key: 'role', label: 'Role' }
                        ]} 
                    />
                    
                    {isEditable && (
                        <div className="actions">
                            <button 
                                onClick={handleEdit}
                                aria-label="Edit user"
                            >
                                Edit
                            </button>
                        </div>
                    )}
                    
                    {user.isAdmin && (
                        <div className="admin-section">
                            <h2>Admin Controls</h2>
                            {/* Admin-only features */}
                        </div>
                    )}
                </>
            ) : (
                <div>No user found</div>
            )}
        </div>
    );
};

// Export decorated component
export default withLogging(UserProfile);
"""

def test_parser(parser, language, code, language_name):
    if not parser:
        print(f"✗ {language_name} parser not initialized")
        return False
    
    try:
        tree = parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        # Print information about the parse tree
        print(f"✓ Successfully parsed {language_name}: {root_node.type}")
        
        # Count nodes to measure completeness
        node_count = 0
        
        def count_nodes(node):
            nonlocal node_count
            node_count += 1
            for child in node.children:
                count_nodes(child)
        
        count_nodes(root_node)
        print(f"Total nodes in the parse tree: {node_count}")
        
        # Print top-level nodes to verify structure recognition
        print(f"\nTop-level nodes in {language_name} code:")
        for child in root_node.children:
            print(f"- {child.type}")
        
        return True
    except Exception as e:
        print(f"✗ Error parsing {language_name}: {e}")
        return False

def main():
    print("=" * 80)
    print("Testing improved TypeScript parser...")
    print("=" * 80)
    
    # Test TypeScript
    ts_parser, ts_language = get_typescript_parser()
    print("\n1. Testing basic TypeScript parsing:")
    basic_ts_result = test_typescript_parsing()
    print(f"Basic TypeScript parsing: {'✓ Passed' if basic_ts_result else '✗ Failed'}")
    
    print("\n2. Testing complex TypeScript parsing:")
    complex_ts_result = test_parser(ts_parser, ts_language, complex_typescript_code, "TypeScript")
    
    # Test TSX
    print("\n" + "=" * 80)
    print("Testing improved TSX parser...")
    print("=" * 80)
    
    tsx_parser, tsx_language = get_tsx_parser()
    print("\n1. Testing basic TSX parsing:")
    basic_tsx_result = test_tsx_parsing()
    print(f"Basic TSX parsing: {'✓ Passed' if basic_tsx_result else '✗ Failed'}")
    
    print("\n2. Testing complex TSX parsing:")
    complex_tsx_result = test_parser(tsx_parser, tsx_language, complex_tsx_code, "TSX")
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Basic TypeScript: {'✓ Passed' if basic_ts_result else '✗ Failed'}")
    print(f"Complex TypeScript: {'✓ Passed' if complex_ts_result else '✗ Failed'}")
    print(f"Basic TSX: {'✓ Passed' if basic_tsx_result else '✗ Failed'}")
    print(f"Complex TSX: {'✓ Passed' if complex_tsx_result else '✗ Failed'}")
    
    # Exit with success only if all tests pass
    if not all([basic_ts_result, complex_ts_result, basic_tsx_result, complex_tsx_result]):
        sys.exit(1)

if __name__ == "__main__":
    main() 