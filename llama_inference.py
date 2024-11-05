from utils import *
import torch

# read ontology
ontology = read_txt("ontology.txt")

# read few shot examples
example_queries_list = read_fewShots(sparql_fewShot_path)

example_queries = ""
for example in example_queries_list:
      example_queries = example_queries + f"\n\n{example}"

#read exadata metadata
exaMeta = read_txt("Exadata_metadata.txt")

def inference(sys_role,input_prompt,context,few_shots,exameta,model,tokenizer,p_num):
      prompt = f"""
      Using the ontology, example query implementations, and sensor metadata, please write a SPARQL query to address the following prompt:
      **Prompt:**
      {input_prompt}
      **SPARQL Query:**
      """
      messages = [
        {"role": "system", "content": sys_role},
        {"role": "user", "content": prompt},
        {"role": "context", "content": f"Ontology:\n{context}\n{few_shots}\nSensor Metadata:\n{exameta}"},
      ]     
      # messages = [
      #   {"role": "system", "content": sys_role},
      #   {"role": "user", "content": prompt},
      #   {"role": "context", "content": f"{context}\n{few_shots}\n{exameta}"},
      # ]     

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
            top_p=0.9                
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

def code_llama_inference(sys_role,prompt,context,model,tokenizer):
      # Move the model to GPU if available
      device = "cuda" if torch.cuda.is_available() else "cpu"
      model.to(device)

      input_text = f"{sys_role}. For context: {context}. Write a SPARQL query for the following prompt: '{prompt}'. Describe the generated query code as well"

      # Tokenize input
      inputs = tokenizer(input_text, return_tensors="pt").to(device)

      # Generate predictions with a limit on the number of new tokens
      outputs = model.generate(**inputs, max_new_tokens=100)

      # Decode the output to get human-readable text
      generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

      # Remove the input text from the output
      output_text = generated_text[len(input_text)+1:].strip()
      print(output_text)

      return output_text


if __name__ == "__main__":
      print(f"Ontology:\n{ontology}\n\n{example_queries}")