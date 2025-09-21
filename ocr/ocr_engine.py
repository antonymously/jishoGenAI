import os
import easyocr
from PIL import Image
import numpy as np
from typing import Optional, List
import json
from textwrap import dedent

from llm.gemini_llm import GeminiLLM

# Initialize EasyOCR reader
EASYOCR_READER = easyocr.Reader(['ja', 'en'])

# Gemini LLM system prompt for OCR
GEMINI_OCR_SYSTEM_PROMPT = dedent('''
    An image will be provided, which will likely be a video game screen.
    Your job is to detect all the Japanese texts in the screen.

    Respond with a list of strings only. No extra text.
    The strings should contain the Japanese texts you see on the screen.
    If the text on screen includes furigana, EXCLUDE FURIGANA from your detected response.

    EXAMPLE RESPONSE:
    [
        "今日は晴れですね",
        "名前はJOHNNYです"
    ]

    Include romanji characters in your extraction as long as it's in a Japanese context.
    Exclude any text that is completely not Japanese from your extraction.
''')

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
        confidence_str = f", Confidence: {self.confidence:.2f}" if self.confidence is not None else ""
        bbox_str = f", Bounding Box: {self.bounding_box}" if self.bounding_box is not None else ""
        return f"Text: {self.text}{confidence_str}{bbox_str}"

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

def _extract_japanese_text_with_easyocr(image: Image.Image, confidence_threshold: float = 0.5) -> List[DetectedText]:
    """
    Extracts Japanese text from an image object using EasyOCR.
    """
    detected_texts = []
    try:
        image_np = np.array(image)
        res = EASYOCR_READER.readtext(image_np)
        for detection in res:
            if detection[2] >= confidence_threshold:
                detected_texts.append(DetectedText(
                    bounding_box = detection[0],
                    text = detection[1],
                    confidence = detection[2],
                ))
    except Exception as e:
        print(f"Error extracting text with EasyOCR: {e}")
    return detected_texts

def _extract_japanese_text_with_gemini(image: Image.Image) -> List[DetectedText]:
    """
    Extracts Japanese text from an image object using Gemini LLM.
    """
    detected_texts = []
    try:
        llm = GeminiLLM(system_message=GEMINI_OCR_SYSTEM_PROMPT)
        res = llm.invoke(contents=["Image:", image])
        
        try:
            extracted_list = json.loads(res)
            if isinstance(extracted_list, list):
                for text_item in extracted_list:
                    if isinstance(text_item, str):
                        detected_texts.append(DetectedText(text=text_item))
            else:
                print(f"Gemini response was not a list: {res}")
        except json.JSONDecodeError:
            print(f"Could not parse Gemini response as JSON: {res}")
            if isinstance(res, str) and res.strip():
                detected_texts.append(DetectedText(text=res.strip()))

    except Exception as e:
        print(f"Error extracting text with Gemini: {e}")
    return detected_texts

def extract_japanese_text_from_image(image: Image.Image, method: str = "easyocr", confidence_threshold: float = 0.5) -> List[DetectedText]:
    """
    Extracts Japanese text from an image object using the specified OCR method.

    Args:
        image: A PIL Image object.
        method: The OCR method to use ("easyocr" or "gemini").
        confidence_threshold: Minimum confidence score for EasyOCR detections to be included.

    Returns:
        List[DetectedText]: A list of detected Japanese texts.
    """
    if method == "easyocr":
        return _extract_japanese_text_with_easyocr(image, confidence_threshold)
    elif method == "gemini":
        return _extract_japanese_text_with_gemini(image)
    else:
        print(f"Unknown OCR method: {method}")
        return []
