import os
import re
import json5
from pocketflow import Node, BatchNode
from utils.crawl_github_files import crawl_github_files
from utils.call_llm import call_llm
from utils.crawl_local_files import crawl_local_files

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
        use_cache = shared.get("use_cache", False)  # Get use_cache flag, default to True

        # Helper to create context from files, respecting limits (basic example)
        def create_llm_context(files_data):
            context = ""
            file_info = [] # Store tuples of (index, path)
            for i, (path, content) in enumerate(files_data):
                entry = f"--- File Index {i}: {path} ---\n{content}\n\n"
                context += entry
                file_info.append((i, path))

            return context, file_info # file_info is list of (index, path)

        context, file_info = create_llm_context(files_data)
        # Format file info for the prompt (comment is just a hint for LLM)
        file_listing_for_prompt = "\n".join(
            [f"- {idx} # {path}" for idx, path in file_info]
        )
        return (
            context,
            file_listing_for_prompt,
            len(files_data),
            project_name,
            language,
            use_cache,
        )  # Return all parameters

    def exec(self, prep_res):
        (
            context,
            file_listing_for_prompt,
            file_count,
            project_name,
            language,
            use_cache,
        ) = prep_res  # Unpack all parameters
        print(f"Identifying abstractions using LLM...")

        # Add language instruction and hints only if not English
        language_instruction = ""
        name_lang_hint = ""
        desc_lang_hint = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `name` and `description` for each abstraction in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            # Keep specific hints here as name/description are primary targets
            name_lang_hint = f" (value in {language.capitalize()})"
            desc_lang_hint = f" (value in {language.capitalize()})"

        prompt = f"""
For the project `{project_name}`:

Codebase Context:
{context}

{language_instruction}Analyze the codebase context.
Identify the complete and comprehensive core most important abstractions to help those new to the codebase.

For each abstraction, provide:
1. A concise `name`{name_lang_hint}.
2. A "technical" and "computer science" centric `description` explaining what it is with a real-world and practical analogy, in atleast 100 words or more if required{desc_lang_hint}.
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

List of file indices and paths present in the context:
{file_listing_for_prompt}

Format the output as a JSON5 list of dictionaries:

```json5
[
  {{
    "name": "Query Processing{name_lang_hint}",
    "description": "Explains what the abstraction does.\nIt's like a central dispatcher routing requests.{desc_lang_hint}",
    "file_indices": [
      "0 # path/to/file1.py",
      "3 # path/to/related.py"
    ]
  }},
  {{
    "name": "Query Optimization{name_lang_hint}",
    "description": "Another core concept, similar to a blueprint for objects.{desc_lang_hint}",
    "file_indices": [
      "5 # path/to/another.js"
    ]
  }}
  // ... include all complete and comprehensive core most important abstractions
]
```"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0))  # Use cache only if enabled and not retrying

        # --- Validation ---
        try:
            json5_str = response.strip().split("```json5")[1].split("```")[0].strip()
            abstractions = json5.loads(json5_str)
        except (IndexError, ValueError) as e:
            # Handle malformed JSON5 or missing code blocks
            print(f"Error parsing JSON5 from LLM response: {e}")
            print("Attempting to fix malformed JSON5...")

            # Try to extract JSON5 content even if not properly formatted
            if "```json5" in response:
                json5_str = response.strip().split("```json5")[1].split("```")[0].strip()
            elif "```" in response:
                json5_str = response.strip().split("```")[1].split("```")[0].strip()
            else:
                json5_str = response.strip()

            # Try to fix common JSON5 formatting issues
            # Fix 1: Fix newlines in description field
            import re
            json5_str = re.sub(r'"description": "([^"]*?)\\n([^"]*?)"', r'"description": "\1 \2"', json5_str)

            try:
                abstractions = json5.loads(json5_str)
            except ValueError as e2:
                print(f"Failed to fix JSON5: {e2}")
                # Create a minimal valid structure as fallback
                abstractions = [
                    {
                        "name": "Default Abstraction",
                        "description": "Default abstraction created due to parsing error",
                        "file_indices": ["0 # main file"]
                    }
                ]
                print("Using fallback minimal structure")

        if not isinstance(abstractions, list):
            print("LLM output is not a list, converting to list")
            if isinstance(abstractions, dict):
                abstractions = [abstractions]
            else:
                abstractions = [
                    {
                        "name": "Default Abstraction",
                        "description": "Default abstraction created due to parsing error",
                        "file_indices": ["0 # main file"]
                    }
                ]

        validated_abstractions = []
        for item in abstractions:
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
        shared["abstractions"] = (
            exec_res  # List of {"name": str, "description": str, "files": [int]}
        )
        
        # List the identified abstractions by name
        print("Identified abstractions:")
        for i, abstraction in enumerate(exec_res):
            print(f"  {i+1}. {abstraction['name']}")


class AnalyzeRelationships(Node):
    def prep(self, shared):
        abstractions = shared[
            "abstractions"
        ]  # Now contains 'files' list of indices, name/description potentially translated
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", False)  # Get use_cache flag, default to True

        # Get the actual number of abstractions directly
        num_abstractions = len(abstractions)

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
            )  # Use potentially translated name here too
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

        # Add language instruction and hints only if not English
        language_instruction = ""
        lang_hint = ""
        list_lang_note = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `summary` and relationship `label` fields in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            lang_hint = f" (in {language.capitalize()})"
            list_lang_note = f" (Names might be in {language.capitalize()})"  # Note for the input list

        prompt = f"""
