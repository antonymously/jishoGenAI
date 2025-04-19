from llm.gemini_llm import GeminiLLM

def main():
    gemini_chat = GeminiLLM(
        system_message = "Translate provided Japanese text to English."
    )

    res = gemini_chat.invoke("赤い本がある")
    print(res)

if __name__ == "__main__":
    main()