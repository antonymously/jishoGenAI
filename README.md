# jishoGenAI
AI companion for English speakers learning Japanese by playing video games in Japanese text. Runs on Windows.

'JishoGenai' is a play on words - 辞書じゃない (jisho jyanai) means 'not a dictionary'. Because it is not simply a dictionary that looks up the direct translation of the in-game text, but uses AI to explain the meaning and usage in context.

## TODO

- [x] Make functionality to merge detected texts by bounding box or semantics
- [x] Add a separate modal/screen for settings and configurations
- [ ] Add options to use screenshot as additional context to text merging, translation and explanation. Use GeminiLLM class and add the image to the contents during invoke().
- [ ] Make LLM invocations asynchronous
- [ ] Add a full sentence/phrase output with furigana
- [ ] Generate a nice logo.
- [ ] Add screenshots and sample footage to readme
- [ ] Add usage guide to readme
- [ ] Add more memory to Setsumei Sensei. Recall text from previous screens to gain more context.
- [ ] Allow user to highlight/select text to be explained if it is a substring of the detected text.
- [ ] Allow user to ask follow-up questions on the explanation of Setsumei Sensei.
- [ ] Option to capture specific game screen rather than full monitor screen.
- [ ] Option to use the screenshot image as context.
- [ ] Option to automatically screenshot and analyze while gameplay is happening.
- [ ] Configurations for current learning level of user.
- [ ] Allow use of other LLM providers.
- [ ] Allow use of local LLM.
- [ ] Provide alternative OCR options.

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

### 4. Set up Gemini API Key

jishoGenAI uses the Gemini API for its language model. You'll need to obtain an API key from Google AI Studio.

1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Create a new API key.
3.  Create a file named `.env` in the root directory of the project (where `app.py` and `requirements.txt` are located).
4.  Add your Gemini API key to the `.env` file in the following format:

    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    Replace `"YOUR_GEMINI_API_KEY_HERE"` with the actual API key you obtained.

### 5. Run the Application

Once all dependencies are installed and your API key is set up, you can run the Streamlit application:

```bash
streamlit run app.py
```

Your browser should automatically open to the jishoGenAI application.
