import os
import re

# PATHS
prompt_folder_path = 'prompts'
sparql_fewShot_path = 'few_shot_SPARQL'
examon_fewShot_path = 'few_shot_ExamonQL'
llm_outputs_path = 'llm_outputs'
query_output_path = 'query_output'
token_used_path = 'stats/token'
time_used_path = 'stats/time'
saved_results_path = 'saved_results'

# provide llama-3 8B model directory
model_dir = ""

def setup():
    os.makedirs(prompt_folder_path, exist_ok=True)
    os.makedirs(llm_outputs_path, exist_ok=True)
    os.makedirs(val_llm_outputs_path, exist_ok=True)
    os.makedirs(query_output_path, exist_ok=True)
    os.makedirs(token_used_path, exist_ok=True)
    os.makedirs(time_used_path, exist_ok=True)
    
    print("Initialialized the repository!\n")

def get_query_txt(text):                        # outdated extraction
    # Find the start and end of the SPARQL query
    start_index = text.find("PREFIX")
    end_index = text.find("```", start_index)

    # If both start and end indices are found
    if start_index != -1 and end_index != -1:
        # Extract the SPARQL query
        sparql_query = text[start_index:end_index]
        return sparql_query.strip()
    else:
        return None

def extract_sparql_query(text):
    import re
    
    # Regex to match the start of the SPARQL query
    start_pattern = re.compile(r'\bPREFIX\b', re.IGNORECASE)
    # Regex to match the closing curly brace '}' after the PREFIX
    end_pattern = re.compile(r'\}', re.IGNORECASE)
  
    end_clauses = ["GROUP BY","ORDER BY", "LIMIT", "HAVING", "OFFSET"]

    # Find the starting position of the SPARQL query
    start_match = start_pattern.search(text)
    if not start_match:
        return None  # No PREFIX found, so no SPARQL query present

    start_index = start_match.start()

    # Find the closing brace '}' after the PREFIX
    end_match = end_pattern.search(text, pos=start_index)
    if not end_match:
        return None  # No closing brace found, invalid SPARQL query
    
    # Set the initial end_index to the position of the closing brace
    end_index = end_match.end()

    # Extract text following the closing brace to check for additional clauses
    subsequent_text = text[end_index:500]  # Extract some buffer length
    subsequent_lines = subsequent_text.splitlines()

    # Check the next few lines for ending clauses
    for line in subsequent_lines:
        for clause in end_clauses:
            if clause in line:
                end_index += len(line) + 1  # Extend end_index to include this line
            else:
                pass

    # Ensure the end_index ends correctly if no additional clauses are found
    if text[end_index:].strip().startswith('}'):
        final_brace_pos = text.find('}', start_index + 1)
        if final_brace_pos != -1:
            end_index = final_brace_pos + 1

    return text[start_index:end_index].strip()

def get_query_codellama(text):
    # Find the start and end of the SPARQL query
    start_index = text.find("PREFIX")
    end_index = text.find("}", start_index)

    # If both start and end indices are found
    if start_index != -1 and end_index != -1:
        # Extract the SPARQL query
        sparql_query = text[start_index:end_index]
        return sparql_query.strip()
    else:
        return None

def read_prompts(folder_path):
    file_text = []
    # List all files in the specified folder
    files = os.listdir(folder_path)
    
    # Filter out non-txt files
    txt_files = [file for file in files if file.endswith('.txt')]
    txt_files =  sorted(txt_files)

    # Read and print the contents of each txt file
    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        with open(file_path, 'r') as file:
            content = file.read()
            # print(f"Contents of {txt_file}:\n{content}\n")
            file_text.append(content)
    return txt_files, file_text


def read_fewShots(folder_path):
    file_text = []
    # List all files in the specified folder
    files = os.listdir(folder_path)

    # Read and print the contents of each txt file
    for txt_file in files:
        file_path = os.path.join(folder_path, txt_file)
        with open(file_path, 'r') as file:
            content = file.read()
            # print(f"Contents of {txt_file}:\n{content}\n")
            file_text.append(content)
    return file_text

def read_txt(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def save_to_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directory if it doesn't exist
    with open(file_path, "w") as file:
        file.write(str(content))
    print(f"Saved to {file_path}\n")

def format_for_llm(content):
    """
    Format the content to make it easier for LLMs to process.
    You can customize this function based on your needs.
    """
    # Example formatting: Add headers or sections
    formatted_content = content.replace('\n\n', '\n\n---\n\n')  # Insert breaks for clarity
    return formatted_content

def read_file_for_llm(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the entire file content
            content = file.read()
            
            # Optional: Format content to improve readability
            # Example: Add section breaks or summaries
            formatted_content = format_for_llm(content)
            
            return formatted_content
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except IOError as e:
        print(f"Error: An IOError occurred. Details: {e}")

def read_examples_for_llm(file_path):
    """Read and format the content of a file for LLM processing."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Format the content for readability
            #formatted_content = format_for_llm(content)
            return content
    except FileNotFoundError:
        return f"Error: The file at {file_path} was not found."
    except IOError as e:
        return f"Error: An IOError occurred. Details: {e}"

def create_formatted_examples(folder_path):
    # List all files in the specified folder
    files = os.listdir(folder_path)

    examples = "## **Some example prompt implementations**\n\n"
    
    # Read and format the contents of each txt file
    for txt_file in files:
        file_path = os.path.join(folder_path, txt_file)
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            file_name = os.path.basename(file_path)
            try:
                file_content = read_examples_for_llm(file_path)
                # Add a header for each file's content and format the example block
                example_name = txt_file.split("_")[1].split(".")[0]
                examples += f"### **Example: {example_name}**\n{file_content}\n"
                # Add a break format between different examples
                examples += "---\n"
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return examples

def extract_sparql_query(text):
    # Regex to match the start of the SPARQL query
    start_pattern = re.compile(r'\bPREFIX\b', re.IGNORECASE)
    # Regex to match the closing curly brace '}' after the PREFIX
    end_pattern = re.compile(r'\}', re.IGNORECASE)
  
    end_clauses = ["GROUP BY","ORDER BY", "LIMIT", "HAVING", "OFFSET"]

    # Find the starting position of the SPARQL query
    start_match = start_pattern.search(text)
    if not start_match:
        return None  # No PREFIX found, so no SPARQL query present

    start_index = start_match.start()

    # Find the closing brace '}' after the PREFIX
    end_match = end_pattern.search(text, pos=start_index)
    if not end_match:
        return None  # No closing brace found, invalid SPARQL query
    
    # Set the initial end_index to the position of the closing brace
    end_index = end_match.end()

    # Extract text following the closing brace to check for additional clauses
    subsequent_text = text[end_index:500]  # Extract some buffer length
    subsequent_lines = subsequent_text.splitlines()

    # Check the next few lines for ending clauses
    for line in subsequent_lines:
        for clause in end_clauses:
            if clause in line:
                end_index += len(line) + 1  # Extend end_index to include this line
            else:
                pass

    # Ensure the end_index ends correctly if no additional clauses are found
    if text[end_index:].strip().startswith('}'):
        final_brace_pos = text.find('}', start_index + 1)
        if final_brace_pos != -1:
            end_index = final_brace_pos + 1

    return text[start_index:end_index].strip()