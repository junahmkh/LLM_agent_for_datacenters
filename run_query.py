from graphdb_connect import *
from process_query import process_query
import time

#initialize the setup
setup()

graphdb_endpoint = "Add endpoint address"

# If authentication is required, provide username and password
username = ""
password = ""

# prompt_filename,prompt_list = read_prompts(prompt_folder_path)
prompt_filename,query_list = read_prompts(llm_outputs_path)

for i in range(len(query_list)):
    prompt = prompt_filename[i]
    sparql_query = query_list[i]

    sparql_query = extract_sparql_query(sparql_query)
    sparql_query = process_query(sparql_query)
    print(sparql_query)
    try:
        start_time = time.time()
        # Get the DataFrame
        df = query_output(graphdb_endpoint, sparql_query, username, password)
        time_taken = time.time() - start_time

        save_path  = os.path.join(time_used_path,f"{int(prompt_filename[i][2:-4])}/query_run_time.txt")
        save_to_file(save_path, time_taken)

        print(f"Prompt: {prompt}")
        print(f"Output: \n{df}\n")

        # Save DataFrame as a text file
        filename = prompt_filename[i][:-4]+".csv"
    
        save_path  = os.path.join(query_output_path,filename)
        df.to_csv(save_path, index=False)
            
        print(f"output saved to {save_path}\n")
    except:
        print("Skipped, error in query.")
