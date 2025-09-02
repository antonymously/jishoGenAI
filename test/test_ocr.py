import sys
sys.path.append('.')

from ocr.ocr_engine import extract_japanese_text_from_image
from PIL import Image
import json

def test_extract_japanese_text_from_image():
    """
    Tests the extract_japanese_text_from_image function.
    """

    # Load the image
    image_path = "./data/sample_screens/dragon_quest_11.jpg"
    image = Image.open(image_path)

    # Extract the text
    res = extract_japanese_text_from_image(image, method = "gemini")
    for detected_text in res:
        print(detected_text)

if __name__ == "__main__":
    test_extract_japanese_text_from_image()
