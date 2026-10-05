# This file contains the core logic for the "sensei" layer
from textwrap import dedent
import json
from typing import Optional

from llm.base_llm import BaseLLM
from llm.utils import (
    PROVIDER_GEMINI,
    create_llm,
    get_default_model,
)
from ocr.ocr_engine import DetectedText
from .utils import trim_json_from_text

class SetsumeiSensei:
    '''
    Translates and/or explains text in the context of other detected text.
    '''

    def __init__(
        self,
        provider: str = PROVIDER_GEMINI,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        llm_cls = None,
        chat_llm_cls = None,
    ):
        self.provider = provider
        self.model = model or get_default_model(provider, "text")
        self.api_key = api_key
        # Optional explicit class override (kept for backwards compatibility).
        self.llm_cls = llm_cls
        self.chat_llm_cls = chat_llm_cls

        self.reset_texts()

        self.base_system_prompt = dedent('''
            You are an assistant to an English speaking Japanese LEARNER.
            The LEARNER is consuming Japanese media.
            The Japanese text from the media has been extracted via OCR.

            A TARGET TEXT will be provided.
            Translate the TARGET TEXT to English.

            Furthermore, other CONTEXT TEXTS that appear on screen may be provided.
        ''')

        self.target_words_instruction = dedent('''
            The TARGET TEXT may contain <target></target> tags.
            If so, you are only to translate and/or explain the text within the TARGET TAGS.
            The rest of the TARGET TEXT is provided only for context.

            For example:
                TARGET TEXT:
                私の<target>頭</target>が痛いですよ

                TRANSLATION:
                head
        ''')

        self.translate_only_system_prompt = self.base_system_prompt + dedent('''
            Respond in the following json format:
            {
                "translation": "<translation of the TARGET TEXT>"
            }

            As much as possible, include only the TARGET TEXT in your translation.
            Use the CONTEXT TEXTS to provide an accurate translation.
            You may assume that the CONTEXT TEXTS may be connected to the TARGET TEXT.
            But avoid including other CONTEXT TEXTS in the translation.
            Do not add any further text to your response outside of the json.
        ''')

        self.translate_explain_system_prompt = self.base_system_prompt + dedent('''
            Also add brief explanation of the translated text.
            Explain any language nuiances the LEARNER might not be familiar with.
            
            Respond in the following json format:
            {
                "translation": "<translation of the TARGET TEXT>",
                "explanation": "<brief explanation>"
            }

            As much as possible, include only the TARGET TEXT in your translation.
            You may refer to the CONTEXT TEXTS in the explanation.
            You may assume that the CONTEXT TEXTS may be connected to the TARGET TEXT.
            But avoid including other CONTEXT TEXTS in the translation.
            Do not add any further text to your response outside of the json.
        ''')

        self.merge_texts_system_prompt = dedent('''
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

        self.add_furigana_system_prompt = dedent('''
            Japanese TARGET TEXT will be provided.
            If it is not in Japanese, simply return the same text.

            If it is in Japanese, add furigana to any KANJI words in the text in parentheses.
            Do not add furigana to katakana or romanji words.
            Respond only with the Japanese text and furigana, adding nothing else.
            For example:

            TARGET TEXT: トイレならあの青い建物にあるよ
            RESPONSE: トイレならあの青い（あおい）建物（たてもの）にあるよ
        ''')

        self.llm_translate_explain = self._make_llm(
            self.translate_explain_system_prompt
        )

        self.llm_merge_texts = self._make_llm(
            self.merge_texts_system_prompt
        )

        self.llm_add_furigana = self._make_llm(
            self.add_furigana_system_prompt
        )

    def _make_llm(self, system_message: str) -> BaseLLM:
        '''
        Build a stateless LLM for the configured provider/model.

        Falls back to an explicit llm_cls override when one was provided.
        '''
        if self.llm_cls is not None:
            return self.llm_cls(
                model = self.model,
                system_message = system_message,
            )
        return create_llm(
            provider = self.provider,
            model = self.model,
            system_message = system_message,
            api_key = self.api_key,
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
        target_words: Optional[str] = None,
    ):
        '''
        Translate the detected text
        but in the context of other texts in the screen/game.

        The text itself may be included in the context,
        this should not be a major issue.

        Args:
            text
            explain: bool. Optional. If true, add extra explanation to the translation.
            add_text: bool. Optional. Whether to add the target_text to self.texts for future context.
            target_words str. Optional.
                it contains the same string as target_text
                but contains <target></target> on word/s to be translated
                ex.
                    私の<target>頭が痛い</target>ですよ。
        '''

        if add_text:
            self.add_texts([text])

        # set self.llm_translate_explain system prompt
        if target_words is not None:
            if explain:
                self.llm_translate_explain.set_system_message(
                    self.translate_explain_system_prompt + self.target_words_instruction
                )
            else:
                self.llm_translate_explain.set_system_message(
                    self.translate_only_system_prompt + self.target_words_instruction
                )
        else:
            if explain:
                self.llm_translate_explain.set_system_message(
                    self.translate_explain_system_prompt
                )
            else:
                self.llm_translate_explain.set_system_message(
                    self.translate_only_system_prompt
                )

        prompt = dedent('''
            TARGET TEXT:
            {target_text}
            CONTEXT TEXTS:
            {context_texts}
        ''').format(
            target_text = target_text.text,
            context_texts = "\n".join([ct.text for ct in self.texts]),
        )

        res = self.llm_translate_explain.invoke([prompt])


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
        
    def add_furigana(
        self, 
        target_text: DetectedText,
    ):

        prompt = dedent('''
            {target_text}
        ''').format(
            target_text = target_text.text,
        )

        res = self.llm_add_furigana.invoke([prompt])

        return res

        



