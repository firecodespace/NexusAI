import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
from typing import List, Dict
import os

# Load fine-tuned model
MODEL_DIR = "models/layoutlmv3-sroie"
processor = LayoutLMv3Processor.from_pretrained(MODEL_DIR)
model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_DIR)
model.eval()

# Map class IDs to field labels
LABEL_MAP = {
    1: "total",
    2: "total",
    3: "date",
    4: "date",
    5: "company",
    6: "company",
    7: "address",
    8: "address",
}

def extract_fields_with_model(image_path: str, ocr_words: List[str], boxes: List[List[int]]) -> Dict[str, str]:
    """
    Uses fine-tuned LayoutLMv3 model to predict labels for each word in invoice.
    Aggregates fields like total, date, etc.
    """
    image = Image.open(image_path).convert("RGB")

    encoding = processor(
        images=image,
        text=ocr_words,
        boxes=boxes,
        return_tensors="pt",
        truncation=True,
        padding="max_length"
    )

    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)[0].tolist()

    field_data = {}
    current_field = None
    current_value = []

    for idx, pred in enumerate(predictions):
        label = LABEL_MAP.get(pred, "O")
        word = ocr_words[idx]

        if label == "O":
            if current_field:
                field_data[current_field] = " ".join(current_value).strip()
                current_field = None
                current_value = []
        else:
            if current_field and current_field != label:
                field_data[current_field] = " ".join(current_value).strip()
                current_value = []
            current_field = label
            current_value.append(word)

    if current_field and current_value:
        field_data[current_field] = " ".join(current_value).strip()

    return field_data