Based on the following abstractions and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions, Descriptions, Code):
{context}

{language_instruction}Please provide:
1. A high-level `summary` of the project's main purpose and functionality in a short "technical" and "computer science" friendly sentences{lang_hint}. Use markdown formatting with **bold** and *italic* text to highlight important concepts.
2. A list (`relationships`) describing the key interactions between these abstractions. For each relationship, specify:
    - `from_abstraction`: Index of the source abstraction (e.g., `0 # AbstractionName1`)
    - `to_abstraction`: Index of the target abstraction (e.g., `1 # AbstractionName2`)
    - `label`: A brief label for the interaction **in just a few words**{lang_hint} (e.g., "Manages", "Inherits", "Uses").
    Ideally the relationship should be backed by one abstraction calling or passing parameters to another.
    Make the relationship Simple but don't dilute it while doing so and exclude those non-important ones.

IMPORTANT INSTRUCTIONS:
1. Make sure EVERY abstraction is involved in at least ONE relationship (either as source or target).
2. Each abstraction index must appear at least once across all relationships.
3. Use ONLY the abstraction indices (0 to {num_abstractions-1}) from the list above, NOT file indices.
4. Do NOT use file indices or project names in the relationships.
5. The indices in from_abstraction and to_abstraction must be between 0 and {num_abstractions-1} inclusive.

Format the output as JSON5:

```json5
{{
  "summary": "A brief, simple explanation of the project{lang_hint}. Can span multiple lines with **bold** and *italic* for emphasis. IMPORTANT: This must be a single string value, not multiple strings.",
  "relationships": [
    {{
      "from_abstraction": "0 # AbstractionName1",
      "to_abstraction": "1 # AbstractionName2",
      "label": "Manages{lang_hint}"
    }},
    {{
      "from_abstraction": "2 # AbstractionName3",
      "to_abstraction": "0 # AbstractionName1",
      "label": "Provides config{lang_hint}"
    }}
    // ... other relationships
  ]
}}
```

