# This file contains the core logic for the "sensei" layer
from textwrap import dedent
import json

from llm.base_llm import ChatLLM
from llm.gemini_llm import GeminiLLM
from ocr.ocr_engine import DetectedText
from .utils import trim_json_from_text

class SetsumeiSensei:
    '''
    Translates and/or explains text in the context of other detected text.
    '''

    def __init__(
        self, 
        chat_llm_cls = GeminiLLM,
    ):

        self.reset_texts()

        base_system_prompt = dedent('''
            You are an assistant to an English speaking Japanese LEARNER.
            The LEARNER is consuming Japanese media.
            The Japanese text from the media has been extracted via OCR.

            A TARGET TEXT will be provided.
            Translate the TARGET TEXT to English.

            Furthermore, other CONTEXT TEXTS that have appeared previously may be provided.
            Use the CONTEXT TEXTS to provide an in-context translation of the TARGET TEXT.
        ''')

        translate_only_system_prompt = base_system_prompt + dedent('''
            Respond in the following json format:
            {
                "translation": "<translation of the TARGET TEXT>"
            }

            Do not add any further text to your resoponse outside of the json.
        ''')

        translate_explain_system_prompt = base_system_prompt + dedent('''
            Also add brief explanation of the translated text.
            Explain any language nuiances the LEARNER might not be familiar with.
            
            Respond in the following json format:
            {
                "translation": "<translation of the TARGET TEXT>",
                "explanation": "<brief explanation>"
            }

            Do not add any further text to your resoponse outside of the json.
        ''')

        self.llm_translate_only = chat_llm_cls(
            system_message = translate_only_system_prompt
        )

        self.llm_translate_explain = chat_llm_cls(
            system_message = translate_explain_system_prompt
        )

    def reset_texts(self):
        self.texts = []

    def add_texts(self, texts: list):
        self.texts += texts

    def translate_text(
        self, 
        target_text: DetectedText, 
        explain: bool = False,
        add_text: bool = False,
    ):
        '''
        Translate the detected text
        but in the context of other texts in the screen/game.

        The text itself may be included in the context,
        this should not be a major issue.

        Args:
            text
            explain: bool. If true, add extra explanation to the translation.
        '''
        # TODO: test this

        if add_text:
            self.add_texts([text])

        prompt = dedent('''
            TARGET TEXT:
            {target_text}
            CONTEXT TEXTS:
            {context_texts}
        ''').format(
            target_text = target_text.text,
            context_texts = "\n".join([ct.text for ct in self.texts]),
        )

        if explain:
            self.llm_translate_explain.reset_chat()
            res = self.llm_translate_explain.invoke(prompt = prompt)
        else:
            self.llm_translate_only.reset_chat()
            res = self.llm_translate_only.invoke(prompt = prompt)

        res_json = trim_json_from_text(res)
        res_dict = json.loads(res_json)

        return res_dict
        

        



