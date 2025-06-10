from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
from PIL import Image
import torch

# Load model and processor
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")

def prepare_inputs(tokens, boxes, image_path):
    image = Image.open(image_path).convert("RGB")

    # LayoutLMv3 expects list of lists (batch)
    words = [tokens]
    boxes = [boxes]

    encoding = processor(
        image,
        boxes=boxes,
        words=words,
        return_tensors="pt",
        padding="max_length",
        truncation=True
    )
    return encoding

def predict_fields(tokens, boxes, image_path):
    encoding = prepare_inputs(tokens, boxes, image_path)

    with torch.no_grad():
        outputs = model(**encoding)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)

    result = {}
    for idx, label_id in enumerate(predictions[0]):
        label = model.config.id2label[label_id.item()]
        if label != "O" and idx < len(tokens):
            key = label.replace("B-", "").replace("I-", "")
            if key not in result:
                result[key] = tokens[idx]
            else:
                result[key] += " " + tokens[idx]

    return result

