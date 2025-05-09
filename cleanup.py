#!/usr/bin/env python3
"""
Cleanup Script for Codebase Knowledge Generator

This script deletes:
1. The llm_cache.json file
2. Contents of the logs directory
3. Contents of the output directory (with confirmation)

Usage:
    python cleanup.py
"""

import os
import shutil
import sys
from pathlib import Path


def confirm_action(message):
    """Ask for user confirmation before proceeding with an action."""
    while True:
        response = input(f"{message} (y/n): ").lower().strip()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("Please enter 'y' or 'n'.")


def delete_file(file_path):
    """Delete a file if it exists and print the result."""
    path = Path(file_path)
    if path.exists() and path.is_file():
        try:
            path.unlink()
            print(f"✓ Deleted file: {file_path}")
            return True
        except Exception as e:
            print(f"✗ Error deleting file {file_path}: {e}")
            return False
    else:
        print(f"! File not found: {file_path}")
        return False


def clean_directory(dir_path, ask_confirmation=False):
    """
    Clean a directory by removing all its contents.
    If ask_confirmation is True, ask for user confirmation first.
    Returns True if cleaning was successful or skipped, False otherwise.
    """
    path = Path(dir_path)
    
    # Check if directory exists
    if not path.exists():
        print(f"! Directory not found: {dir_path}")
        return False
    
    # Check if it's actually a directory
    if not path.is_dir():
        print(f"✗ Error: {dir_path} is not a directory")
        return False
    
    # Empty directory check
    if not any(path.iterdir()):
        print(f"! Directory already empty: {dir_path}")
        return True
    
    # Confirmation if required
    if ask_confirmation:
        if not confirm_action(f"Delete all contents of '{dir_path}' directory?"):
            print(f"✓ Skipped cleaning directory: {dir_path}")
            return True
    
    # Clean the directory
    try:
        # Remove all contents but keep the directory
        for item in path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"✓ Cleaned directory: {dir_path}")
        return True
    except Exception as e:
        print(f"✗ Error cleaning directory {dir_path}: {e}")
        return False


def main():
    """Main function to execute the cleanup process."""
    print("\n=== Codebase Knowledge Generator Cleanup ===\n")
    
    # Get the base directory (where the script is located)
    base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Paths to clean
    cache_file = base_dir / "llm_cache.json"
    logs_dir = base_dir / "logs"
    output_dir = base_dir / "output"
    
    # Track success/failure
    success = True
    
    # 1. Delete llm_cache.json
    print("\n> Cleaning LLM cache file:")
    if not delete_file(cache_file):
        success = False
    
    # 2. Clean logs directory
    print("\n> Cleaning logs directory:")
    if not clean_directory(logs_dir):
        success = False
    
    # 3. Clean output directory (with confirmation)
    print("\n> Cleaning output directory:")
    if not clean_directory(output_dir, ask_confirmation=True):
        success = False
    
    # Summary
    print("\n=== Cleanup Summary ===")
    if success:
        print("✓ All cleanup operations completed successfully")
    else:
        print("! Some cleanup operations failed or were skipped")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
