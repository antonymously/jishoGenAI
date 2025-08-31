import sys
sys.path.append('.')
from llm.gemini_llm import GeminiLLM

def main():
    gemini_llm = GeminiLLM(
        system_message = "Translate provided Japanese text to English."
    )

    res = gemini_llm.invoke(["赤い本がある"])
    print(res)

if __name__ == "__main__":
    main()