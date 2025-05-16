# At the beginning of your main script
from joblib_patch import apply_joblib_patches
apply_joblib_patches()
import dotenv
import os
import argparse
import logging

# Import the keyboard handler to enable Ctrl+Q key termination
from utils.keyboard_handler import setup_exit_handler

# Apply joblib patch before importing any modules that might use joblib
from joblib_patch import apply_joblib_patches
apply_joblib_patches()

# Import the function that creates the flow
from flow import create_tutorial_flow

dotenv.load_dotenv(override=True)

# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    # High-value pattern strategy - semantic prioritization
    # 1. Core application source files
    # Language-specific source files
    "**/*.py", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", "**/*.go", 
    "**/*.java", "**/*.rs", "**/*.cs", "**/*.fs", "**/*.kt", "**/*.scala",
    "**/*.c", "**/*.cpp", "**/*.h", "**/*.hpp", 
    
    # 2. Architecture definition files
    # Web/UI frameworks
    "**/*.component.*", "**/*.directive.*", "**/*.guard.*", "**/*.pipe.*", 
    "**/*.service.*", "**/*.module.*", "**/*.interceptor.*", "**/*.resolver.*",
    # State management
    "**/*.store.*", "**/*.reducer.*", "**/*.action.*", "**/*.effect.*", 
    "**/*.selector.*", "**/*.state.*", "**/*.model.*", "**/*.entity.*",
    # API/backend
    "**/*.controller.*", "**/*.repository.*", "**/*.dao.*", "**/*.dto.*", 
    "**/*.service.*", "**/*.middleware.*", "**/*.filter.*", "**/*.route.*", 
    "**/*.handler.*",
    
    # 3. Configuration files (high-value for understanding architecture)
    # Project configuration
    "package.json", "tsconfig*.json", "*.csproj", "*.fsproj", "*.sln", 
    "pom.xml", "build.gradle*", "settings.gradle*", "Cargo.toml", "go.mod",
    "setup.py", "pyproject.toml", "requirements.txt", "poetry.lock",
    "Makefile", "CMakeLists.txt", "Dockerfile*", "docker-compose*.y*ml",
    # Framework configuration
    ".babelrc*", "babel.config.*", "webpack.config.*", "rollup.config.*",
    "next.config.*", "nuxt.config.*", "angular.json", "vue.config.*",
    "nx.json", "project.json", "workspace.json",
    # Environment and application settings
    ".env.example", "**/*.env.example", "application*.yml", "application*.yaml", 
    "application*.properties", "appsettings*.json", "app.config.*",
    "**/*.environment.ts", "**/config/**",
    
    # 4. Definition and declaration files
    "**/*.d.ts", "**/*.proto", "**/*.graphql", "**/*.schema.*", 
    "**/*.avsc", "**/*.thrift",
    
    # 5. Templates and views
    "**/*.html", "**/*.cshtml", "**/*.jsp", "**/*.jspx", "**/*.ejs", 
    "**/*.hbs", "**/*.mustache", "**/*.twig", "**/*.erb", "**/*.razor",
    
    # 6. Style files
    "**/*.css", "**/*.scss", "**/*.sass", "**/*.less", "**/*.styl",
    
    # 7. Documentation
    "README*", "CHANGELOG*", "**/docs/**/*.md",
    
    # 8. Scripts and tooling
    "scripts/*.{js,ts,sh,py}", "tools/**/*.{js,ts,sh,py}"
}


DEFAULT_EXCLUDE_PATTERNS = {
    # Core test pattern strategy - multi-layered approach
    # 1. Directory-based exclusion (broad coverage)
    "**/test/**", "**/tests/**", "**/spec/**", "**/specs/**", 
    "**/__test__/**", "**/__tests__/**", "**/__spec__/**", "**/__specs__/**",
    "**/testing/**", "**/__testing__/**", "**/e2e/**", "**/e2e-tests/**", 
    "**/*-e2e/**", "**/integration-tests/**", "**/it/**", "**/fixtures/**", 
    
    # 2. Framework-specific test directories (thorough coverage)
    # Jest, Mocha, Jasmine
    "**/__mocks__/**", "**/mocks/**", "**/__stubs__/**", "**/stubs/**", 
    "**/__snapshots__/**", "**/__fixtures__/**", "**/__helpers__/**",
    # Common test utility directories
    "**/test-utils/**", "**/test-helpers/**", "**/test-setup/**",
    "**/test-support/**", "**/test-common/**", "**/testdata/**",
    # Testing tools
    "cypress/**", "playwright/**", "**/selenium/**", "**/webdriver/**",
    "**/cucumber/**", "**/protractor/**", "**/puppeteer/**", "**/vitest/**",
    "**/karma/**", "**/jest/**",
    
    # 3. Filename-based exclusion (extension patterns)
    # JavaScript/TypeScript
    "**/*.test.*", "**/*.spec.*", "**/*_test.*", "**/*_spec.*", "**/*-test.*", 
    "**/*-spec.*", "**/*.cy.*", "**/*.e2e.*", "**/*e2e-spec.*", "**/*-it.*",
    # Java
    "**/*Test.java", "**/*Tests.java", "**/*IT.java", "**/*ITCase.java",
    "**/*TestCase.java", "**/Test*.java",
    # Go
    "**/*_test.go",
    # Rust
    "**/*_test.rs",
    # C#
    "**/*Test.cs", "**/*Tests.cs", "**/*.Test/**", "**/*.Tests/**",
    
    # 4. Test configuration files
    "**/jest.config.*", "**/karma.conf.*", "**/karma.config.*", "**/mocha.opts",
    "**/.mocharc.*", "**/cypress.config.*", "**/playwright.config.*",
    "**/vitest.config.*", "**/ava.config.*", "**/jasmine.json",
    "**/protractor.conf.*", "**/testng.xml", "**/junit.xml",
    "**/*.postman_collection.json", "**/test.setup.*", "**/test-setup.*",
    
    # Resource and asset directories (minimal scope)
    "assets/", "static/fonts/**", "static/images/**", "dist/**", "build/**", 
    "out/**", "target/**", ".next/**", ".nuxt/**", "node_modules/**",
    
    # System and IDE directories
    ".git/**", ".github/**", ".idea/**", ".vscode/**", ".vs/**", ".gradle/**",
    
    # Log and cache directories
    "logs/**", "coverage/**", ".nyc_output/**", "reports/**", "**/__pycache__/**",
    ".pytest_cache/**", ".eslintcache", "**/*.log",
    
    # Temporary and experimental
    "**/temp/**", "**/tmp/**", "**/experimental/**", "**/deprecated/**"
}


