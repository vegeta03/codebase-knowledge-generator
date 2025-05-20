import os
import re
import json5
from pocketflow import Node, BatchNode
from utils.crawl_github_files import crawl_github_files
from utils.call_llm import call_llm, repair_llm_json
from utils.crawl_local_files import crawl_local_files
from utils.code_chunking import chunk_codebase
from utils.chunk_processor import process_code_for_llm, batch_process_chunks, estimate_model_calls
from prompts import get_identify_abstractions_prompt, get_write_chapter_prompt, get_analyze_relationships_prompt
import logging

# Helper to get content for specific file indices
def get_content_for_indices(files_data, indices):
    content_map = {}
    for i in indices:
        if 0 <= i < len(files_data):
            path, content = files_data[i]
            content_map[f"{i} # {path}"] = (
                content  # Use index + path as key for context
            )
    return content_map

class FetchRepo(Node):
    def prep(self, shared):
        repo_url = shared.get("repo_url")
        local_dir = shared.get("local_dir")
        project_name = shared.get("project_name")

        if not project_name:
            # Basic name derivation from URL or directory
            if repo_url:
                project_name = repo_url.split("/")[-1].replace(".git", "")
            else:
                project_name = os.path.basename(os.path.abspath(local_dir))
            shared["project_name"] = project_name

        # Get file patterns directly from shared
        include_patterns = shared["include_patterns"]
        exclude_patterns = shared["exclude_patterns"]
        max_file_size = shared["max_file_size"]

        return {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "token": shared.get("github_token"),
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "max_file_size": max_file_size,
            "use_relative_paths": True,
        }

    def exec(self, prep_res):
        if prep_res["repo_url"]:
            print(f"Crawling repository: {prep_res['repo_url']}...")
            result = crawl_github_files(
                repo_url=prep_res["repo_url"],
                token=prep_res["token"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"],
            )
        else:
            print(f"Crawling directory: {prep_res['local_dir']}...")
            result = crawl_local_files(
                directory=prep_res["local_dir"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"]
            )

        # Convert dict to list of tuples: [(path, content), ...]
        files_list = list(result.get("files", {}).items())
        if len(files_list) == 0:
            raise(ValueError("Failed to fetch files"))
        print(f"Fetched {len(files_list)} files.")
        return files_list

    def post(self, shared, prep_res, exec_res):
        shared["files"] = exec_res # List of (path, content) tuples

class IdentifyAbstractions(Node):
    def prep(self, shared):
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english") # Get language
        use_cache = shared.get("use_cache", False)  # Get use_cache flag, default to False
        base_dir = shared.get("local_dir") or os.getcwd()  # Get base directory
        
        # Convert files_data to the format expected by the chunking system
        file_paths = []
        file_contents = {}
        file_info = []  # Store tuples of (index, path)
        
        for i, (path, content) in enumerate(files_data):
            file_paths.append(path)
            file_contents[path] = content
            file_info.append((i, path))
        
        # Format file info for the prompt (comment is just a hint for LLM)
        file_listing_for_prompt = "\n".join(
            [f"- {idx} # {path}" for idx, path in file_info]
        )
        
        # Add language instruction and hints only if not English
        language_instruction = ""
        name_lang_hint = ""
        desc_lang_hint = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `name` and `description` for each abstraction in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            # Keep specific hints here as name/description are primary targets
            name_lang_hint = f" (value in {language.capitalize()})"
            desc_lang_hint = f" (value in {language.capitalize()})"
        
        # Use the prompt template from prompts.py
        prompt_template = get_identify_abstractions_prompt(
            project_name=project_name,
            context="{code}",  # Placeholder for code content that will be replaced
            file_listing_for_prompt=file_listing_for_prompt,
            language_instruction=language_instruction,
            name_lang_hint=name_lang_hint,
            desc_lang_hint=desc_lang_hint
        )
        
        # Estimate model usage for logging purposes
        estimation = estimate_model_calls(file_paths, file_contents)
        print(f"Estimated code tokens: {estimation['estimated_code_tokens']}")
        print(f"Estimated chunks: {estimation['estimated_chunks']}")
        print(f"Estimated total tokens: {estimation['total_tokens']}")
        print(f"Using model context length: {estimation['model_context_length']} tokens")
        print(f"Reserving 20% ({int(estimation['model_context_length']*0.2)} tokens) for model response")
        print(f"Max input tokens: {estimation['max_input_tokens']} tokens (80% of model context)")
        
        # Use the hierarchical AST-aware chunking system to prepare prompts
        print("\n=== HIERARCHICAL CHUNKING PROCESS ===")
        prompts = process_code_for_llm(
            base_dir, 
            file_paths, 
            file_contents, 
            prompt_template
        )
        
        # Log detailed chunking information
        print(f"\n=== CHUNKING STATISTICS ===")
        print(f"Total chunks generated: {len(prompts)}")
        total_tokens = 0
        for i, prompt_data in enumerate(prompts):
            chunk_tokens = prompt_data.get('estimated_tokens', 'unknown')
            total_tokens += chunk_tokens if isinstance(chunk_tokens, int) else 0
            print(f"  Chunk {i+1}: {chunk_tokens} tokens, ID: {prompt_data.get('chunk_id', 'unknown')}")
        
        if prompts and 'overlap_percentage' in prompts[0]:
            print(f"Chunk overlap percentage: {prompts[0]['overlap_percentage']}%")
        
        # Calculate average tokens per chunk
        if len(prompts) > 0 and total_tokens > 0:
            print(f"Average tokens per chunk: {total_tokens / len(prompts):.2f}")
        
        print(f"Total files: {len(file_paths)}")
        print(f"Total lines of code: {sum(len(content.splitlines()) for content in file_contents.values())}")
        print("=" * 40)
        
        return (
            prompts,
            file_info,
            len(files_data),
            project_name,
            language,
            use_cache,
        )  # Return all parameters
    
    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing <think></think> tags and other artifacts.
        
        Args:
            response: The raw LLM response to clean
            
        Returns:
            Cleaned response with thinking tags removed
        """
        # Remove <think>...</think> blocks
        import re
        clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove possible trailing/leading whitespace from the cleaning
        clean_response = clean_response.strip()
        
        # If the response is now empty (entire response was inside think tags), 
        # return the original (this shouldn't happen with proper LLM behavior)
        if not clean_response and response:
            print("Warning: Entire response was inside <think> tags. Using original response.")
            return response
            
        return clean_response
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from an LLM response.
        
        Args:
            response: The LLM response, potentially containing JSON code blocks
            
        Returns:
            The extracted JSON as a string
        """
        import re
        
        # First, clean any thinking tags from the response
        response = self._clean_llm_response(response)
        
        # First, try to extract JSON from standard markdown code blocks
        json_pattern = r"```(?:json5?|JSON5?)?(.+?)```"
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            # Return the largest match, which is likely the complete JSON
            return max(matches, key=len).strip()
            
        # If no code blocks found, check if the response is already a JSON array/object
        # Look for response starting with [ or { and ending with ] or }
        if (response.strip().startswith("[") and response.strip().endswith("]")) or \
           (response.strip().startswith("{") and response.strip().endswith("}")):
            return response.strip()
            
        # If we get here, try to extract anything that looks like a JSON array/object
        # This is a more aggressive approach to salvage the response
        start_idx = -1
        end_idx = -1
        
        # Check for array
        if "[" in response and "]" in response:
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            
        # Check for object if no array found
        if start_idx == -1 and "{" in response and "}" in response:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
        if start_idx != -1 and end_idx > start_idx:
            return response[start_idx:end_idx].strip()
                
        # Last resort: return the cleaned response
        return response.strip()

    def _fix_malformed_json(self, json_str: str) -> str:
        """
        Fix common JSON syntax errors that might appear in LLM responses.
        This delegates to the comprehensive repair_llm_json function.
        
        Args:
            json_str: The potentially malformed JSON string
            
        Returns:
            Fixed JSON string that should be parseable
        """
        # Use the comprehensive repair function from call_llm module
        return repair_llm_json(json_str)

    def exec(self, prep_res):
        (
            prompts,
            file_info,
            file_count,
            project_name,
            language,
            use_cache,
        ) = prep_res  # Unpack all parameters
        print(f"\n=== PROCESSING CHUNKS WITH LLM ===")
        print(f"Processing {len(prompts)} code chunks...")

        # Process all chunks and combine results
        print(f"Starting batch processing of {len(prompts)} chunks...")
        processed_results = batch_process_chunks(prompts, call_llm, use_cache=use_cache)
        print(f"Completed batch processing")
        
        # Extract and combine abstractions from all chunks
        combined_abstractions = []
        abstraction_tracker = {}  # Track abstractions by name to avoid duplicates
        
        # Log details for tracking abstraction processing
        print("\n=== ABSTRACTION PROCESSING DETAILS ===")
        total_raw_abstractions = 0
        chunk_abstraction_counts = {}
        
        try:
            for chunk_result in processed_results:
                chunk_id = chunk_result.get('chunk_id', 'unknown')
                
                if "error" in chunk_result:
                    print(f"Warning: Error processing chunk {chunk_id}: {chunk_result['error']}")
                    continue
                    
                # Get the response for this chunk
                result = chunk_result['response']
                
                # Parse the JSON response
                try:
                    # Extract JSON from the response using our helper function
                    abstractions_json = self._extract_json_from_response(result)
                    
                    # Fix common JSON syntax errors in the LLM response
                    abstractions_json = self._fix_malformed_json(abstractions_json)
                    
                    # Parse the JSON with increasing levels of fallback strategies
                    try:
                        # Attempt 1: Parse with json5 (most lenient)
                        chunk_abstractions = json5.loads(abstractions_json)
                    except Exception as json5_error:
                        print(f"Failed to parse with json5: {json5_error}")
                        
                        try:
                            # Attempt 2: Try standard json parser (sometimes works better for certain errors)
                            import json
                            chunk_abstractions = json.loads(abstractions_json)
                            print("Successfully parsed with standard json parser")
                        except Exception as json_error:
                            print(f"Failed with standard json parser: {json_error}")
                            
                            # Attempt 3: More aggressive JSON repair
                            print("Attempting more aggressive JSON repair...")
                            # Print first 100 chars of the problematic JSON for debugging
                            print(f"Problematic JSON (first 100 chars): {abstractions_json[:100]}...")
                            
                            # First try our comprehensive repair function from utils
                            from utils.call_llm import repair_llm_json
                            try:
                                repaired_json = repair_llm_json(abstractions_json)
                                try:
                                    # Try to parse with the repaired JSON
                                    chunk_abstractions = json5.loads(repaired_json)
                                    print(f"Successfully repaired JSON with comprehensive repair function")
                                    # Continue with the repaired abstractions
                                except Exception as final_error:
                                    print(f"FATAL ERROR: All JSON repair attempts failed!")
                                    print(f"Original error: {json5_error}")
                                    print(f"Final error: {final_error}")
                                    print(f"JSON sample: {repaired_json[:200]}...")
                                    print(f"Exiting program because JSON parsing failed completely.")
                                    import sys
                                    sys.exit(1)
                            except Exception as repair_error:
                                print(f"Error with repair function: {repair_error}")
                                print("Falling back to manual repair attempts...")
                            
                            # If we get here, try manual salvage approaches
                            # Try to salvage the JSON by manually reconstructing it
                            chunk_abstractions = []
                            
                            # Attempt to extract objects with a multiline pattern
                            pattern = r'\{\s*"name"\s*:\s*"([^"]*)"\s*,\s*"description"\s*:\s*"([^"]*)"\s*,\s*"file_indices"\s*:\s*\[(.*?)\]\s*\}'
                            matches = re.findall(pattern, abstractions_json, re.DOTALL)
                            
                            if not matches:
                                # Try a more liberal pattern if the first one fails
                                pattern = r'\{\s*"name"\s*:\s*"([^"]*)"\s*,?\s*"description"\s*:\s*"([^"]*)"\s*,?\s*"file_indices"\s*:\s*\[(.*?)\]\s*\}'
                                matches = re.findall(pattern, abstractions_json, re.DOTALL)
                            
                            if not matches:
                                # Even more liberal pattern as last resort
                                pattern = r'"name"\s*:\s*"([^"]*)".*?"description"\s*:\s*"([^"]*)".*?"file_indices"\s*:\s*\[(.*?)\]'
                                matches = re.findall(pattern, abstractions_json, re.DOTALL)
                                
                            # Check if we have nested object in description - special case for LLM outputs
                            if not matches:
                                # Look for JSON objects where description is an object not a string
                                nested_pattern = r'\{\s*"name"\s*:\s*"([^"]*)"\s*,\s*"description"\s*:\s*(\{[^}]*\})\s*,\s*"file_indices"\s*:\s*\[(.*?)\]\s*\}'
                                nested_matches = re.findall(nested_pattern, abstractions_json, re.DOTALL)
                                
                                if nested_matches:
                                    print("Found nested objects in description field - flattening")
                                    for match in nested_matches:
                                        name, desc_obj, indices_str = match
                                        # Convert the nested object to a string representation
                                        # Basic sanitization
                                        desc_str = str(desc_obj).replace('"', '\\"').replace('\n', ' ')
                                        
                                        # Parse the indices
                                        indices = []
                                        # Look for any quoted strings in the indices part
                                        for idx in re.findall(r'"([^"]*)"', indices_str):
                                            indices.append(idx)
                                        
                                        # If we didn't find any quoted indices, try to extract numbers directly
                                        if not indices:
                                            for idx in re.findall(r'\d+', indices_str):
                                                indices.append(idx)
                                                
                                        chunk_abstractions.append({
                                            "name": name,
                                            "description": desc_str,
                                            "file_indices": indices
                                        })
                            
                            for match in matches:
                                name, description, indices_str = match
                                # Parse the indices
                                indices = []
                                # Look for any quoted strings in the indices part
                                for idx in re.findall(r'"([^"]*)"', indices_str):
                                    indices.append(idx)
                                
                                # If we didn't find any quoted indices, try to extract numbers directly
                                if not indices:
                                    for idx in re.findall(r'\d+', indices_str):
                                        indices.append(idx)
                                
                                chunk_abstractions.append({
                                    "name": name,
                                    "description": description,
                                    "file_indices": indices
                                })
                            
                            if not chunk_abstractions:
                                # Last desperate attempt - parse line by line looking for key patterns
                                lines = abstractions_json.split('\n')
                                current_obj = {}
                                file_indices = []
                                
                                for line in lines:
                                    if '"name"' in line:
                                        # Start a new object if we encounter a name
                                        current_obj = {"file_indices": []}
                                        name_match = re.search(r'"name"\s*:\s*"([^"]*)"', line)
                                        if name_match:
                                            current_obj["name"] = name_match.group(1)
                                    
                                    elif '"description"' in line:
                                        # Check for object-style description
                                        if '{' in line and '}' in line:
                                            # Nested object description, flatten it
                                            start_idx = line.find('{')
                                            end_idx = line.rfind('}') + 1
                                            if start_idx >= 0 and end_idx > start_idx:
                                                obj_desc = line[start_idx:end_idx]
                                                # Sanitize
                                                current_obj["description"] = obj_desc.replace('"', '\\"')
                                        else:
                                            # Normal string description
                                            desc_match = re.search(r'"description"\s*:\s*"([^"]*)"', line)
                                            if desc_match:
                                                current_obj["description"] = desc_match.group(1)
                                    
                                    elif '"file_indices"' in line:
                                        # Start collecting file indices
                                        file_indices = []
                                    
                                    elif '#' in line and any(char.isdigit() for char in line):
                                        # This looks like a file index entry
                                        idx_match = re.search(r'"(\d+\s*#[^"]*)"', line)
                                        if idx_match and "file_indices" in current_obj:
                                            current_obj["file_indices"].append(idx_match.group(1))
                                    
                                    elif '}' in line and all(k in current_obj for k in ["name", "description"]):
                                        # End of object, add it if it has required fields
                                        if current_obj and "name" in current_obj and "description" in current_obj:
                                            chunk_abstractions.append(current_obj)
                                            current_obj = {}
                            
                            if chunk_abstractions:
                                print(f"Successfully salvaged {len(chunk_abstractions)} abstractions with aggressive repair")
                            else:
                                # If we've reached here, all attempts to parse the JSON have failed
                                print("FATAL ERROR: Unable to salvage JSON even with aggressive repair")
                                print(f"Problematic chunk ID: {chunk_id}")
                                print(f"Exiting program because JSON repair failed completely.")
                                import sys
                                sys.exit(1)
                    
                    # Log the number of abstractions found in this chunk
                    abstraction_count = len(chunk_abstractions)
                    total_raw_abstractions += abstraction_count
                    chunk_abstraction_counts[chunk_id] = abstraction_count
                    
                    print(f"Chunk {chunk_id}: {abstraction_count} abstractions found")
                    print(f"  Abstractions: {', '.join([a.get('name', 'Unknown') for a in chunk_abstractions])}")
                    
                    # Process each abstraction from this chunk
                    for abstraction in chunk_abstractions:
                        # Ensure required fields are present
                        if not all(k in abstraction for k in ["name", "description", "file_indices"]):
                            print(f"Warning: Skipping incomplete abstraction: {abstraction}")
                            continue
                            
                        # Create a more nuanced abstraction identifier that considers both name and file indices
                        # This helps preserve abstractions with similar names but different scope/purpose
                        abstraction_name = abstraction["name"].strip()
                        file_indices_set = set([str(idx) for idx in abstraction["file_indices"]])
                        
                        # Use first 50 chars of description to help distinguish similar abstractions
                        desc_excerpt = abstraction["description"][:50] if abstraction["description"] else ""
                        
                        # Create a composite key that's still name-focused but considers context
                        norm_name = abstraction_name.lower()
                        
                        # Initialize file_overlap_ratio to 0 for all cases
                        file_overlap_ratio = 0
                        
                        # Check if we have an exact name match
                        if norm_name in abstraction_tracker:
                            existing = abstraction_tracker[norm_name]
                            existing_file_set = set([str(idx) for idx in existing["file_indices"]])
                            
                            # Calculate overlap between file indices
                            if existing_file_set and file_indices_set:
                                intersection = existing_file_set.intersection(file_indices_set)
                                union = existing_file_set.union(file_indices_set)
                                file_overlap_ratio = len(intersection) / len(union)
                            
                            # If high overlap in files and similar name, treat as duplicate
                            # Otherwise, treat as distinct abstraction with similar name
                            if file_overlap_ratio > 0.3:  # Require at least 30% overlap to merge
                                # Merge this as a duplicate
                                print(f"  Duplicate found: \"{abstraction['name']}\" merging with existing abstraction (file overlap: {file_overlap_ratio:.2f})")
                                
                                # Merge file indices (avoid duplicates)
                                old_indices = set(existing["file_indices"])
                                new_indices = set(abstraction["file_indices"])
                                combined_indices = old_indices.union(new_indices)
                                
                                if len(combined_indices) > len(old_indices):
                                    print(f"    Added {len(combined_indices) - len(old_indices)} new file indices")
                                
                                existing["file_indices"] = list(combined_indices)
                                
                                # Take the longer description
                                if len(abstraction["description"]) > len(existing["description"]):
                                    existing["description"] = abstraction["description"]
                                    print(f"    Updated with longer description")
                                continue
                        
                        # Different enough to be a distinct abstraction, or no existing one with this name
                        abstraction_tracker[norm_name] = abstraction
                except Exception as e:
                    print(f"Warning: Failed to parse abstractions from chunk {chunk_id}: {e}")
                    # Log the problematic response for debugging
                    print(f"Response text: {result[:100]}...")
            
            # Convert the deduplicated abstractions to a list
            combined_abstractions = list(abstraction_tracker.values())
            
            # Sort abstractions for consistent output
            combined_abstractions.sort(key=lambda x: x["name"])
            
            # Log deduplication summary
            print("\n=== ABSTRACTION DEDUPLICATION SUMMARY ===")
            print(f"Total raw abstractions across all chunks: {total_raw_abstractions}")
            print(f"Unique abstractions after deduplication: {len(combined_abstractions)}")
            print(f"Removed duplicates: {total_raw_abstractions - len(combined_abstractions)}")
            
            # Check if we found a reasonable number of abstractions
            # Threshold varies by codebase size but larger codebases should have more abstractions
            file_count_threshold = {
                10: 5,     # For tiny codebases (<10 files), expect at least 5 abstractions
                30: 10,    # For small codebases (<30 files), expect at least 10 abstractions 
                100: 15,   # For medium codebases (<100 files), expect at least 15 abstractions
                1000: 20,  # For large codebases (<1000 files), expect at least 20 abstractions
                10000: 30  # For very large codebases, expect at least 30 abstractions
            }
            
            # Find the appropriate threshold for this codebase size
            expected_abstractions = 5  # Default minimum
            for size, threshold in sorted(file_count_threshold.items()):
                if file_count <= size:
                    expected_abstractions = threshold
                    break
                expected_abstractions = threshold  # Use the highest threshold for very large codebases
            
            if len(combined_abstractions) < expected_abstractions:
                print("\n⚠️ WARNING: Found fewer abstractions than expected!")
                print(f"For a codebase with {file_count} files, expected at least {expected_abstractions} abstractions")
                print(f"But only found {len(combined_abstractions)} abstractions")
                print("Possible solutions to consider:")
                print("1. Review and refine the abstraction identification prompt")
                print("2. Adjust chunk size or chunking strategy to better capture cross-cutting concerns")
                print("3. Modify deduplication logic to preserve more distinct abstractions")
                print("4. Consider a multi-pass approach for hierarchical abstraction identification")
            elif len(combined_abstractions) >= expected_abstractions * 2:
                print("\n✅ Excellent! Found a comprehensive set of abstractions")
                print(f"Expected at least {expected_abstractions}, found {len(combined_abstractions)}")
            else:
                print("\n✓ Found an adequate number of abstractions")
                print(f"Expected at least {expected_abstractions}, found {len(combined_abstractions)}")
            
            # List all chunks with their abstraction counts
            print("\nAbstractions per chunk:")
            for chunk_id, count in chunk_abstraction_counts.items():
                print(f"  Chunk {chunk_id}: {count} abstractions")
            
            # Calculate average abstractions per chunk
            if chunk_abstraction_counts:
                avg_abstractions = sum(chunk_abstraction_counts.values()) / len(chunk_abstraction_counts)
                print(f"Average abstractions per chunk: {avg_abstractions:.2f}")
            
            print(f"Successfully extracted {len(combined_abstractions)} unique abstractions across all chunks")
            print("Final abstractions:")
            for i, abstraction in enumerate(combined_abstractions):
                print(f"  {i+1}. {abstraction['name']}")
            print("=" * 40)
            
        except Exception as e:
            print(f"FATAL ERROR: Error processing abstraction results: {e}")
            print("Exiting program because JSON processing failed completely.")
            import sys
            sys.exit(1)
        
        # Validate abstractions structure
        validated_abstractions = []
        for item in combined_abstractions:
            if not isinstance(item, dict) or not all(
                k in item for k in ["name", "description", "file_indices"]
            ):
                print(f"Missing keys in abstraction item: {item}")
                # Skip this abstraction or create a default one
                continue

            if not isinstance(item["name"], str):
                print(f"Name is not a string in item: {item}")
                item["name"] = str(item["name"])

            if not isinstance(item["description"], str):
                print(f"Description is not a string in item: {item}")
                if isinstance(item["description"], list):
                    item["description"] = " ".join(str(part) for part in item["description"])
                else:
                    item["description"] = str(item["description"])

            if not isinstance(item["file_indices"], list):
                print(f"file_indices is not a list in item: {item}")
                if isinstance(item["file_indices"], str):
                    item["file_indices"] = [item["file_indices"]]
                else:
                    item["file_indices"] = ["0 # main file"]

            # Validate indices
            validated_indices = []
            for idx_entry in item["file_indices"]:
                try:
                    if isinstance(idx_entry, int):
                        idx = idx_entry
                    elif isinstance(idx_entry, str) and "#" in idx_entry:
                        idx = int(idx_entry.split("#")[0].strip())
                    else:
                        idx = int(str(idx_entry).strip())

                    if not (0 <= idx < file_count):
                        print(f"Warning: Invalid file index {idx} in item {item['name']}. Max index is {file_count - 1}.")
                        # Use a valid index instead of skipping
                        idx = idx % file_count
                        print(f"Auto-correcting to index {idx}")

                    validated_indices.append(idx)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse index from entry: {idx_entry} in item {item['name']}. Error: {e}")
                    # Use index 0 as fallback
                    validated_indices.append(0)
                    print("Using index 0 as fallback")

            item["files"] = sorted(list(set(validated_indices)))
            # Store only the required fields
            validated_abstractions.append(
                {
                    "name": item["name"],  # Potentially translated name
                    "description": item[
                        "description"
                    ],  # Potentially translated description
                    "files": item["files"],
                }
            )

        print(f"Identified {len(validated_abstractions)} abstractions.")
        return validated_abstractions

    def post(self, shared, prep_res, exec_res):
        # Store the combined abstractions in the shared context
        shared["abstractions"] = exec_res
        
        # Log summary of identified abstractions
        print(f"\n=== FINAL ABSTRACTIONS SUMMARY ===")
        print(f"Identified {len(exec_res)} abstractions:")
        for i, abstraction in enumerate(exec_res):
            print(f"  {i+1}. {abstraction['name']}: {abstraction['description'][:60]}...")
            file_indices = abstraction.get("file_indices", [])
            if file_indices:
                # Convert indices to file paths for better context
                file_paths = []
                for idx in file_indices:
                    if isinstance(idx, (int, str)) and 0 <= int(idx) < len(prep_res[1]):
                        file_paths.append(prep_res[1][int(idx)][1])
                print(f"     Found in {len(file_paths)} files")
        print("=" * 40)
        
        # Return a string action instead of the shared dictionary
        return "default"

class AnalyzeRelationships(Node):
    def prep(self, shared):
        abstractions = shared["abstractions"]  # From IdentifyAbstractions
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", False)  # Get use_cache flag, default to False

        # Get the actual number of abstractions directly
        num_abstractions = len(abstractions)
        
        # Normalize the abstraction data structure to ensure consistent format
        normalized_abstractions = []
        for i, abstr in enumerate(abstractions):
            normalized = {
                "name": abstr.get("name", f"Abstraction {i}"),
                "description": abstr.get("description", "No description provided"),
                "files": []
            }
            
            # Handle different formats of file indices
            if "file_indices" in abstr:
                # Convert all indices to integers where possible
                for idx in abstr["file_indices"]:
                    if isinstance(idx, (int, str)):
                        try:
                            normalized["files"].append(int(idx))
                        except (ValueError, TypeError):
                            # If there's a string that can't be converted to int, skip it
                            pass
            
            normalized_abstractions.append(normalized)
        
        # Replace abstractions with normalized version
        shared["abstractions"] = normalized_abstractions
        abstractions = normalized_abstractions
            
        # Create context with abstraction names, indices, descriptions, and relevant file snippets
        context = "Identified Abstractions:\\n"
        all_relevant_indices = set()
        abstraction_info_for_prompt = []
        
        for i, abstr in enumerate(abstractions):
            # Use 'files' which contains indices directly
            file_indices_str = ", ".join(map(str, abstr["files"]))
            # Abstraction name and description might be translated already
            info_line = f"- Index {i}: {abstr['name']} (Relevant file indices: [{file_indices_str}])\\n  Description: {abstr['description']}"
            context += info_line + "\\n"
            abstraction_info_for_prompt.append(
                f"{i} # {abstr['name']}"
            )
            all_relevant_indices.update(abstr["files"])

        context += "\\nRelevant File Snippets (Referenced by Index and Path):\\n"
        # Get content for relevant files using helper
        relevant_files_content_map = get_content_for_indices(
            files_data, sorted(list(all_relevant_indices))
        )
        # Format file content for context
        file_context_str = "\\n\\n".join(
            f"--- File: {idx_path} ---\\n{content}"
            for idx_path, content in relevant_files_content_map.items()
        )
        context += file_context_str

        return (
            context,
            "\n".join(abstraction_info_for_prompt),
            num_abstractions, # Pass the actual count
            project_name,
            language,
            use_cache,
        )  # Return use_cache

    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing <think></think> tags and other artifacts.
        
        Args:
            response: The raw LLM response to clean
            
        Returns:
            Cleaned response with thinking tags removed
        """
        # Remove <think>...</think> blocks
        import re
        clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove possible trailing/leading whitespace from the cleaning
        clean_response = clean_response.strip()
        
        # If the response is now empty (entire response was inside think tags), 
        # return the original (this shouldn't happen with proper LLM behavior)
        if not clean_response and response:
            print("Warning: Entire response was inside <think> tags. Using original response.")
            return response
            
        return clean_response
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from an LLM response.
        
        Args:
            response: The LLM response, potentially containing JSON code blocks
            
        Returns:
            The extracted JSON as a string
        """
        import re
        
        # First, clean any thinking tags from the response
        response = self._clean_llm_response(response)
        
        # First, try to extract JSON from standard markdown code blocks
        json_pattern = r"```(?:json5?|JSON5?)?(.+?)```"
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            # Return the largest match, which is likely the complete JSON
            return max(matches, key=len).strip()
            
        # If no code blocks found, check if the response is already a JSON array/object
        # Look for response starting with [ or { and ending with ] or }
        if (response.strip().startswith("[") and response.strip().endswith("]")) or \
           (response.strip().startswith("{") and response.strip().endswith("}")):
            return response.strip()
            
        # If we get here, try to extract anything that looks like a JSON array/object
        # This is a more aggressive approach to salvage the response
        start_idx = -1
        end_idx = -1
        
        # Check for array
        if "[" in response and "]" in response:
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            
        # Check for object if no array found
        if start_idx == -1 and "{" in response and "}" in response:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
        if start_idx != -1 and end_idx > start_idx:
            return response[start_idx:end_idx].strip()
                
        # Last resort: return the cleaned response
        return response.strip()

    def _fix_malformed_json(self, json_str: str) -> str:
        """
        Fix common JSON syntax errors that might appear in LLM responses.
        This delegates to the comprehensive repair_llm_json function.
        
        Args:
            json_str: The potentially malformed JSON string
            
        Returns:
            Fixed JSON string that should be parseable
        """
        # Use the comprehensive repair function from call_llm module
        return repair_llm_json(json_str)

    def exec(self, prep_res):
        (
            context,
            abstraction_listing,
            num_abstractions, # Receive the actual count
            project_name,
            language,
            use_cache,
         ) = prep_res  # Unpack use_cache
        print(f"Analyzing relationships using LLM...")

        # Handle the case where there are no abstractions
        if num_abstractions == 0:
            print("Warning: No abstractions found. Creating a default abstraction.")
            # Create a default placeholder abstraction and return it along with relationships
            default_abstraction = {
                "name": "Project Overview",
                "description": f"Overview of the {project_name} project structure and functionality.",
                "file_indices": []
            }
            
            # Will be handled in post method
            return {
                "create_default_abstraction": True,
                "default_abstraction": default_abstraction,
                "summary": f"This is a {language} tutorial for the {project_name} project.",
                "details": [{
                    "from": 0,
                    "to": 0,
                    "label": "Self-reference"
                }]
            }
            
        # Add language instruction and hints only if not English
        language_instruction = ""
        lang_hint = ""
        list_lang_note = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `summary` and relationship `label` fields in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            lang_hint = f" (in {language.capitalize()})"
            list_lang_note = f" (Names might be in {language.capitalize()})"  # Note for the input list

        prompt = get_analyze_relationships_prompt(
            project_name=project_name,
            abstraction_listing=abstraction_listing,
            context=context,
            num_abstractions=num_abstractions,
            language_instruction=language_instruction,
            lang_hint=lang_hint,
            list_lang_note=list_lang_note
        )
        
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # --- Validation ---
        try:
            # Extract and clean JSON5 from response
            json5_str = self._extract_json_from_response(response)
            relationships_data = json5.loads(json5_str)
        except (IndexError, ValueError) as e:
            # Handle malformed JSON5 or missing code blocks
            print(f"Error parsing JSON5 from LLM response: {e}")
            print("Attempting to fix malformed JSON5...")

            # Try to extract JSON5 content even if not properly formatted
            json5_str = self._extract_json_from_response(response)

            # Try to fix common JSON5 formatting issues
            # Fix 1: Multiple strings in summary field
            json5_str = json5_str.replace('  "summary": "', '  "summary": "')
            json5_str = json5_str.replace('",\n  "*', ' *')
            json5_str = json5_str.replace('*",\n', '",\n')

            try:
                relationships_data = json5.loads(json5_str)
            except ValueError as e2:
                print(f"Failed to fix JSON5: {e2}")
                # Create a minimal valid structure as fallback
                relationships_data = {
                    "summary": "Project summary not available due to parsing error",
                    "relationships": []
                }
                print("Using fallback minimal structure")

        if not isinstance(relationships_data, dict) or not all(
            k in relationships_data for k in ["summary", "relationships"]
        ):
            print("LLM output is not a dict or missing keys ('summary', 'relationships')")
            # Create a minimal valid structure
            relationships_data = {
                "summary": relationships_data.get("summary", "Project summary not available"),
                "relationships": relationships_data.get("relationships", [])
            }

        if not isinstance(relationships_data["summary"], str):
            print("Summary is not a string, converting to string")
            # Convert summary to string if it's not already
            if isinstance(relationships_data["summary"], list):
                relationships_data["summary"] = " ".join(str(item) for item in relationships_data["summary"])
            else:
                relationships_data["summary"] = str(relationships_data["summary"])

        if not isinstance(relationships_data["relationships"], list):
            print("Relationships is not a list, converting to empty list")
            relationships_data["relationships"] = []

        # Validate relationships structure
        validated_relationships = []
        for rel in relationships_data["relationships"]:
            # Check for 'label' key
            if not isinstance(rel, dict) or not all(
                k in rel for k in ["from_abstraction", "to_abstraction", "label"]
            ):
                raise ValueError(
                    f"Missing keys (expected from_abstraction, to_abstraction, label) in relationship item: {rel}"
                )
            # Validate 'label' is a string
            if not isinstance(rel["label"], str):
                raise ValueError(f"Relationship label is not a string: {rel}")

            # Validate indices
            try:
                # Extract the index from the from_abstraction field
                from_str = str(rel["from_abstraction"]).strip()
                if "#" in from_str:
                    from_idx = int(from_str.split("#")[0].strip())
                else:
                    from_idx = int(from_str)

                # Extract the index from the to_abstraction field
                to_str = str(rel["to_abstraction"]).strip()
                if "#" in to_str:
                    to_idx = int(to_str.split("#")[0].strip())
                else:
                    to_idx = int(to_str)

                # Check if indices are valid
                if not (0 <= from_idx < num_abstractions):
                    print(f"Warning: Invalid 'from' index {from_idx} in relationship. Max index is {num_abstractions-1}.")
                    # Try to fix by using a valid index
                    if num_abstractions > 0:
                        from_idx = from_idx % num_abstractions
                        print(f"Auto-correcting to index {from_idx}")
                    else:
                        # Handle case where num_abstractions is zero
                        print("No abstractions available. Using default index 0.")
                        from_idx = 0

                if not (0 <= to_idx < num_abstractions):
                    print(f"Warning: Invalid 'to' index {to_idx} in relationship. Max index is {num_abstractions-1}.")
                    # Try to fix by using a valid index
                    if num_abstractions > 0:
                        to_idx = to_idx % num_abstractions
                        print(f"Auto-correcting to index {to_idx}")
                    else:
                        # Handle case where num_abstractions is zero
                        print("No abstractions available. Using default index 0.")
                        to_idx = 0

                # Add the validated relationship
                validated_relationships.append(
                    {
                        "from": from_idx,
                        "to": to_idx,
                        "label": rel["label"],  # Potentially translated label
                    }
                )
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not parse indices from relationship: {rel}. Error: {e}")
                # Instead of failing, try to extract any numbers from the strings
                try:
                    # Try to extract numbers from the strings
                    from_str = str(rel["from_abstraction"])
                    to_str = str(rel["to_abstraction"])

                    # Use regex to find the first number in each string
                    import re
                    from_matches = re.findall(r'\d+', from_str)
                    to_matches = re.findall(r'\d+', to_str)

                    if from_matches and to_matches:
                        if num_abstractions > 0:
                            from_idx = int(from_matches[0]) % num_abstractions
                            to_idx = int(to_matches[0]) % num_abstractions
                        else:
                            from_idx = 0
                            to_idx = 0
                            print("No abstractions available. Using default indices 0, 0.")

                        print(f"Auto-corrected indices: from={from_idx}, to={to_idx}")

                        validated_relationships.append(
                            {
                                "from": from_idx,
                                "to": to_idx,
                                "label": rel["label"],  # Potentially translated label
                            }
                        )
                    else:
                        # If we can't extract numbers, use default indices
                        print(f"Could not extract indices, using defaults: from=0, to=1")
                        validated_relationships.append(
                            {
                                "from": 0,
                                "to": min(1, num_abstractions-1),  # Use 1 or max index if only 1 abstraction
                                "label": rel["label"],  # Potentially translated label
                            }
                        )
                except Exception as e2:
                    print(f"Failed to auto-correct relationship: {e2}")
                    # If all else fails, use default indices
                    validated_relationships.append(
                        {
                            "from": 0,
                            "to": min(1, num_abstractions-1),  # Use 1 or max index if only 1 abstraction
                            "label": rel["label"],  # Potentially translated label
                        }
                    )

        # --- PHASE 1: Identify disconnected abstractions ---
        # Check if all abstractions are involved in at least one relationship
        involved_abstractions = set()
        for rel in validated_relationships:
            involved_abstractions.add(rel["from"])
            involved_abstractions.add(rel["to"])

        # Find abstractions with no relationships
        disconnected_abstractions = [i for i in range(num_abstractions) if i not in involved_abstractions]
        
        # If we have disconnected abstractions, we need a second phase
        if disconnected_abstractions:
            print(f"\n=== PHASE 2: GENERATING MEANINGFUL RELATIONSHIPS FOR {len(disconnected_abstractions)} DISCONNECTED ABSTRACTIONS ===")
            
            # --- PHASE 2: Generate meaningful relationships for disconnected abstractions ---
            # Extract abstraction details for disconnected and connected abstractions
            from prompts import get_abstraction_relationship_completion_prompt
            
            # Convert abstraction listing to a dictionary for easier lookup
            abstraction_dict = {}
            for line in abstraction_listing.split('\n'):
                if line.strip():
                    parts = line.strip().split('#', 1)
                    if len(parts) == 2:
                        idx = parts[0].strip()
                        name = parts[1].strip()
                        abstraction_dict[idx] = name
            
            # Get names for disconnected abstractions
            disconnected_names = []
            for idx in disconnected_abstractions:
                name = abstraction_dict.get(str(idx), f"Abstraction {idx}")
                disconnected_names.append(f"{idx} # {name}")
            
            # Get existing relationships as context
            existing_relationships = []
            for rel in validated_relationships:
                from_idx = rel["from"]
                to_idx = rel["to"]
                from_name = abstraction_dict.get(str(from_idx), f"Abstraction {from_idx}")
                to_name = abstraction_dict.get(str(to_idx), f"Abstraction {to_idx}")
                existing_relationships.append(f"- {from_idx} # {from_name} → {to_idx} # {to_name}: {rel['label']}")
            
            # Build a completion prompt for each disconnected abstraction
            completion_prompt = f"""
Based on the abstractions in the project and the existing relationships already identified, 
please generate SPECIFIC and LOGICAL relationships for these disconnected abstractions.

For each disconnected abstraction, create at least one relationship connecting it to another abstraction.
The relationship must be conceptually valid and reflect a real architectural connection.

Disconnected abstractions:
{chr(10).join(f"- {name}" for name in disconnected_names)}

Context from other abstractions:
{abstraction_listing}

Existing relationships:
{chr(10).join(existing_relationships)}

IMPORTANT:
1. Create only meaningful, logical relationships based on the likely roles of these abstractions
2. Each relationship must connect a disconnected abstraction to EITHER another disconnected abstraction OR an already-connected one
3. Use technology-agnostic concepts (dependence, composition, uses, specializes, etc.)
4. Be specific about the relationship type, not just general "relates to"

Output format should be a JSON array of objects with:
- from_abstraction: The source abstraction index and name
- to_abstraction: The target abstraction index and name  
- label: A descriptive relationship label

```json
[
  {{
    "from_abstraction": "{disconnected_abstractions[0]} # {abstraction_dict.get(str(disconnected_abstractions[0]), 'Disconnected Abstraction')}",
    "to_abstraction": "1 # {abstraction_dict.get('1', 'Some Connected Abstraction')}",
    "label": "Depends on for configuration"
  }},
  // Add relationships for all disconnected abstractions
]
```
"""
            
            # Call LLM to generate meaningful relationships for disconnected abstractions
            completion_response = call_llm(completion_prompt, use_cache=False)  # Never use cache for this
            
            # Parse the completion response
            try:
                # Extract JSON from the response using our helper function
                completion_json = self._extract_json_from_response(completion_response)
                
                # Fix common JSON syntax errors in the LLM response
                completion_json = self._fix_malformed_json(completion_json)
                
                # Parse the JSON
                new_relationships = json5.loads(completion_json)
                
                # Validate and add new relationships
                for rel in new_relationships:
                    try:
                        # Extract indices
                        from_str = str(rel["from_abstraction"]).strip()
                        if "#" in from_str:
                            from_idx = int(from_str.split("#")[0].strip())
                        else:
                            from_idx = int(from_str)
                            
                        to_str = str(rel["to_abstraction"]).strip()
                        if "#" in to_str:
                            to_idx = int(to_str.split("#")[0].strip())
                        else:
                            to_idx = int(to_str)
                        
                        # Ensure indices are valid
                        if 0 <= from_idx < num_abstractions and 0 <= to_idx < num_abstractions:
                            # Add the new relationship
                            validated_relationships.append({
                                "from": from_idx,
                                "to": to_idx,
                                "label": rel["label"]
                            })
                            
                            # Update the set of involved abstractions
                            involved_abstractions.add(from_idx)
                            involved_abstractions.add(to_idx)
                            
                            print(f"Added relationship: {from_idx} ({abstraction_dict.get(str(from_idx), '')}) → {to_idx} ({abstraction_dict.get(str(to_idx), '')}): {rel['label']}")
                        else:
                            print(f"Warning: Invalid indices in generated relationship: {from_idx}, {to_idx}")
                    except (ValueError, KeyError, TypeError) as e:
                        print(f"Warning: Error processing generated relationship: {rel}. Error: {e}")
            except Exception as e:
                print(f"Warning: Failed to process generated relationships: {e}")
                # Proceed with fallback relationships

        # --- PHASE 3: Final check and fallback for any remaining disconnected abstractions ---
        # Recheck for any abstractions still disconnected
        disconnected_abstractions = [i for i in range(num_abstractions) if i not in involved_abstractions]
        
        # If we still have disconnected abstractions, add simple fallback relationships
        if disconnected_abstractions:
            print(f"\n=== PHASE 3: ADDING FALLBACK RELATIONSHIPS FOR {len(disconnected_abstractions)} REMAINING DISCONNECTED ABSTRACTIONS ===")
            
            # Find a suitable connection target - prefer a central/common abstraction if possible
            connection_counts = {}
            for rel in validated_relationships:
                connection_counts[rel["from"]] = connection_counts.get(rel["from"], 0) + 1
                connection_counts[rel["to"]] = connection_counts.get(rel["to"], 0) + 1
            
            # Find the most connected abstraction to use as a hub (if there are any relationships)
            hub_abstraction = None
            if connection_counts:
                hub_abstraction = max(connection_counts, key=connection_counts.get)
            
            for i in disconnected_abstractions:
                # If we have a hub, connect to it; otherwise connect to the next abstraction
                if hub_abstraction is not None:
                    to_idx = hub_abstraction
                    connection_type = "Integrates with"
                else:
                    to_idx = (i + 1) % num_abstractions
                    connection_type = "Relates to" if i != to_idx else "Self-manages"
                
                print(f"Warning: Abstraction {i} still disconnected. Adding fallback relationship to {to_idx}.")
                validated_relationships.append({
                    "from": i,
                    "to": to_idx,
                    "label": connection_type
                })

        print("Generated project summary and relationship details.")
        return {
            "summary": relationships_data["summary"],  # Potentially translated summary
            "details": validated_relationships,  # Store validated, index-based relationships with potentially translated labels
        }

    def post(self, shared, prep_res, exec_res):
        # Structure is now {"summary": str, "details": [{"from": int, "to": int, "label": str}]}
        # Summary and label might be translated

        # Handle the case where we created a default abstraction
        if exec_res.get("create_default_abstraction", False):
            shared["abstractions"] = [exec_res["default_abstraction"]]
            # Remove the special flags we added
            clean_res = {
                "summary": exec_res["summary"],
                "details": exec_res["details"]
            }
            shared["relationships"] = clean_res
        else:
            shared["relationships"] = exec_res
            
        return "default"

class OrderChapters(Node):
    def prep(self, shared):
        abstractions = shared["abstractions"]  # Name/description might be translated
        relationships = shared["relationships"]  # Summary/label might be translated
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", False)  # Get use_cache flag, default to True

        # Prepare context for the LLM
        abstraction_info_for_prompt = []
        for i, a in enumerate(abstractions):
            abstraction_info_for_prompt.append(
                f"- {i} # {a['name']}"
            )  # Use potentially translated name
        abstraction_listing = "\n".join(abstraction_info_for_prompt)

        # Use potentially translated summary and labels
        summary_note = ""
        if language.lower() != "english":
            summary_note = (
                f" (Note: Project Summary might be in {language.capitalize()})"
            )

        context = f"Project Summary{summary_note}:\n{relationships['summary']}\n\n"
        context += "Relationships (Indices refer to abstractions above):\n"
        for rel in relationships["details"]:
            from_name = abstractions[rel["from"]]["name"]
            to_name = abstractions[rel["to"]]["name"]
            # Use potentially translated 'label'
            context += f"- From {rel['from']} ({from_name}) to {rel['to']} ({to_name}): {rel['label']}\n"  # Label might be translated

        list_lang_note = ""
        if language.lower() != "english":
            list_lang_note = f" (Names might be in {language.capitalize()})"

        return (
            abstraction_listing,
            context,
            len(abstractions),
            project_name,
            list_lang_note,
            use_cache,
        )  # Return use_cache

    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing <think></think> tags and other artifacts.
        
        Args:
            response: The raw LLM response to clean
            
        Returns:
            Cleaned response with thinking tags removed
        """
        # Remove <think>...</think> blocks
        import re
        clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove possible trailing/leading whitespace from the cleaning
        clean_response = clean_response.strip()
        
        # If the response is now empty (entire response was inside think tags), 
        # return the original (this shouldn't happen with proper LLM behavior)
        if not clean_response and response:
            print("Warning: Entire response was inside <think> tags. Using original response.")
            return response
            
        return clean_response
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from an LLM response.
        
        Args:
            response: The LLM response, potentially containing JSON code blocks
            
        Returns:
            The extracted JSON as a string
        """
        import re
        
        # First, clean any thinking tags from the response
        response = self._clean_llm_response(response)
        
        # First, try to extract JSON from standard markdown code blocks
        json_pattern = r"```(?:json5?|JSON5?)?(.+?)```"
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            # Return the largest match, which is likely the complete JSON
            return max(matches, key=len).strip()
            
        # If no code blocks found, check if the response is already a JSON array/object
        # Look for response starting with [ or { and ending with ] or }
        if (response.strip().startswith("[") and response.strip().endswith("]")) or \
           (response.strip().startswith("{") and response.strip().endswith("}")):
            return response.strip()
            
        # If we get here, try to extract anything that looks like a JSON array/object
        # This is a more aggressive approach to salvage the response
        start_idx = -1
        end_idx = -1
        
        # Check for array
        if "[" in response and "]" in response:
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            
        # Check for object if no array found
        if start_idx == -1 and "{" in response and "}" in response:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
        if start_idx != -1 and end_idx > start_idx:
            return response[start_idx:end_idx].strip()
                
        # Last resort: return the cleaned response
        return response.strip()

    def exec(self, prep_res):
        (
            abstraction_listing,
            context,
            num_abstractions,
            project_name,
            list_lang_note,
            use_cache,
        ) = prep_res  # Unpack use_cache
        print("Determining chapter order using LLM...")
        # No language variation needed here in prompt instructions, just ordering based on structure
        # The input names might be translated, hence the note.
        prompt = f"""
Given the following project abstractions and their relationships for the project ```` {project_name} ````:

Abstractions (Index # Name){list_lang_note}:
{abstraction_listing}

Context about relationships and project summary:
{context}

If you are going to make a tutorial for ```` {project_name} ````, what is the best order to explain these abstractions, from first to last?
Ideally, first explain those that are the most important or foundational, perhaps user-facing concepts or entry points. Then move to more detailed, lower-level implementation details or supporting concepts.

Output the ordered list of abstraction indices, including the name in a comment for clarity. Use the format `idx # AbstractionName`.

```json5
[
  "2 # FoundationalConcept",
  "0 # CoreClassA",
  "1 # CoreClassB (uses CoreClassA)",
  // ...
]
```

Now, provide the JSON5 output:
"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # --- Validation ---
        try:
            # Extract JSON from the response using our helper function
            json5_str = self._extract_json_from_response(response)
            ordered_indices_raw = json5.loads(json5_str)
        except ValueError as e:
            print(f"Error parsing JSON5 from LLM response: {e}")
            print("Attempting to fix malformed JSON5...")

            # Try to clean up common JSON5 formatting issues
            # Remove comments
            json5_str = re.sub(r'//.*', '', json5_str)
            # Fix trailing commas
            json5_str = re.sub(r',\s*]', ']', json5_str)

            try:
                ordered_indices_raw = json5.loads(json5_str)
            except ValueError as e2:
                print(f"Failed to fix JSON5: {e2}")
                # Create a minimal valid structure as fallback
                print("Using fallback ordering based on abstraction indices")
                ordered_indices_raw = [str(i) for i in range(num_abstractions)]

        if not isinstance(ordered_indices_raw, list):
            print("LLM output is not a list, converting to list")
            if isinstance(ordered_indices_raw, dict):
                # Try to extract a list from the dict if possible
                for key, value in ordered_indices_raw.items():
                    if isinstance(value, list):
                        ordered_indices_raw = value
                        break
                else:
                    # If no list found in dict values, create default list
                    ordered_indices_raw = [str(i) for i in range(num_abstractions)]
            else:
                ordered_indices_raw = [str(i) for i in range(num_abstractions)]

        # Process the raw indices, handling duplicates and invalid entries
        ordered_indices = []
        seen_indices = set()

        # First pass: collect valid indices
        for entry in ordered_indices_raw:
            try:
                if isinstance(entry, int):
                    idx = entry
                elif isinstance(entry, str) and "#" in entry:
                    idx = int(entry.split("#")[0].strip())
                else:
                    idx = int(str(entry).strip())

                # Validate index range
                if not (0 <= idx < num_abstractions):
                    print(f"Warning: Invalid index {idx} in ordered list. Max index is {num_abstractions-1}.")
                    # Use modulo to bring into valid range
                    idx = idx % num_abstractions
                    print(f"Auto-correcting to index {idx}")

                # Handle duplicates by skipping them
                if idx in seen_indices:
                    print(f"Warning: Duplicate index {idx} found in ordered list. Skipping duplicate.")
                    continue

                ordered_indices.append(idx)
                seen_indices.add(idx)
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not parse index from ordered list entry: {entry}. Error: {e}")
                # Continue instead of raising an exception
                continue

        # Second pass: add any missing indices
        missing_indices = set(range(num_abstractions)) - seen_indices
        if missing_indices:
            print(f"Warning: Missing indices in ordered list: {missing_indices}")
            print("Adding missing indices to the end of the list")
            ordered_indices.extend(sorted(missing_indices))

        # Ensure we have the right number of indices
        if len(ordered_indices) != num_abstractions:
            print(f"Warning: Ordered list length ({len(ordered_indices)}) does not match number of abstractions ({num_abstractions}).")
            # If we somehow still don't have the right number, use a fallback ordering
            if len(ordered_indices) < num_abstractions:
                # Add any indices that are still missing
                still_missing = set(range(num_abstractions)) - set(ordered_indices)
                ordered_indices.extend(sorted(still_missing))
            elif len(ordered_indices) > num_abstractions:
                # Truncate to the right number
                ordered_indices = ordered_indices[:num_abstractions]

        print(f"Determined chapter order (indices): {ordered_indices}")
        return ordered_indices  # Return the list of indices

    def post(self, shared, prep_res, exec_res):
        # exec_res is already the list of ordered indices
        shared["chapter_order"] = exec_res  # List of indices
        return "default"


class WriteChapters(BatchNode):
    def prep(self, shared):
        chapter_order = shared["chapter_order"]  # List of indices
        abstractions = shared[
            "abstractions"
        ]  # List of {"name": str, "description": str, "files": [int]}
        files_data = shared["files"]  # List of (path, content) tuples
        project_name = shared["project_name"]
        language = shared.get("language", "english")
        use_cache = shared.get("use_cache", False)  # Get use_cache flag, default to True

        # Get already written chapters to provide context
        # We store them temporarily during the batch run, not in shared memory yet
        # The 'previous_chapters_summary' will be built progressively in the exec context
        self.chapters_written_so_far = (
            []
        )  # Use instance variable for temporary storage across exec calls

        # Create a complete list of all chapters
        all_chapters = []
        chapter_filenames = {}  # Store chapter filename mapping for linking
        for i, abstraction_index in enumerate(chapter_order):
            if 0 <= abstraction_index < len(abstractions):
                chapter_num = i + 1
                chapter_name = abstractions[abstraction_index][
                    "name"
                ]  # Potentially translated name
                # Create safe filename (from potentially translated name)
                safe_name = "".join(
                    c if c.isalnum() else "_" for c in chapter_name
                ).lower()
                filename = f"{i+1:02d}_{safe_name}.md"
                # Format with link (using potentially translated name)
                all_chapters.append(f"{chapter_num}. [{chapter_name}]({filename})")
                # Store mapping of chapter index to filename for linking
                chapter_filenames[abstraction_index] = {
                    "num": chapter_num,
                    "name": chapter_name,
                    "filename": filename,
                }

        # Create a formatted string with all chapters
        full_chapter_listing = "\n".join(all_chapters)

        items_to_process = []
        for i, abstraction_index in enumerate(chapter_order):
            if 0 <= abstraction_index < len(abstractions):
                abstraction_details = abstractions[
                    abstraction_index
                ]  # Contains potentially translated name/desc
                # Use 'files' (list of indices) directly
                related_file_indices = abstraction_details.get("files", [])
                # Get content using helper, passing indices
                related_files_content_map = get_content_for_indices(
                    files_data, related_file_indices
                )

                # Get previous chapter info for transitions (uses potentially translated name)
                prev_chapter = None
                if i > 0:
                    prev_idx = chapter_order[i - 1]
                    prev_chapter = chapter_filenames[prev_idx]

                # Get next chapter info for transitions (uses potentially translated name)
                next_chapter = None
                if i < len(chapter_order) - 1:
                    next_idx = chapter_order[i + 1]
                    next_chapter = chapter_filenames[next_idx]

                items_to_process.append(
                    {
                        "chapter_num": i + 1,
                        "abstraction_index": abstraction_index,
                        "abstraction_details": abstraction_details,  # Has potentially translated name/desc
                        "related_files_content_map": related_files_content_map,
                        "project_name": shared["project_name"],  # Add project name
                        "full_chapter_listing": full_chapter_listing,  # Add the full chapter listing (uses potentially translated names)
                        "chapter_filenames": chapter_filenames,  # Add chapter filenames mapping (uses potentially translated names)
                        "prev_chapter": prev_chapter,  # Add previous chapter info (uses potentially translated name)
                        "next_chapter": next_chapter,  # Add next chapter info (uses potentially translated name)
                        "language": language,  # Add language for multi-language support
                        "use_cache": use_cache, # Pass use_cache flag
                        # previous_chapters_summary will be added dynamically in exec
                    }
                )
            else:
                print(
                    f"Warning: Invalid abstraction index {abstraction_index} in chapter_order. Skipping."
                )

        print(f"Preparing to write {len(items_to_process)} chapters...")
        return items_to_process  # Iterable for BatchNode

    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing <think></think> tags and other artifacts.
        
        Args:
            response: The raw LLM response to clean
            
        Returns:
            Cleaned response with thinking tags removed
        """
        # Remove <think>...</think> blocks
        import re
        clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove possible trailing/leading whitespace from the cleaning
        clean_response = clean_response.strip()
        
        # If the response is now empty (entire response was inside think tags), 
        # return the original (this shouldn't happen with proper LLM behavior)
        if not clean_response and response:
            print("Warning: Entire response was inside <think> tags. Using original response.")
            return response
            
        return clean_response

    def exec(self, item):
        # This runs for each item prepared above
        abstraction_name = item["abstraction_details"][
            "name"
        ]  # Potentially translated name
        abstraction_description = item["abstraction_details"][
            "description"
        ]  # Potentially translated description
        chapter_num = item["chapter_num"]
        project_name = item.get("project_name")
        language = item.get("language", "english")
        use_cache = item.get("use_cache", False) # Read use_cache from item
        print(f"Writing chapter {chapter_num} for: {abstraction_name} using LLM...")

        # Prepare file context string from the map
        file_context_str = "\n\n".join(
            f"--- File: {idx_path.split('# ')[1] if '# ' in idx_path else idx_path} ---\n{content}"
            for idx_path, content in item["related_files_content_map"].items()
        )

        # Get summary of chapters written *before* this one
        # Use the temporary instance variable
        previous_chapters_summary = "\n---\n".join(self.chapters_written_so_far)

        # Add language instruction and context notes only if not English
        language_instruction = ""
        concept_details_note = ""
        structure_note = ""
        prev_summary_note = ""
        instruction_lang_note = ""
        mermaid_lang_note = ""
        code_comment_note = ""
        link_lang_note = ""
        tone_note = ""
        if language.lower() != "english":
            lang_cap = language.capitalize()
            language_instruction = f"IMPORTANT: Write this ENTIRE tutorial chapter in **{lang_cap}**. Some input context (like concept name, description, chapter list, previous summary) might already be in {lang_cap}, but you MUST translate ALL other generated content including explanations, examples, technical terms, and potentially code comments into {lang_cap}. DO NOT use English anywhere except in code syntax, required proper nouns, or when specified. The entire output MUST be in {lang_cap}.\n\n"
            concept_details_note = f" (Note: Provided in {lang_cap})"
            structure_note = f" (Note: Chapter names might be in {lang_cap})"
            prev_summary_note = f" (Note: This summary might be in {lang_cap})"
            instruction_lang_note = f" (in {lang_cap})"
            mermaid_lang_note = f" (Use {lang_cap} for labels/text if appropriate)"
            code_comment_note = f" (Translate to {lang_cap} if possible, otherwise keep minimal English for clarity)"
            link_lang_note = (
                f" (Use the {lang_cap} chapter title from the structure above)"
            )
            tone_note = f" (appropriate for {lang_cap} readers)"

        # Use the comprehensive prompt template from prompts.py instead of the hardcoded one
        prompt = get_write_chapter_prompt(
            project_name=project_name,
            chapter_num=chapter_num,
            abstraction_name=abstraction_name,
            abstraction_description=abstraction_description,
            full_chapter_listing=item["full_chapter_listing"],
            file_context_str=file_context_str if file_context_str else "No specific code snippets provided for this abstraction.",
            previous_chapters_summary=previous_chapters_summary if previous_chapters_summary else "This is the first chapter.",
            language_instruction=language_instruction,
            concept_details_note=concept_details_note,
            structure_note=structure_note,
            prev_summary_note=prev_summary_note,
            instruction_lang_note=instruction_lang_note,
            mermaid_lang_note=mermaid_lang_note,
            code_comment_note=code_comment_note,
            link_lang_note=link_lang_note,
            tone_note=tone_note,
            language=language
        )

        chapter_content = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # Clean the chapter content to remove <think></think> blocks
        chapter_content = self._clean_llm_response(chapter_content)
        
        # Basic validation/cleanup
        actual_heading = f"# Chapter {chapter_num}: {abstraction_name}"  # Use potentially translated name
        if not chapter_content.strip().startswith(f"# Chapter {chapter_num}"):
            # Add heading if missing or incorrect, trying to preserve content
            lines = chapter_content.strip().split("\n")
            if lines and lines[0].strip().startswith(
                "#"
            ):  # If there's some heading, replace it
                lines[0] = actual_heading
                chapter_content = "\n".join(lines)
            else:  # Otherwise, prepend it
                chapter_content = f"{actual_heading}\n\n{chapter_content}"

        # Add the generated content to our temporary list for the next iteration's context
        self.chapters_written_so_far.append(chapter_content)

        return chapter_content # Return the Markdown string (potentially translated)

    def post(self, shared, prep_res, exec_res_list):
        # exec_res_list contains the generated Markdown for each chapter, in order
        shared["chapters"] = exec_res_list
        # Clean up the temporary instance variable
        del self.chapters_written_so_far
        print(f"Finished writing {len(exec_res_list)} chapters.")
        return "default"

    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing <think></think> tags and other artifacts.
        
        Args:
            response: The raw LLM response to clean
            
        Returns:
            Cleaned response with thinking tags removed
        """
        # Remove <think>...</think> blocks
        import re
        clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove possible trailing/leading whitespace from the cleaning
        clean_response = clean_response.strip()
        
        # If the response is now empty (entire response was inside think tags), 
        # return the original (this shouldn't happen with proper LLM behavior)
        if not clean_response and response:
            print("Warning: Entire response was inside <think> tags. Using original response.")
            return response
            
        return clean_response

    def exec_fallback(self, item, exc):
        """
        Provide a fallback chapter when the LLM API fails after all retries.
        
        Args:
            item: The preparation result containing chapter information
            exc: The exception that occurred
            
        Returns:
            A placeholder chapter as fallback content
        """
        print(f"API call failed after all retries. Creating fallback chapter. Error: {exc}")
        logger = logging.getLogger("llm_logger")
        logger.error(f"Creating fallback chapter due to API failure: {exc}")
        
        # Extract necessary information to create a basic placeholder chapter
        chapter_num = item["chapter_num"]
        abstraction_name = item["abstraction_details"]["name"]
        abstraction_description = item["abstraction_details"]["description"]
        
        # Get next chapter info for link
        next_chapter_link = ""
        if item.get("next_chapter"):
            next_name = item["next_chapter"]["name"]
            next_filename = item["next_chapter"]["filename"]
            next_chapter_link = f"\n\nNext: [{next_name}]({next_filename})"
        
        # Create a simple fallback chapter with basic structure
        fallback_chapter = f"""# Chapter {chapter_num}: {abstraction_name}

> **Note:** This is a placeholder chapter. The full content couldn't be generated due to a temporary service interruption. Please try regenerating the tutorial later.

## Overview

{abstraction_description}

## Basic Implementation

This section would typically contain implementation details for the {abstraction_name} abstraction.

## Key Concepts

- Concept 1: Would explain core functionality
- Concept 2: Would detail design patterns used
- Concept 3: Would cover architectural considerations

## Usage Examples

Examples of how to use this abstraction would be included here.

## Conclusion

The {abstraction_name} abstraction is an important part of the system architecture. It provides essential functionality and integrates with other components.{next_chapter_link}

---

Generated by [AI Codebase Knowledge Generator](https://github.com/vegeta03/codebase-knowledge-generator)
"""
        
        print(f"Created fallback chapter for Chapter {chapter_num}: {abstraction_name}")
        return fallback_chapter

class CombineTutorial(Node):
    def prep(self, shared):
        project_name = shared["project_name"]
        output_base_dir = shared.get("output_dir", "output") # Default output dir
        output_path = os.path.join(output_base_dir, project_name)
        repo_url = shared.get("repo_url")  # Get the repository URL
        # language = shared.get("language", "english") # No longer needed for fixed strings

        # Get potentially translated data
        relationships_data = shared[
            "relationships"
        ]  # {"summary": str, "details": [{"from": int, "to": int, "label": str}]} -> summary/label potentially translated
        chapter_order = shared["chapter_order"]  # indices
        abstractions = shared[
            "abstractions"
        ]  # list of dicts -> name/description potentially translated
        chapters_content = shared[
            "chapters"
        ]  # list of strings -> content potentially translated

        # --- Generate Mermaid Diagram ---
        mermaid_lines = ["flowchart TD"]
        # Add nodes for each abstraction using potentially translated names
        for i, abstr in enumerate(abstractions):
            node_id = f"A{i}"
            # Use potentially translated name, sanitize for Mermaid ID and label
            sanitized_name = abstr["name"].replace('"', "")
            node_label = sanitized_name  # Using sanitized name only
            mermaid_lines.append(
                f'    {node_id}["{node_label}"]'
            )  # Node label uses potentially translated name
        # Add edges for relationships using potentially translated labels
        for rel in relationships_data["details"]:
            from_node_id = f"A{rel['from']}"
            to_node_id = f"A{rel['to']}"
            # Use potentially translated label, sanitize
            edge_label = (
                rel["label"].replace('"', "").replace("\n", " ")
            )  # Basic sanitization
            max_label_len = 30
            if len(edge_label) > max_label_len:
                edge_label = edge_label[: max_label_len - 3] + "..."
            mermaid_lines.append(
                f'    {from_node_id} -- "{edge_label}" --> {to_node_id}'
            )  # Edge label uses potentially translated label

        mermaid_diagram = "\n".join(mermaid_lines)
        # --- End Mermaid ---

        # --- Prepare index.md content ---
        index_content = f"# Tutorial: {project_name}\n\n"
        index_content += f"{relationships_data['summary']}\n\n" # Use the potentially translated summary directly
        # Keep fixed strings in English
        index_content += f"**Source Repository:** [{repo_url}]({repo_url})\n\n"

        # Add Mermaid diagram for relationships (diagram itself uses potentially translated names/labels)
        index_content += "```mermaid\n"
        index_content += mermaid_diagram + "\n"
        index_content += "```\n\n"

        # Keep fixed strings in English
        index_content += f"## Chapters\n\n"

        chapter_files = []
        # Generate chapter links based on the determined order, using potentially translated names
        for i, abstraction_index in enumerate(chapter_order):
            # Ensure index is valid and we have content for it
            if 0 <= abstraction_index < len(abstractions) and i < len(chapters_content):
                abstraction_name = abstractions[abstraction_index][
                    "name"
                ]  # Potentially translated name
                # Sanitize potentially translated name for filename
                safe_name = "".join(
                    c if c.isalnum() else "_" for c in abstraction_name
                ).lower()
                filename = f"{i+1:02d}_{safe_name}.md"
                index_content += f"{i+1}. [{abstraction_name}]({filename})\n"  # Use potentially translated name in link text

                # Add attribution to chapter content (using English fixed string)
                chapter_content = chapters_content[i]  # Potentially translated content
                # Clean any thinking tags from chapter content
                chapter_content = self._clean_llm_response(chapter_content)
                
                if not chapter_content.endswith("\n\n"):
                    chapter_content += "\n\n"
                # Keep fixed strings in English
                chapter_content += f"---\n\nGenerated by [AI Codebase Knowledge Generator](https://github.com/vegeta03/codebase-knowledge-generator)"

                # Store filename and corresponding content
                chapter_files.append({"filename": filename, "content": chapter_content})
            else:
                print(
                    f"Warning: Mismatch between chapter order, abstractions, or content at index {i} (abstraction index {abstraction_index}). Skipping file generation for this entry."
                )

        # Add attribution to index content (using English fixed string)
        index_content += f"\n\n---\n\nGenerated by [AI Codebase Knowledge Generator](https://github.com/vegeta03/codebase-knowledge-generator)"

        return {
            "output_path": output_path,
            "index_content": index_content,
            "chapter_files": chapter_files,  # List of {"filename": str, "content": str}
        }
        
    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing <think></think> tags and other artifacts.
        
        Args:
            response: The raw LLM response to clean
            
        Returns:
            Cleaned response with thinking tags removed
        """
        # Remove <think>...</think> blocks
        import re
        clean_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove possible trailing/leading whitespace from the cleaning
        clean_response = clean_response.strip()
        
        # If the response is now empty (entire response was inside think tags), 
        # return the original (this shouldn't happen with proper LLM behavior)
        if not clean_response and response:
            print("Warning: Entire response was inside <think> tags. Using original response.")
            return response
            
        return clean_response

    def exec(self, prep_res):
        output_path = prep_res["output_path"]
        index_content = prep_res["index_content"]
        chapter_files = prep_res["chapter_files"]

        print(f"Combining tutorial into directory: {output_path}")
        # Rely on Node's built-in retry/fallback
        os.makedirs(output_path, exist_ok=True)

        # Write index.md
        index_filepath = os.path.join(output_path, "index.md")
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(index_content)
        print(f"  - Wrote {index_filepath}")

        # Write chapter files - earlier implementation already had the cleaning code
        for chapter_info in chapter_files:
            chapter_content = chapter_info["content"]
            
            # No need to manually clean again since we've already done this in prep
            # The existing code to clean <think></think> tags can remain
            import re
            chapter_content = re.sub(r'<think>.*?</think>', '', chapter_content, flags=re.DOTALL)
            
            chapter_filepath = os.path.join(output_path, chapter_info["filename"])
            with open(chapter_filepath, "w", encoding="utf-8") as f:
                f.write(chapter_content)
            print(f"  - Wrote {chapter_filepath}")

        return output_path # Return the final path

    def post(self, shared, prep_res, exec_res):
        shared["final_output_dir"] = exec_res # Store the output path
        print(f"\nTutorial generation complete! Files are in: {exec_res}")
        return "default"
