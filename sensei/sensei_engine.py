# This file contains the core logic for the "sensei" layer
from llm.base_llm import ChatLLM
from llm.gemini_llm import GeminiLLM
from ocr.ocr_engine import DetectedText

class SetsumeiSensei:
    '''
    Translates and/or explains text in the context of other detected text.
    '''

    def __init__(self, chat_llm: ChatLLM):

        self.chat_llm = chat_llm
        self.reset_texts()

    def reset_texts(self):
        self.texts = []

    def add_texts(self, texts: list):
        self.texts += texts

    def translate_text(self, text: DetectedText, explain: bool = False):
        '''
        Translate the detected text
        but in the context of other texts in the screen/game.

        The text itself may be included in the context,
        this should not be a major issue.

        Args:
            text
            explain: bool. If true, add extra explanation to the translation.
        '''
        pass



