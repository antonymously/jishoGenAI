import os
import easyocr
from PIL import Image
import numpy as np
from typing import Optional

READER = easyocr.Reader(['ja'])

class DetectedText:

    def __init__(
        self, 
        text: str, 
        bounding_box: Optional[list] = None, 
        confidence: Optional = None, 
    ):
        
        self.text = text
        self.bounding_box = bounding_box
        self.confidence = confidence

    def __str__(self):
        return f"Text: {self.text}, Confidence: {self.confidence:.2f}, Bounding Box: {self.bounding_box}"

    def to_json(self):
        if self.bounding_box is not None:
            bbox = [[int(pair[0]), int(pair[1])] for pair in self.bounding_box]
        else:
            bbox = None

        return {
            "text": self.text,
            "bounding_box": bbox,
            "confidence": self.confidence
        }

def extract_japanese_text_from_image(image, confidence_threshold = 0.5):
    """
    Extracts Japanese text from an image object using easyocr.

    Args:
        image: A PIL Image object.

    Returns:
        str: The extracted Japanese text.
    """
    try:
        # Convert PIL Image to numpy array as easyocr.Reader.readtext expects it
        image_np = np.array(image)
        res = READER.readtext(image_np)
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
