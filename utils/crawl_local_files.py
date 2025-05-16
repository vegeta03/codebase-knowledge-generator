import os
import fnmatch
import pathspec
import joblib
from tqdm import tqdm
from utils.file_filtering import should_process_file


def crawl_local_files(
    directory,
    include_patterns=None,
    exclude_patterns=None,
    max_file_size=None,
    use_relative_paths=True,
    n_jobs=-1,  # Number of parallel jobs, -1 means using all processors
):
    """
    Crawl files in a local directory with similar interface as crawl_github_files.
    Args:
        directory (str): Path to local directory
        include_patterns (set): File patterns to include (e.g. {"*.py", "*.js"})
        exclude_patterns (set): File patterns to exclude (e.g. {"tests/*"})
        max_file_size (int): Maximum file size in bytes
        use_relative_paths (bool): Whether to use paths relative to directory

    Returns:
        dict: {"files": {filepath: content}}
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")

    files_dict = {}

    # --- Load .gitignore ---
    gitignore_path = os.path.join(directory, ".gitignore")
    gitignore_spec = None
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                gitignore_patterns = f.readlines()
            gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns)
            print(f"Loaded .gitignore patterns from {gitignore_path}")
        except Exception as e:
            print(f"Warning: Could not read or parse .gitignore file {gitignore_path}: {e}")

    all_files = []
    for root, dirs, files in os.walk(directory):
        # Filter directories using .gitignore and exclude_patterns early
        excluded_dirs = set()
        for d in dirs:
            dirpath_rel = os.path.relpath(os.path.join(root, d), directory)

            if gitignore_spec and gitignore_spec.match_file(dirpath_rel):
                excluded_dirs.add(d)
                continue

            if exclude_patterns:
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(dirpath_rel, pattern) or fnmatch.fnmatch(d, pattern):
                        excluded_dirs.add(d)
                        break

        for d in dirs.copy():
            if d in excluded_dirs:
                dirs.remove(d)

        for filename in files:
            filepath = os.path.join(root, filename)
            all_files.append(filepath)

    total_files = len(all_files)
    print(f"Found {total_files} files to process")

    def process_file(filepath):
        """Process a single file and return (path, content) if valid, None otherwise"""
        relpath = os.path.relpath(filepath, directory) if use_relative_paths else filepath

        # --- Exclusion check using gitignore first (highest priority) ---
        if gitignore_spec and gitignore_spec.match_file(relpath):
            return None
            
        # --- Use optimized file filtering utility for pattern matching ---
        if not should_process_file(relpath, include_patterns, exclude_patterns):
            return None  # Skip to next file if not passing pattern matching

        if max_file_size and os.path.getsize(filepath) > max_file_size:
            return None  # Skip large files

        # --- File is being processed ---        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return (relpath, content)
        except Exception as e:
            return None

    # Use joblib to parallelize file processing
    results = joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(process_file)(filepath) for filepath in tqdm(all_files, desc="Processing files"))
    
    # Filter out None results and add to files_dict
    for result in results:
        if result is not None:
            relpath, content = result
            files_dict[relpath] = content

    return {"files": files_dict}


if __name__ == "__main__":
    print("--- Crawling parent directory ('..')  ---")
    files_data = crawl_local_files(
        "..",
        exclude_patterns={
            "*.pyc",
            "__pycache__/*",
            ".venv/*",
            ".git/*",
            "docs/*",
            "output/*",
        },
        n_jobs=4,  # Use 4 parallel jobs as an example
    )
    print(f"Found {len(files_data['files'])} files:")
    for path in files_data["files"]:
        print(f"  {path}")