# --- Main Function ---
def main():
    parser = argparse.ArgumentParser(description="Generate a tutorial for a GitHub codebase or local directory.")

    # Create mutually exclusive group for source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo", help="URL of the public GitHub repository.")
    source_group.add_argument("--dir", help="Path to local directory.")

    parser.add_argument("-n", "--name", help="Project name (optional, derived from repo/directory if omitted).")
    parser.add_argument("-t", "--token", help="GitHub personal access token (optional, reads from GITHUB_TOKEN env var if not provided).")
    parser.add_argument("-o", "--output", default="output", help="Base directory for output (default: ./output).")
    parser.add_argument("-i", "--include", nargs="+", help="Include file patterns (e.g. '*.py' '*.js'). Defaults to common code files if not specified.")
    parser.add_argument("-e", "--exclude", nargs="+", help="Exclude file patterns (e.g. 'tests/*' 'docs/*'). Defaults to test/build directories if not specified.")
    parser.add_argument("-s", "--max-size", type=int, default=100000, help="Maximum file size in bytes (default: 100000, about 100KB).")
    # Add language parameter for multi-language support
    parser.add_argument("--language", default="english", help="Language for the generated tutorial (default: english)")
    # Add use_cache parameter to control LLM caching
    parser.add_argument("--cache", action="store_true", help="Enable LLM response caching (default: caching disabled)")
    # Add verbose flag for additional logging information
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging output")

    args = parser.parse_args()

    # Configure logging based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.INFO

    # Reset logging configuration (in case it was configured by the patch)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Output to console
        ]
    )

    # Set the level for the joblib_patch logger specifically
    logging.getLogger('joblib_patch').setLevel(log_level)

    # Create logger for this module
    logger = logging.getLogger(__name__)

    if args.verbose:
        logger.debug("Verbose logging enabled")
        # Log all arguments (excluding token for security)
        safe_args = vars(args).copy()
        if 'token' in safe_args:
            safe_args['token'] = '***REDACTED***' if safe_args['token'] else None
        logger.debug(f"Command line arguments: {safe_args}")

    # Get GitHub token from argument or environment variable if using repo
    github_token = None
    if args.repo:
        github_token = args.token or os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GitHub token provided. You might hit rate limits for public repositories.")

    # Initialize the shared dictionary with inputs
    shared = {
        "repo_url": args.repo,
        "local_dir": args.dir,
        "project_name": args.name, # Can be None, FetchRepo will derive it
        "github_token": github_token,
        "output_dir": args.output, # Base directory for CombineTutorial output

        # Add include/exclude patterns and max file size
        "include_patterns": set(args.include) if args.include else DEFAULT_INCLUDE_PATTERNS,
        "exclude_patterns": set(args.exclude) if args.exclude else DEFAULT_EXCLUDE_PATTERNS,
        "max_file_size": args.max_size,

        # Add language for multi-language support
        "language": args.language,

        # Add use_cache flag (directly from cache flag)
        "use_cache": args.cache,

        # Outputs will be populated by the nodes
        "files": [],
        "abstractions": [],
        "relationships": {},
        "chapter_order": [],
        "chapters": [],
        "final_output_dir": None
    }

    # Display starting message with repository/directory and language
    print(f"Starting tutorial generation for: {args.repo or args.dir} in {args.language.capitalize()} language")
    print(f"LLM caching: {'Enabled' if args.cache else 'Disabled'}")
    if args.verbose:
        print("Verbose logging: Enabled")
        
    # Setup keyboard handler to allow Ctrl+Q key termination at any time
    keyboard_thread = setup_exit_handler()

    # Create the flow instance
    tutorial_flow = create_tutorial_flow()

    try:
        # Run the flow
        tutorial_flow.run(shared)
    except KeyboardInterrupt:
        logger.info("Process interrupted by keyboard")
        print("\n🛑 Process interrupted. Shutting down...")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
