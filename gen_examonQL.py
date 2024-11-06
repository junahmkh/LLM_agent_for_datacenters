import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from utils import *
import time

sys_role = read_txt("sys_role_examon.txt")

# read examonql context
context = read_txt("context_examonQL.txt")

# read few shot examples
example_queries_list = read_fewShots(examon_fewShot_path)

example_queries = "Some ExamonQL implementations as examples:"
for example in example_queries_list:
      example_queries = example_queries + f"\n\n{example}"

def inference(sys_role,prompt,context,example_queries,model,tokenizer,p_num):
      messages = [
        {"role": "system", "content": sys_role},
        {"role": "user", "content": "Write ExamonQL implementation for the following prompt: "+prompt},
        {"role": "context", "content": f"Context:\n{context}\n\n{example_queries}"},
      ]     
       
      input_ids = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
            ).to(model.device)

      # Tokenize the input for comparison and count tokens
      input_tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
      input_token_count = len(input_tokens)

      terminators = [
            tokenizer.eos_token_id,
            tokenizer.convert_tokens_to_ids("<|eot_id|>")
      ]

      outputs = model.generate(
            input_ids,
            max_new_tokens=512,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
      )
      
      response = outputs[0][input_ids.shape[-1]:]
      output_text = tokenizer.decode(response, skip_special_tokens=True)
      print(output_text)
      
      # Tokenize the output and count tokens
      output_tokens = tokenizer.convert_ids_to_tokens(response)
      output_token_count = len(output_tokens)

      # Save the token counts
      save_path  = os.path.join(token_used_path,f"{p_num}/input_token_count.txt")
      save_to_file(save_path, input_token_count)
      save_path  = os.path.join(token_used_path,f"{p_num}/output_token.txt")
      save_to_file(save_path, output_token_count)

      return output_text

if __name__ == '__main__':
    #initialize the setup
    setup()

    # Load llm model
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto")

    prompt_filename,prompt_list = read_prompts(prompt_folder_path)

    spatial_queries_to_remove = ["p_01.txt","p_02.txt","p_03.txt"]

    for file_name in spatial_queries_to_remove:
        idx = prompt_filename.index(file_name)
        prompt_list.pop(idx)
        prompt_filename.pop(idx)

    for i in range(len(prompt_list)):
        start_time = time.time()
        llm_output = inference(sys_role,prompt_list[i],context,example_queries,model,tokenizer,i+1)
        time_taken = time.time() - start_time

        # Save the time taken
        save_path  = os.path.join(time_used_path,f"{i+1}/inference_time.txt")
        save_to_file(save_path, time_taken)

        save_path  = os.path.join(llm_outputs_path,prompt_filename[i])
        with open(save_path, "w") as file:
            file.write(llm_output)

        print(f"String saved to {save_path}\n")