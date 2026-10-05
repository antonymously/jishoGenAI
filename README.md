# jishoGenAI
AI companion for English speakers learning Japanese by playing video games in Japanese text. Runs on Windows.

'JishoGenai' is a play on words - 辞書じゃない (jisho jyanai) means 'not a dictionary'. Because it is not simply a dictionary that looks up the direct translation of the in-game text, but uses AI to explain the meaning and usage in context.

## Demo
[![jishoGenAI demo video](https://img.youtube.com/vi/rlpXhu6bODQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=rlpXhu6bODQ)

## TODO

- [x] Make functionality to merge detected texts by bounding box or semantics
- [x] Add output that shows the Japanese text with Furigana
- [ ] Add option to highlight substring for translation. NOTE: This seems difficult in native Streamlit
- [ ] On selection of detected text, tokenize it into words. Display these words below the detected text as additional options for translation.
- [ ] Add option to disable 'merged_texts'. Default to disabled.
- [x] Add function to use Gemini for OCR
- [ ] Allow ordered multi-select of detected texts prior to translation. Or add a translate mode 'single/multi' option
- [x] Add a separate modal/screen for settings and configurations
- [x] In settings page, add preview of the screen being captured
- [ ] Add options to use screenshot as additional context to text merging, translation and explanation. Use GeminiLLM class and add the image to the contents during invoke().
- [ ] Make LLM invocations asynchronous
- [ ] Generate a nice logo.
- [x] Add screenshots and sample footage to readme
- [ ] Add usage guide to readme
- [ ] Add more memory to Setsumei Sensei. Recall text from previous screens to gain more context.
- [ ] Allow user to highlight/select text to be explained if it is a substring of the detected text.
- [ ] Allow user to ask follow-up questions on the explanation of Setsumei Sensei.
- [ ] Option to automatically screenshot and analyze while gameplay is happening.
- [ ] Configurations for current learning level of user.
- [x] Allow use of other LLM providers (Gemini, OpenRouter).
- [ ] Allow use of local LLM.
- [ ] Provide alternative OCR options.
- [ ] Fine tune a small model for OCR on Japanese game screenshots.

## Installation and Setup

To get started with jishoGenAI, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/antonymously/jishoGenAI.git
cd jishoGenAI
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Set up API Key(s)

jishoGenAI can source its language and vision models from either Google Gemini or [OpenRouter](https://openrouter.ai/). Configure whichever provider(s) you want to use.

1.  Create a file named `.env` in the root directory of the project (where `app.py` and `requirements.txt` are located).
2.  Add the API key(s) you have in the following format:

    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY_HERE"
    ```

    - **Gemini**: obtain an API key from [Google AI Studio](https://aistudio.google.com/).
    - **OpenRouter**: obtain an API key from [openrouter.ai/keys](https://openrouter.ai/keys). You can also paste the OpenRouter key directly into the in-app **Settings** page (kept for the current session only).

### 5. Select a Provider and Model

Open the **Settings** page in the app to choose:

- **LLM Provider** — Google Gemini or OpenRouter.
- **LLM (text) Model** — used for translation, explanation, furigana, and text merging.
- **Vision Model (for OCR)** — used to read Japanese text from screenshots.

The OpenRouter model list is fetched live from OpenRouter's public models API; the Gemini list is curated. Your selections are saved to `settings.json`.

### 6. Run the Application

Once all dependencies are installed and your API key is set up, you can run the Streamlit application:

```bash
streamlit run app.py
```

Your browser should automatically open to the jishoGenAI application.
