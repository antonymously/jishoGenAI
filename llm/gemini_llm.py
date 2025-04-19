import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from llm.base_llm import ChatLLM

load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)

# NOTE: API reference here https://ai.google.dev/gemini-api/docs/text-generation
# TODO: test this
class GeminiLLM(ChatLLM):
    
    def __init__(
        self, 
        system_message: str = "You are a helpful assistant.",
        model: str = 'gemini-2.0-flash',
    ):
        super().__init__(system_message)
        self.model = model
        self.reset_chat()

    def reset_chat(self):
        self.chat = GEMINI_CLIENT.chats.create(
            model = self.model,
            config = types.GenerateContentConfig(
                system_instruction = self.system_message
            ),
        )

    def invoke(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text

    