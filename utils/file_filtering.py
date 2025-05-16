import fnmatch

def should_process_file(file_path, include_patterns, exclude_patterns):
    """Determines if a file should be processed based on optimized pattern matching
    
    Args:
        file_path (str): Path to the file (relative or absolute)
        include_patterns (set, optional): Set of glob patterns specifying which files to include
        exclude_patterns (set, optional): Set of glob patterns specifying which files to exclude
        
    Returns:
        bool: True if the file should be processed, False otherwise
    
    Performance optimized by:
    1. Applying exclude patterns first (faster rejection)
    2. Only checking include patterns when not excluded
    3. Using a default rejection policy for unlisted extensions when include patterns exist
    """
    
    # Step 1: Apply exclude patterns first (faster rejection)
    if exclude_patterns:
        for exclude_pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, exclude_pattern):
                return False
            
    # Step 2: Check if file matches include patterns
    if include_patterns:
        for include_pattern in include_patterns:
            if fnmatch.fnmatch(file_path, include_pattern):
                return True
        # If include patterns exist but none match, exclude the file
        return False
    
    # Step 3: Default inclusion when no include patterns are specified
    return True
