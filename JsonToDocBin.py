import json
import spacy
from spacy.tokens import DocBin

def convert_json_to_spacy(json_path, output_path, nlp):
    doc_bin = DocBin()
    with open(json_path, "r") as f:
        training_data = json.load(f)
    for entry in training_data:
        text = entry["text"]
        entities = entry["entities"]
        doc = nlp.make_doc(text)
        spans = [doc.char_span(start, end, label) for start, end, label in entities]
        doc.ents = [span for span in spans if span is not None]
        doc_bin.add(doc)
    doc_bin.to_disk(output_path)
    return list(doc_bin.get_docs(nlp.vocab))

nlp = spacy.blank("en")  # Blank model for conversion
docs = convert_json_to_spacy("parsed_dataset.json", "./train.spacy", nlp)

for doc in docs:
    print(f"Text: {doc.text}")
    print("Entities:")
    for ent in doc.ents:
        print(f"  - {ent.text} ({ent.start_char}, {ent.end_char}, {ent.label_})")
    print("-" * 40)
