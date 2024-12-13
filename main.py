import spacy
from spacy.tokens import DocBin
import random
from spacy.training.example import Example
from openai import OpenAI
import os
import actionreduction
import inspect
import re
import test
import time
import csv

username, password = 'username', 'password'
def NER(model, text):
    pred = model(text)
    # Create a dictionary to group entities
    entity_lines = []
    options = []  # To collect 'Option' entities
    # Iterate over entities
    for ent in pred.ents:
        if ent.label_ == "Option":
            options.append(ent.text)
        else:
            entity_lines.append(f"{ent.label_}: {ent.text}")
    # Add grouped options as a single line
    if options:
        entity_lines.append(f"Options: [{', '.join(options)}]")
    # Combine all lines into the final string
    formatted_string = "\n".join(entity_lines)
    return formatted_string

def NER_GPT(handle, entities, input):
    # Create the prompt
    prompt1 = f"""
    "You are an intelligent assistant tasked with extracting entities from a given string based on predefined categories. 
    Each category has specific examples to guide your extraction. 
    Your task is to identify the entities present in the string and assign them to the appropriate categories as accurately as possible. 
    Follow these guidelines:
    {entities}
    Return your results in a clear, labeled format with values corresponding to the appropriate categories. If entities in entity list cannot be found omit them from output.
    present output in format:
    entity1: value
    entity2: value
    ...
    Ensure the output strictly adheres to this format with no additional text, explanations, or comments.
    Avoid assuming information not explicitly stated in the input."
    """
    response = handle.chat.completions.create(
        model="gpt-4o",
        messages=[
             {"role": "system", "content": prompt1},
              {"role": "user", "content": input}
        ]
    )
    return response.choices[0].message.content

def MissingEntityInference(handle, entities, input, script):
    # Create the prompt
    prompt1 = f"""
    "You are an intelligent porgramming assistant tasked with finding missing required inputs for functions in a script.
    If any required input in the sequence of function calls are in the format %entity_name% it means those specific required inputs are missing and need to be identified.
    Follow these guidelines:
    {entities}
    Return the same sequence of functions with the updated inputs and any missing inputs can be inferred from the user string and cannot be left empty. Return only the function calls, without any explanation or comments in the code.
    The output should only be the python script.
    """
    prompt2 = f"""
    user string:
    {input}
    script:
    {script}
    """
    response = handle.chat.completions.create(
        model="gpt-4o",
        messages=[
             {"role": "system", "content": prompt1},
              {"role": "user", "content": prompt2}
        ]
    )
    return response.choices[0].message.content
   
def AutoFormalizer(handle, function_str, entity_list_str, InferDis, userInput, entities=None):
    # Create the prompt
    recomputeFlag = False
    prompt = f"""
    Using the following functions:
    {function_str}

    using the extracted information:
    {entity_list_str}

    Construct a series of Python function calls that should be executed in the correct order in which a user would interact with the website to accomplish the following task. 
    {userInput}
    Return only the function calls, without any explanation or comments in the code to be executed later by exec() missing inputs should always be replaced with the name of the missing function parameter encapsulated with % in format %parameter_name%.
    The output should only be the python script. For optional parameters set them to parameter_name=None if not required.
    """
    response = handle.chat.completions.create(
        model="gpt-4o",
        messages=[
             {"role": "system", "content": "You are a helpful programming assistant."},
              {"role": "user", "content": prompt}
        ]
    )
    #infer missing inputs missing inputs will be in format %var_name%
    output = response.choices[0].message.content
    pattern = r"%[a-zA-Z0-9_]+%"
    if InferDis == False:
        if re.search(pattern, response.choices[0].message.content):
            recomputeFlag = True
            output = MissingEntityInference(handle, entities, userInput, output)
    
    pattern = r"^(`{3}|~{3}).*$"
    cleaned_text = re.sub(pattern, "", output, flags=re.MULTILINE).strip()
    return cleaned_text, recomputeFlag

def list_public_functions_with_args(obj, object_name, blacklist=None):
    public_methods = [
        attr for attr in dir(obj)
        if not attr.startswith("_") and callable(getattr(obj, attr))
    ]
    
    method_signatures = []
    for method_name in public_methods:
        method = getattr(obj, method_name)
        if (callable(method)) and (method_name not in blacklist):
            signature = inspect.signature(method)
            method_signatures.append(f"{object_name}.{method_name}{signature}")
    
    return "\n".join(method_signatures)

def process_test_dataset(file_path):
    # Read the dataset from the file
    with open(file_path, 'r') as file:
        dataset = file.read()

    # Split dataset into sections separated by empty lines
    sections = [section.strip() for section in dataset.strip().split("\n\n")]
    prompt_result_map = {}

    for section in sections:
        # Split each section into lines
        lines = section.splitlines()
        
        # First 5 lines are the prompts, the rest are the expected output
        prompts = lines[:5]
        expected_output = lines[5:]
        
        # Map each prompt to the entire expected output block
        for prompt in prompts:
            prompt_result_map[prompt] = "\n".join(expected_output)
    
    return prompt_result_map

# Load the fine-tuned model for evaluation
nlp = spacy.load("./fine_tuned_model")
key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key= key)

# Load the testing dataset
testing_set = process_test_dataset('test_data.txt')

#initialize selenium
rd = actionreduction.RedditPoster()
#dynamically creates list of basic functions which are available to be called
function_str = list_public_functions_with_args(rd, 'rd', blacklist=['login', 'quit']) 


#load available salient categories
with open('SalientCategories.txt', 'r') as file:
    content = file.read()

#log test
header = ["Prompt Name", "Function Accuracy", "Argument Accuracy", "Overall Accuracy", "Execution Time", "Recomputed"]

csv_file = open("accuracy_log_GPT.csv", mode="w", newline="")   
# Write the header row
csv_writer = csv.writer(csv_file)
csv_writer.writerow(header)

key_iterator = iter(testing_set)
for key in key_iterator:
    #get salient categories
    start_time = time.time() 
    formatted_string = NER_GPT(client, content, key)
    #formatted_string = NER(nlp, key)
    script, recomputed = AutoFormalizer(client, function_str, formatted_string, False, key, entities=content)
    delta_time = time.time() - start_time
    accuracy = test.ModelEval.evaluate_model_with_accuracy(testing_set[key], script)
    print('expected')
    print(testing_set[key])
    print('result')
    print(script)
    csv_writer.writerow([key, accuracy['function_accuracy'], accuracy["argument_accuracy"], accuracy["overall_accuracy"], delta_time, 1 if recomputed else 0])


#print(result)



#rd.login(username, password)
#text = 'Post a link in r/testautomationcom with content www.google.com'
#text = 'Search for example workout routines, diet plans, and fitness tips in r/fitness based on comment count and whats hot.'
#input() 
'''
with open('SalientCategories.txt', 'r') as file:
    content = file.read()
formatted_string = NER_GPT(client, content, text)
print(formatted_string)
script = AutoFormalizer(client, function_str, formatted_string, False, text, entities=content)
#print(script)
#exec(script)
'''