'''
OpenRouter LLM implementation.

OpenRouter exposes an OpenAI-compatible chat completions API, so we reuse the
official `openai` client pointed at the OpenRouter base URL.

Docs:
    - https://openrouter.ai/docs/quickstart
    - https://openrouter.ai/docs/features/multimodal/overview
'''
import base64
import io
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

from llm.base_llm import BaseLLM, ChatLLM

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# A cheap, widely available multimodal model as the default.
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"


def get_openrouter_client(api_key: Optional[str] = None) -> OpenAI:
    '''
    Build an OpenAI-compatible client for OpenRouter.

    The API key is resolved at call time (explicit argument -> OPENROUTER_API_KEY
    environment variable) so importing this module never requires a key.
    '''
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError(
            "OPENROUTER_API_KEY not found. Add it to your .env file or provide it in settings."
        )
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=key)


def _image_to_data_url(image: Image.Image) -> str:
    '''Encode a PIL image as a base64 PNG data URL.'''
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _build_user_content(contents) -> list:
    '''
    Convert the app's generic `contents` list (strings and PIL images, e.g.
    ["Image:", <PIL.Image>]) into OpenAI-style content parts.
    '''
    if isinstance(contents, str):
        contents = [contents]

    parts = []
    for item in contents:
        if isinstance(item, Image.Image):
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": _image_to_data_url(item)},
                }
            )
        else:
            parts.append({"type": "text", "text": str(item)})
    return parts


def _optional_headers() -> dict:
    '''Optional attribution headers recommended by OpenRouter.'''
    headers = {}
    referer = os.getenv("OPENROUTER_SITE_URL")
    title = os.getenv("OPENROUTER_APP_NAME")
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title
    return headers


class OpenRouterLLM(BaseLLM):
    '''
    A stateless LLM for single-turn conversations via OpenRouter.
    Supports text and image inputs.
    '''

    def __init__(
        self,
        system_message: str = "You are a helpful assistant.",
        model: str = DEFAULT_OPENROUTER_MODEL,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.system_message = system_message
        self.api_key = api_key

    def invoke(self, contents) -> str:
        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append({"role": "user", "content": _build_user_content(contents)})

        response = get_openrouter_client(self.api_key).chat.completions.create(
            model = self.model,
            messages = messages,
            extra_headers = _optional_headers() or None,
        )
        return response.choices[0].message.content or ""


class OpenRouterChatLLM(ChatLLM):
    '''
    A stateful chat LLM via OpenRouter. Chat history is retained in the object.
    '''

    def __init__(
        self,
        system_message: str = "You are a helpful assistant.",
        model: str = DEFAULT_OPENROUTER_MODEL,
        api_key: Optional[str] = None,
    ):
        super().__init__(system_message)
        self.model = model
        self.api_key = api_key
        self.reset_chat()

    def reset_chat(self):
        self.history = []
        if self.system_message:
            self.history.append({"role": "system", "content": self.system_message})

    def invoke(self, prompt: str) -> str:
        self.history.append({"role": "user", "content": _build_user_content(prompt)})

        response = get_openrouter_client(self.api_key).chat.completions.create(
            model = self.model,
            messages = self.history,
            extra_headers = _optional_headers() or None,
        )
        message = response.choices[0].message
        self.history.append({"role": "assistant", "content": message.content})
        return message.content or ""
