import re
import json

def parse_dataset(input_file, output_file):
    # Read input file
    with open(input_file, "r") as file:
        input_text = file.read()

    # Split dataset into lines
    lines = input_text.strip().split('\n')
    data = []

    # Regex to extract text and entities
    entity_pattern = r"\{(.*?)\}\[(.*?)\]"

    for line in lines:
        entities = []
        clean_text = ""
        last_end = 0

        # Find all entities and clean the text
        for match in re.finditer(entity_pattern, line):
            start, end = match.span()
            entity_text, entity_label = match.groups()

            # Append text before the entity
            clean_text += line[last_end:start]
            # Append the entity text and record its start/end indices
            clean_text += entity_text
            start_idx = len(clean_text) - len(entity_text)
            end_idx = len(clean_text)
            entities.append([start_idx, end_idx, entity_label])
            last_end = end

        # Append the remaining text after the last match
        clean_text += line[last_end:]

        # Store the parsed data
        data.append({"text": clean_text.strip(), "entities": entities})

    # Write to JSON file
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, separators=(',', ':'))

# File paths
input_file = "dataset.txt"  # Input file containing the dataset
output_file = "parsed_dataset.json"  # Output JSON file

# Run the parser
parse_dataset(input_file, output_file)

print(f"Dataset has been parsed and saved to {output_file}.")