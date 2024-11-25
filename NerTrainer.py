import spacy
from spacy.tokens import DocBin
import random
from spacy.training.example import Example
from sklearn.metrics import precision_score, recall_score, f1_score

nlp = spacy.load("en_core_web_sm")

# Add a new pipeline component
ner = nlp.get_pipe("ner")

# Load the binary file
doc_bin = DocBin().from_disk("./train.spacy")
docs = list(doc_bin.get_docs(nlp.vocab))


# Extract unique entity types
entity_types = set()
for doc in docs:
    for ent in doc.ents:
        label = ent.label_
        entity_types.add(label)

for type in entity_types:
    print(type)
    ner.add_label(type)

train_data = docs

# Split data
random.shuffle(train_data)
split = int(len(train_data) * 0.8)
train, dev = train_data[:split], train_data[split:]


# Training loop
optimizer = nlp.create_optimizer()
for epoch in range(50):  # Number of epochs
    losses = {}
    random.shuffle(train)
    for doc in train:
        example = Example.from_dict(doc, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]})
        nlp.update([example], drop=0.5, losses=losses)
    print(f"Epoch {epoch + 1}: {losses}")

nlp.to_disk("./fine_tuned_model")

# Load the fine-tuned model for evaluation
nlp = spacy.load("./fine_tuned_model")

pred = nlp(dev[0].text)
print(pred.ents)

# Evaluate the fine-tuned model
def evaluate_model(model, validation_docs):
    y_true = []
    y_pred = []

    for doc in validation_docs:
        # Use the fine-tuned model to predict entities
        pred_doc = model(doc.text)

        # Ground truth entities
        
        true_entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        # Predicted entities
        pred_entities = [(ent.start_char, ent.end_char, ent.label_) for ent in pred_doc.ents]
        
        # Append binary comparison for each label
        for entity in true_entities:
            y_true.append(entity)
            y_pred.append(entity if entity in pred_entities else None)

        for entity in pred_entities:
            if entity not in true_entities:
                y_true.append(None)
                y_pred.append(entity)

    # Flatten the true and predicted lists for evaluation
    y_true_labels = [ent[2] for ent in y_true if ent]
    y_pred_labels = [ent[2] for ent in y_pred if ent]

    # Calculate metrics
    precision = precision_score(y_true_labels, y_pred_labels, average="weighted", zero_division=0)
    recall = recall_score(y_true_labels, y_pred_labels, average="weighted", zero_division=0)
    f1 = f1_score(y_true_labels, y_pred_labels, average="weighted", zero_division=0)

    return precision, recall, f1


#Run evaluation
precision, recall, f1 = evaluate_model(nlp, dev[:5])
print(f"Evaluation Results:\nPrecision: {precision:.2f}\nRecall: {recall:.2f}\nF1-Score: {f1:.2f}")