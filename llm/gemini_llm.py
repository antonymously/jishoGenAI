import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from llm.base_llm import BaseLLM, ChatLLM

load_dotenv()

DEFAULT_GEMINI_MODEL = "gemini-flash-latest"

# NOTE: API reference here https://ai.google.dev/gemini-api/docs/text-generation


@lru_cache(maxsize=None)
def get_gemini_client(api_key: Optional[str] = None):
    '''
    Lazily build (and cache) the Gemini client.

    The client is created on first use rather than at import time so that the
    application can run without a GEMINI_API_KEY when another provider (e.g.
    OpenRouter) is selected.
    '''
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY not found. Add it to your .env file or provide it in settings."
        )
    return genai.Client(api_key=key)


class GeminiChatLLM(ChatLLM):

    def __init__(
        self,
        system_message: str = "You are a helpful assistant.",
        model: str = DEFAULT_GEMINI_MODEL,
        api_key: Optional[str] = None,
    ):
        super().__init__(system_message)
        self.model = model
        self.api_key = api_key
        self.reset_chat()

    def reset_chat(self):
        self.chat = get_gemini_client(self.api_key).chats.create(
            model = self.model,
            config = types.GenerateContentConfig(
                system_instruction = self.system_message
            ),
        )

    def invoke(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text


class GeminiLLM(BaseLLM):
    '''
    A stateless LLM for single-turn conversations.
    '''

    def __init__(
        self,
        system_message: str = "You are a helpful assistant.",
        model: str = DEFAULT_GEMINI_MODEL,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.system_message = system_message
        self.api_key = api_key

    def invoke(self, contents: list) -> str:
        '''
        contents can include text and images in the prompt
        '''

        response = get_gemini_client(self.api_key).models.generate_content(
            model = self.model,
            config = types.GenerateContentConfig(
                system_instruction = self.system_message,
            ),
            contents = contents,
        )
        return response.text