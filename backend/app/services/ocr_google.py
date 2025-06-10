import os
print("🔐 Google Key Path:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

from google.cloud import vision
from app.services.layoutlm_runner import predict_fields

def run_google_vision_and_layoutlm(image_path: str):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as f:
        content = f.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    tokens, boxes = [], []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for para in block.paragraphs:
                for word in para.words:
                    text = ''.join([s.text for s in word.symbols])
                    if not text.strip():
                        continue
                    tokens.append(text)
                    box = word.bounding_box
                    x0 = int(min(v.x for v in box.vertices) * 1000)
                    y0 = int(min(v.y for v in box.vertices) * 1000)
                    x1 = int(max(v.x for v in box.vertices) * 1000)
                    y1 = int(max(v.y for v in box.vertices) * 1000)
                    boxes.append([x0, y0, x1, y1])

    print("🧾 Tokens:", tokens[:15])
    print("📦 Boxes:", boxes[:15])

    # LayoutLMv3 model prediction
    fields = predict_fields(tokens, boxes, image_path)
    return fields