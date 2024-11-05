import os
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_inference import *
from utils import *

#initialize the setup
setup()

# Load llm model
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto")

prompt_filename,prompt_list = read_prompts(prompt_folder_path)

sys_role = read_txt("sys_role.txt")
# read ontology
ontology = read_file_for_llm("ontology.txt")

#read exadata metadata
exaMeta = read_file_for_llm("Exadata_metadata.txt")

# read few shot examples
few_shots = create_formatted_examples(sparql_fewShot_path)

for i in range(len(prompt_list)):
    start_time = time.time()
    llm_output = inference(sys_role,prompt_list[i],ontology,few_shots,exaMeta,model,tokenizer,i+1)
    time_taken = time.time() - start_time

    # Save the time taken
    save_path  = os.path.join(time_used_path,f"{i+1}/inference_time.txt")
    save_to_file(save_path, time_taken)

    query_code = get_query_txt(llm_output)
    #query_code = get_query_codellama(llm_output)

    save_path  = os.path.join(llm_outputs_path,prompt_filename[i])
    with open(save_path, "w") as file:
        file.write(llm_output)

    print(f"String saved to {save_path}\n")

if __name__ == "__main__":
    print(ontology,few_shots,exaMeta)
    print("\n\nDONE!")
