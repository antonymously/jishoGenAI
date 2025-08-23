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
    translation = setsumei_sensei.translate_text(
        target_text,
        add_text = False,
    )
    print(translation)

    # get translation with explanation
    translation = setsumei_sensei.translate_text(
        target_text,
        explain = True,
        add_text = False,
    )
    print(translation)

if __name__ == "__main__":
    test_extract_japanese_text_from_image()