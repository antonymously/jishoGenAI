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


def _thinking_config(model: str, disable_thinking: bool):
    '''
    Return a ThinkingConfig that turns thinking off, or None when not applicable.

    Gemini thinking models accept thinking_budget=0 to disable reasoning.
    Non-Gemini models (e.g. Gemma) do not support the field, so we skip them.
    '''
    if not disable_thinking:
        return None
    if not (model or "").startswith("gemini-"):
        return None
    return types.ThinkingConfig(thinking_budget=0)


class GeminiChatLLM(ChatLLM):

    def __init__(
        self,
        system_message: str = "You are a helpful assistant.",
        model: str = DEFAULT_GEMINI_MODEL,
        api_key: Optional[str] = None,
        disable_thinking: bool = True,
    ):
        super().__init__(system_message)
        self.model = model
        self.api_key = api_key
        self.disable_thinking = disable_thinking
        self.reset_chat()

    def reset_chat(self):
        config_kwargs = {"system_instruction": self.system_message}
        thinking_config = _thinking_config(self.model, self.disable_thinking)
        if thinking_config is not None:
            config_kwargs["thinking_config"] = thinking_config

        self.chat = get_gemini_client(self.api_key).chats.create(
            model = self.model,
            config = types.GenerateContentConfig(**config_kwargs),
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
        disable_thinking: bool = True,
    ):
        self.model = model
        self.system_message = system_message
        self.api_key = api_key
        self.disable_thinking = disable_thinking

    def invoke(self, contents: list) -> str:
        '''
        contents can include text and images in the prompt
        '''
        thinking_config = _thinking_config(self.model, self.disable_thinking)

        def _generate(thinking):
            config_kwargs = {"system_instruction": self.system_message}
            if thinking is not None:
                config_kwargs["thinking_config"] = thinking
            return get_gemini_client(self.api_key).models.generate_content(
                model = self.model,
                config = types.GenerateContentConfig(**config_kwargs),
                contents = contents,
            )

        try:
            response = _generate(thinking_config)
        except Exception:
            if thinking_config is None:
                raise
            # Some models reject a thinking config; retry once without it.
            response = _generate(None)
        return response.text