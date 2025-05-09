import dotenv
import os
import argparse
import logging

# Import the keyboard handler to enable ESC key termination
from utils.keyboard_handler import setup_exit_handler

# Apply joblib patch before importing any modules that might use joblib
from joblib_patch import apply_joblib_patches
apply_joblib_patches()

# Import the function that creates the flow
from flow import create_tutorial_flow

dotenv.load_dotenv(override=True)

# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    # Programming languages
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
    "Makefile", "*.yaml", "*.yml",
    
    # Angular/TypeScript/NgRx specific files
    "*.json", "*.html", "*.css", "*.scss", "*.sass", "*.less",
    "*.service.ts", "*.component.ts", "*.module.ts", "*.pipe.ts",
    "*.directive.ts", "*.guard.ts", "*.resolver.ts", "*.interceptor.ts",
    "*.store.ts", "*.effects.ts", "*.reducer.ts", "*.actions.ts", "*.model.ts",
    "*.config.ts", "*.routes.ts", "*.d.ts", "*.environment.ts",
    
    # Nx specific files
    "project.json", "nx.json", "tsconfig*.json",
    
    # Config files
    ".eslintrc*", ".prettierrc*", ".editorconfig", ".angular*",
}

DEFAULT_EXCLUDE_PATTERNS = {
    # Asset directories
    "assets/*", "data/*", "examples/*", "images/*", "public/*", "static/*", "temp/*",
    
    # Documentation and example directories
    "docs/*", "examples/*",
    
    # Virtual environments
    "venv/*", ".venv/*",
    
    # Angular/TypeScript specific test files - ONLY exclude spec files, not entire directories
    "*.spec.ts", "**/test-setup.ts", "**/apps/*-e2e/**", "**/e2e/**",
    
    # Build and output directories
    "dist/*", "build/*", "experimental/*", "deprecated/*", "misc/*",
    "obj/*", "bin/*",
    
    # System directories
    ".git/*", "node_modules/*",
    
    # Log files
    "*.log"
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
        
    # Setup keyboard handler to allow ESC key termination at any time
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
