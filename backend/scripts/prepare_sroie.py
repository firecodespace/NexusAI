import os
from tqdm import tqdm
from PIL import Image
import pytesseract
from datasets import Dataset, DatasetDict
from transformers import LayoutLMv3Processor

# Paths
IMAGE_DIR = "datasets/sroie/images"
LABEL_DIR = "datasets/sroie/annotations"

# Load processor (no OCR here)
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)

examples = []

def parse_labels(txt_path):
    labels = {}
    with open(txt_path, 'r') as f:
        for line in f:
            if ':' in line:
                key, val = line.split(':', 1)
                labels[key.strip().lower()] = val.strip()
    return labels

def normalize_box(box, width, height):
    return [
        int(1000 * (box[0] / width)),
        int(1000 * (box[1] / height)),
        int(1000 * (box[2] / width)),
        int(1000 * (box[3] / height)),
    ]

print("🔍 Processing invoice images...")

for filename in tqdm(os.listdir(IMAGE_DIR)):
    if not filename.endswith(".jpg"):
        continue

    img_path = os.path.join(IMAGE_DIR, filename)
    txt_path = os.path.join(LABEL_DIR, filename.replace(".jpg", ".txt"))

    if not os.path.exists(txt_path):
        continue

    labels = parse_labels(txt_path)
    image = Image.open(img_path).convert("RGB")
    width, height = image.size

    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    words = []
    boxes = []

    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        if not word:
            continue

        x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
        box = normalize_box([x, y, x + w, y + h], width, height)

        words.append(word)
        boxes.append(box)

    # Just pass raw labels for now
    examples.append({
        "id": filename,
        "image": image,
        "words": words,
        "boxes": boxes,
        "labels": labels
    })

# Create Hugging Face dataset
dataset = Dataset.from_list(examples)
dataset_dict = DatasetDict({"train": dataset})

# Save it
dataset.save_to_disk("datasets/sroie_tokenized")

print("✅ SROIE Dataset ready. Saved to: datasets/sroie_tokenized")
