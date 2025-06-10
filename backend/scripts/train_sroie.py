import os
import torch
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor, Trainer, TrainingArguments, DataCollatorForTokenClassification
from datasets import load_from_disk

# Load your tokenized dataset
dataset = load_from_disk("datasets/sroie_tokenized")

# Define label names (based on SROIE fields or your custom fields)
label_list = ["O", "B-total", "I-total", "B-date", "I-date", "B-company", "I-company", "B-address", "I-address"]
label2id = {l: i for i, l in enumerate(label_list)}
id2label = {i: l for i, l in enumerate(label_list)}

# Label map for simple keyword-based alignment (temporary, basic logic)
label_keywords = {
    "total": "B-total",
    "date": "B-date",
    "company": "B-company",
    "address": "B-address"
}

def tokenize_and_align_labels(example):
    words = example["words"]
    boxes = example["boxes"]
    labels = example["labels"]
    image = example["image"]

    label_ids = []
    for word in words:
        key = word.lower()
        matched_label = "O"
        for keyword, label in label_keywords.items():
            if keyword in key:
                matched_label = label
                break
        label_ids.append(label2id[matched_label])

    encoding = processor(
        images=image,
        text=words,
        boxes=boxes,
        word_labels=label_ids,
        return_tensors="pt",
        truncation=True,
        padding="max_length"
    )

    return {
        "input_ids": encoding["input_ids"][0],
        "attention_mask": encoding["attention_mask"][0],
        "bbox": encoding["bbox"][0],
        "labels": encoding["labels"][0],
        "pixel_values": encoding["pixel_values"][0]
    }

# Load processor and model
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
model = LayoutLMv3ForTokenClassification.from_pretrained(
    "microsoft/layoutlmv3-base",
    num_labels=len(label_list),
    id2label=id2label,
    label2id=label2id
)

# Apply the token labeling logic to dataset
encoded_dataset = dataset.map(
    tokenize_and_align_labels,
    remove_columns=dataset.column_names
)

# Training configuration
training_args = TrainingArguments(
    output_dir="models/layoutlmv3-sroie",
    per_device_train_batch_size=1,
    num_train_epochs=1,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=50
)


# Data collator for dynamic padding
collator = DataCollatorForTokenClassification(tokenizer=processor.tokenizer)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset,
    tokenizer=processor.tokenizer,
    data_collator=collator
)

# Start training
trainer.train()

# Save fine-tuned model
model.save_pretrained("models/layoutlmv3-sroie")
processor.save_pretrained("models/layoutlmv3-sroie")

print("✅ Model training complete! Saved to models/layoutlmv3-sroie")
