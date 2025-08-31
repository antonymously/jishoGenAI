# This file contains the core logic for the "sensei" layer
from textwrap import dedent
import json

from llm.base_llm import BaseLLM
from llm.gemini_llm import GeminiChatLLM, GeminiLLM
from ocr.ocr_engine import DetectedText
from .utils import trim_json_from_text

class SetsumeiSensei:
    '''
    Translates and/or explains text in the context of other detected text.
    '''

    def __init__(
        self,
        llm_cls = GeminiLLM,
        chat_llm_cls = GeminiChatLLM,
    ):
        self.llm_cls = llm_cls

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

        merge_texts_system_prompt = dedent('''
            You are an assistant that merges segmented text extracted via OCR.
            You will be provided with a list of text segments, each with its bounding box.
            Your task is to identify segments that belong to the same logical sentence or phrase and merge them.
            
            The texts will likely be in Japanese.
            Consider that the detected texts may include furigana.
            You do not have to include all the texts in your outputs.
            Include only those that make sense as logical sentences or phrases.

            Respond in the following json format:
            [
                {
                    "text": "<merged text 1>",
                },
                {
                    "text": "<merged text 2>",
                }
            ]
            Do not add any further text to your response outside of the json.
        ''')

        self.llm_translate_only = self.llm_cls(
            model = 'gemini-1.5-flash',
            system_message = translate_only_system_prompt
        )

        self.llm_translate_explain = self.llm_cls(
            model = 'gemini-1.5-flash',
            system_message = translate_explain_system_prompt
        )

        self.llm_merge_texts = self.llm_cls(
            model = 'gemini-1.5-flash',
            system_message = merge_texts_system_prompt
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
            res = self.llm_translate_explain.invoke([prompt])
        else:
            res = self.llm_translate_only.invoke([prompt])

        res_json = trim_json_from_text(res)
        res_dict = json.loads(res_json)

        return res_dict

    def merge_texts(
        self,
        texts: list[DetectedText],
    ):
        '''
        Uses an LLM to merge segmented detected texts
        that belong to the same sentence.
        '''
        if not texts:
            return []

        text_segments_for_llm = []
        for i, dt in enumerate(texts):
            text_segments_for_llm.append(json.dumps(dt.to_json(), indent = 4))
        
        prompt = dedent('''
            Merge the following text segments. Each segment includes its text and bounding box.
            {segments}
        ''').format(
            segments = "\n".join(text_segments_for_llm)
        )

        res = self.llm_merge_texts.invoke([prompt])

        res_json = trim_json_from_text(res)
        merged_texts_data = json.loads(res_json)

        merged_detected_texts = []
        for item in merged_texts_data:
            merged_detected_texts.append(DetectedText(text=item['text']))
        
        return merged_detected_texts
        

        



