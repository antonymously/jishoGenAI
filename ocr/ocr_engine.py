import os
import easyocr
from PIL import Image

READER = easyocr.Reader(['ja'])

class DetectedText:

    def __init__(self, bounding_box, text, confidence):
        self.bounding_box = bounding_box
        self.text = text
        self.confidence = confidence

    def __str__(self):
        return f"Text: {self.text}, Confidence: {self.confidence:.2f}, Bounding Box: {self.bounding_box}"

def extract_japanese_text_from_image(image, confidence_threshold = 0.5):
    """
    Extracts Japanese text from an image object using easyocr.

    Args:
        image: A PIL Image object.

    Returns:
        str: The extracted Japanese text.
    """
    try:
        res = READER.readtext(image)
        detected_texts = []
        for detection in res:
            if detection[2] >= confidence_threshold:
                detected_texts.append(DetectedText(
                    bounding_box = detection[0],
                    text = detection[1],
                    confidence = detection[2],
                ))

        return detected_texts
    except Exception as e:
        print(f"Error extracting text: {e}")
        return []