Now, provide the JSON5 output:
"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # --- Validation ---
        try:
            json5_str = response.strip().split("```json5")[1].split("```")[0].strip()
            relationships_data = json5.loads(json5_str)
        except (IndexError, ValueError) as e:
            # Handle malformed JSON5 or missing code blocks
            print(f"Error parsing JSON5 from LLM response: {e}")
            print("Attempting to fix malformed JSON5...")

            # Try to extract JSON5 content even if not properly formatted
            if "```json5" in response:
                json5_str = response.strip().split("```json5")[1].split("```")[0].strip()
            elif "```" in response:
                json5_str = response.strip().split("```")[1].split("```")[0].strip()
            else:
                json5_str = response.strip()

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
                    from_idx = from_idx % num_abstractions
                    print(f"Auto-correcting to index {from_idx}")

                if not (0 <= to_idx < num_abstractions):
                    print(f"Warning: Invalid 'to' index {to_idx} in relationship. Max index is {num_abstractions-1}.")
                    # Try to fix by using a valid index
                    to_idx = to_idx % num_abstractions
                    print(f"Auto-correcting to index {to_idx}")

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
                        from_idx = int(from_matches[0]) % num_abstractions
                        to_idx = int(to_matches[0]) % num_abstractions

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

        # Check if all abstractions are involved in at least one relationship
        involved_abstractions = set()
        for rel in validated_relationships:
            involved_abstractions.add(rel["from"])
            involved_abstractions.add(rel["to"])

        # If any abstractions are missing, add relationships to ensure all are included
        for i in range(num_abstractions):
            if i not in involved_abstractions:
                print(f"Warning: Abstraction {i} is not involved in any relationship. Adding a default relationship.")
                # Add a relationship from this abstraction to the next one (or the first one if this is the last)
                to_idx = (i + 1) % num_abstractions
                validated_relationships.append({
                    "from": i,
                    "to": to_idx,
                    "label": "Relates to"  # Default generic label
                })

        print("Generated project summary and relationship details.")
        return {
            "summary": relationships_data["summary"],  # Potentially translated summary
            "details": validated_relationships,  # Store validated, index-based relationships with potentially translated labels
        }


    def post(self, shared, prep_res, exec_res):
        # Structure is now {"summary": str, "details": [{"from": int, "to": int, "label": str}]}
        # Summary and label might be translated
        shared["relationships"] = exec_res

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
            json5_str = response.strip().split("```json5")[1].split("```")[0].strip()
        except IndexError:
            # Handle case where ```json5 is not found
            print("Could not find ```json5 in response, trying to extract JSON from any code block")
            if "```" in response:
                json5_str = response.strip().split("```")[1].split("```")[0].strip()
            else:
                json5_str = response.strip()

        try:
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


        prompt = f"""
{language_instruction}Write a software developer friendly tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

Concept Details{concept_details_note}:
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note}:
{item["full_chapter_listing"]}

Context from previous chapters{prev_summary_note}:
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}

Relevant Code Snippets (Code itself remains unchanged):
{file_context_str if file_context_str else "No specific code snippets provided for this abstraction."}

Instructions for the chapter (Generate content in {language.capitalize()} unless specified otherwise):
- Start with a clear heading (e.g., `# Chapter {chapter_num}: {abstraction_name}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter{instruction_lang_note}, referencing it with a proper Markdown link using its name{link_lang_note}.

- Begin with a high-level motivation explaining what problem this abstraction solves{instruction_lang_note}. Start with a central use case as a concrete example. The whole chapter should guide the reader to understand how to solve this use case. Make it very comprehensive and very understandable to a Senior Software Developer.

- If the abstraction is complex, break it down into key concepts. Explain each concept one-by-one in a very beginner-friendly way{instruction_lang_note}.

- Explain how to use this abstraction to solve the use case{instruction_lang_note}. Give example inputs and outputs for code snippets (if the output isn't values, describe at a high level what will happen{instruction_lang_note}).

- Each code block should be COMPLETE! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Make the code Simple however don't loose clarity. Use comments{code_comment_note} to skip non-important implementation details. Each code block should have a senior software developer friendly explanation right after it{instruction_lang_note}.

- Describe the internal implementation to help understand what's under the hood{instruction_lang_note}. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called{instruction_lang_note}. It's recommended to use a simple sequence diagram with mermaid syntax (`sequenceDiagram`) with a dummy example - keep it minimal with at least 5 participants to ensure clarity. If participant name has space, use: `participant QP as Query Processing`. ALWAYS use proper mermaid syntax with `sequenceDiagram` at the beginning and the correct arrow syntax (e.g., use `->>` for messages, NOT `->`). Example: ```mermaid\nsequenceDiagram\n    participant A as ComponentA\n    participant B as ComponentB\n    A->>B: Request\n    B->>A: Response\n```{mermaid_lang_note}.

- Then dive deeper into code for the internal implementation with references to files. Provide example code blocks, but make them similarly simple however don't dilute it, and "Computer Science"-friendly. Explain{instruction_lang_note}.

- IMPORTANT: When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title{link_lang_note}. Translate the surrounding text.

- Use mermaid diagrams to illustrate complex concepts with PROPER mermaid syntax. ALWAYS begin with the diagram type (e.g., `sequenceDiagram`, `flowchart LR`, `classDiagram`, etc.) and use the correct syntax for that diagram type. For sequence diagrams, use proper arrow syntax like `->>`, `-->>`, `-->`, etc. NOT just `->`. For flowcharts, use proper node and connection syntax. Example with correct syntax: ```mermaid\nsequenceDiagram\n    participant A as ComponentA\n    participant B as ComponentB\n    A->>B: Request\n    B->>A: Response\n``` {mermaid_lang_note}.

- Heavily use real-world and practical analogies and examples throughout{instruction_lang_note} to help a Senior Software Developer understand.

- End the chapter with a brief conclusion that summarizes what was learned{instruction_lang_note} and provides a transition to the next chapter{instruction_lang_note}. If there is a next chapter, use a proper Markdown link: [Next Chapter Title](next_chapter_filename){link_lang_note}.

- Ensure the tone is welcoming and easy for a seasoned sofware developer professional to understand{tone_note}.

- Output *only* the Markdown content for this chapter.

Now, directly provide a "technical" and "Computer Science"-friendly Markdown output (DON'T need ```markdown``` tags):
"""
        chapter_content = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying
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

        # Write chapter files
        for chapter_info in chapter_files:
            chapter_filepath = os.path.join(output_path, chapter_info["filename"])
            with open(chapter_filepath, "w", encoding="utf-8") as f:
                f.write(chapter_info["content"])
            print(f"  - Wrote {chapter_filepath}")

        return output_path # Return the final path


    def post(self, shared, prep_res, exec_res):
        shared["final_output_dir"] = exec_res # Store the output path
        print(f"\nTutorial generation complete! Files are in: {exec_res}")
