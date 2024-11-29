import spacy
from spacy.tokens import DocBin
import random
from spacy.training.example import Example
from openai import OpenAI
import os
import actionreduction
import inspect
import re

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

def AutoFormalizer(handle, function_str, entity_list_str):
    # Create the prompt
    prompt = f"""
    Using the following functions:
    {function_str}

    using the extracted information:
    {entity_list_str}

    Construct a series of Python function calls that should be executed in the correct order in which a user would interact with the webiste to create the Reddit post. Return only the function calls, without any explanation or comments in the code to be executed later by exec().
    """
    response = handle.chat.completions.create(
        model="gpt-4o",
        messages=[
             {"role": "system", "content": "You are a helpful programming assistant."},
              {"role": "user", "content": prompt}
        ]
    )
    pattern = r"^(`{3}|~{3}).*$"
    cleaned_text = re.sub(pattern, "", response.choices[0].message.content, flags=re.MULTILINE).strip()
    return cleaned_text

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


# Load the fine-tuned model for evaluation
nlp = spacy.load("./fine_tuned_model")
key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key= key)

# Load the binary file
doc_bin = DocBin().from_disk("./train.spacy")
docs = list(doc_bin.get_docs(nlp.vocab))
random.shuffle(docs)

#initialize selenium
rd = actionreduction.RedditPoster()
#dynamically creates list of basic functions which are available to be called
function_str = list_public_functions_with_args(rd, 'rd', blacklist=['login', 'quit'])
rd.login(username, password)
input()

text = 'Create a poll in r/testautomationcom titled "Whats your favourite show in 2024?" with content "which of the following shows did you enjoy the most during during this year?" and options "The Penguin", "Dune Prophecy", "Tracker", "Fallout".'
formatted_string = NER(nlp, text)
script = AutoFormalizer(client, function_str, formatted_string)
#print(script)
exec(script)
input()
