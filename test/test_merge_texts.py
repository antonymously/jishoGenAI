import sys
sys.path.append('.')

from ocr.ocr_engine import extract_japanese_text_from_image
from PIL import Image
import json

from sensei.sensei_engine import SetsumeiSensei

def test_extract_japanese_text_from_image():
    """
    Tests the extract_japanese_text_from_image function.
    """

    # Load the image
    image_path = "./data/sample_screens/dragon_quest_11.jpg"
    image = Image.open(image_path)

    # Extract the text
    detected_texts = extract_japanese_text_from_image(image)
    for detected_text in detected_texts:
        print(detected_text)

    # select a target text
    target_text = detected_texts[-2]
    print("target text:", target_text.text)

    # construct setsumei sensei
    setsumei_sensei = SetsumeiSensei()

    # add context texts
    setsumei_sensei.add_texts(detected_texts)

    # get translation
    merged_texts = setsumei_sensei.merge_texts(detected_texts)

    for merged_text in merged_texts:
        print(merged_text.to_json())

if __name__ == "__main__":
    test_extract_japanese_text_from_image()