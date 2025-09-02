'''
Test using Gemini for OCR
'''
import sys
sys.path.append('.')

from PIL import Image
import json
from textwrap import dedent

from llm.gemini_llm import GeminiLLM

extraction_system_prompt = dedent('''
    An image will be provided, which will likely be a video game screen.
    Your job is to detect all the Japanese texts in the screen.

    Respond with a list of strings only. No extra text.
    The strings should contain the Japanese texts you see on the screen.

    EXAMPLE RESPONSE:
    [
        "今日は晴れですね",
        "名前はJOHNNYです"
    ]

    Include romanji characters in your extraction as long as it's in a Japanese context.
    Exclude any text that is completely not Japanese from your extraction.
''')

def main():

    # Load the image
    image_path = "./data/sample_screens/rune_factory.webp"
    image = Image.open(image_path)

    # gemini LLM
    llm = GeminiLLM(
        system_message = extraction_system_prompt
    )

    res = llm.invoke(
        contents = [
            "Image:",
            image
        ]
    )

    print(res)

if __name__ == "__main__":
    main()