import streamlit as st
import os
from utils.screens import screenshot_monitor
from ocr.ocr_engine import extract_japanese_text_from_image, DetectedText
from sensei.sensei_engine import SetsumeiSensei
from pages.settings_page import settings_page
from utils.screens import get_monitors # Import get_monitors here
from utils.settings_manager import load_settings
from sensei.utils import tokenize_japanese_text # Import the new tokenizer
from utils.helper import label_target_words

st.set_page_config(layout="wide")

# Load settings on startup
initial_settings = load_settings()

if "page" not in st.session_state:
    st.session_state.page = "main"

# Initialize session state with loaded settings or defaults
if "selected_screen_index" not in st.session_state:
    st.session_state.selected_screen_index = initial_settings.get("selected_screen_index", 1) # Default to the 2nd screen
if "ocr_method" not in st.session_state:
    st.session_state.ocr_method = initial_settings.get("ocr_method", "gemini") # Default to Gemini

def update_translation_display():
    # DONE: simply provide target_words as target_text

    if st.session_state.selected_text:
        sensei = st.session_state.sensei_engine
        sensei.reset_texts()
        sensei.add_texts(st.session_state.detected_texts)

        target_words_input = None
        if st.session_state.selected_word_idxs:

            start_idx = min(st.session_state.selected_word_idxs)
            end_idx = max(st.session_state.selected_word_idxs)

            target_words_input = "".join(
                st.session_state.tokenized_words[start_idx:end_idx + 1]
            )

        current_detected_text = None
        for dt in st.session_state.detected_texts:
            if dt.text == st.session_state.selected_text:
                current_detected_text = dt
                break
        
        if current_detected_text:
            if st.session_state.selected_word_idxs:
                target_word_dt = DetectedText(
                    text = target_words_input
                )
                result = sensei.translate_text(
                    target_word_dt, 
                    explain=True, 
                )
                reading = sensei.add_furigana(target_word_dt)
            else:
                result = sensei.translate_text(
                    current_detected_text, 
                    explain=True, 
                )
                reading = sensei.add_furigana(current_detected_text)
            st.session_state.translation = result.get("translation", "Translation not available.")
            st.session_state.explanation = result.get("explanation", "Explanation not available.")
            st.session_state.reading = reading
        else:
            st.session_state.translation = "Error: Selected text not found in detected texts."
            st.session_state.explanation = "Error: Selected text not found in detected texts."
            st.session_state.reading = "Error: Selected text not found in detected texts."
    else:
        st.session_state.translation = "Placeholder for translation"
        st.session_state.explanation = "Placeholder for explanation"
        st.session_state.reading = "Placeholder for reading"

def main_page():
    header_cols = st.columns([0.8, 0.2])
    with header_cols[0]:
        st.title("辞書GenAI")
    with header_cols[1]:
        def navigate_to_settings():
            st.session_state.page = "settings"
        st.button("Settings", on_click=navigate_to_settings)

    if "sensei_engine" not in st.session_state:
        st.session_state.sensei_engine = SetsumeiSensei()

    # Initialize session state for screen selection if not already present
    if "selected_screen" not in st.session_state:
        monitors = get_monitors()
        available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]
        st.session_state.selected_screen = available_screens[st.session_state.selected_screen_index]

    left_column, right_column = st.columns(2)

    with left_column:
        if "detected_texts" not in st.session_state:
            st.session_state.detected_texts = []
        if "selected_text" not in st.session_state:
            st.session_state.selected_text = None
        if "translation" not in st.session_state:
            st.session_state.translation = "Placeholder for translation"
        if "explanation" not in st.session_state:
            st.session_state.explanation = "Placeholder for explanation"
        if "selected_word_idxs" not in st.session_state:
            st.session_state.selected_word_idxs = []
        if "reading" not in st.session_state:
            st.session_state.reading = "Placeholder for reading"

        if st.button("Analyze Screen"):
            # Clear previous texts, selected text, translation, and explanation when a new screenshot is taken
            st.session_state.detected_texts = []
            st.session_state.selected_text = None
            st.session_state.translation = "Placeholder for translation"
            st.session_state.explanation = "Placeholder for explanation"
            st.session_state.reading = "Placeholder for reading"
            
            # Get the monitor dictionary for the selected screen
            monitors = get_monitors()
            selected_index = st.session_state.selected_screen_index
            monitor_to_screenshot = monitors[selected_index]
            
            # Take the screenshot
            screenshot_img = screenshot_monitor(monitor_to_screenshot)
            
            # Define the save path
            screenshot_dir = "./data/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            save_path = os.path.join(screenshot_dir, "test_app_screenshot.png")
            
            # Save the screenshot
            screenshot_img.save(save_path)

            # Perform OCR on the screenshot
            detected_texts = extract_japanese_text_from_image(screenshot_img, method=st.session_state.ocr_method)

            # Store detected texts in session state
            st.session_state.detected_texts = detected_texts
            if st.session_state.ocr_method != "gemini":
                st.session_state.merged_texts = st.session_state.sensei_engine.merge_texts(detected_texts)
            else:
                st.session_state.merged_texts = [] # Clear merged texts if Gemini is used

        # Display detected sentences/phrases if available
        if st.session_state.ocr_method != "gemini" and 'merged_texts' in st.session_state and st.session_state.merged_texts:
            st.subheader("Detected Japanese Sentences/Phrases:")
            with st.container(height=250, gap=None):
                for i, merged_text in enumerate(st.session_state.merged_texts):
                    is_selected = (st.session_state.selected_text == merged_text.text)
                    button_type = "primary" if is_selected else "secondary"

                    def set_selected_text_merged(dt: DetectedText):
                        st.session_state.selected_text = dt.text
                        st.session_state.selected_word_idxs = [] # Clear word selection when a new sentence is selected
                        update_translation_display()

                    if st.button(
                        merged_text.text,
                        key=f"merged_text_{i}",
                        type=button_type,
                        on_click=set_selected_text_merged,
                        args=(merged_text,)
                    ):
                        st.write(f"You clicked: {merged_text.text}")

        # Display detected texts if available
        if 'detected_texts' in st.session_state and st.session_state.detected_texts:
            st.subheader("Detected Japanese Texts:")
            
            # Create a scrollable area
            with st.container(height=500, gap=None):
                for i, detected_text in enumerate(st.session_state.detected_texts):
                    is_selected = (st.session_state.selected_text == detected_text.text)
                    button_type = "primary" if is_selected else "secondary"
                    
                    # Define a callback function for the button
                    def set_selected_text(dt: DetectedText):
                        st.session_state.selected_text = dt.text
                        st.session_state.selected_word_idxs = [] # Clear word selection when a new text is selected
                        
                        # tokenize words and set to state
                        words = tokenize_japanese_text(st.session_state.selected_text)
                        st.session_state.tokenized_words = words
                        
                        update_translation_display()
        
                    # Make each detected text clickable
                    if st.button(
                        detected_text.text,
                        key=f"detected_text_{i}",
                        type=button_type,
                        on_click=set_selected_text,
                        args=(detected_text,)
                    ):
                        st.write(f"You clicked: {detected_text.text}")

        # Display tokenized words if a text is selected
        if st.session_state.selected_text:
            # DONE: capture the selected word/s
                # save the selected indices st.session_state.selected_word_idxs

            # DONE: make a utility function in utils.helper.py
                # that takes the selected_text and the selected_word_idxs
                # outputs a string such that the selected text is in <target></target> tags
                # ex.
                    # 私の<target>頭が痛い</target>ですよ。
                # if the selected words are dis-joint
                    # wrap them as if they are joint
                    # include all words in between in the target
                    # but maintain the selected indices in selected_word_idxs

            st.subheader("Individual Words:")

            # Create a container
            with st.container(
                height = "content", 
                horizontal = True,
                gap = None,
            ):
                # add buttons for the words
                for i, word in enumerate(st.session_state.tokenized_words):
                    is_word_selected = i in st.session_state.selected_word_idxs
                    button_type = "primary" if is_word_selected else "secondary"

                    # NOTE: target_text is not working well
                        # let's just provide the selected words as the target_text
                        # and leave the rest to context

                    def toggle_word_selection(word_idx):
                        if word_idx in st.session_state.selected_word_idxs:
                            st.session_state.selected_word_idxs.remove(word_idx)
                        else:
                            st.session_state.selected_word_idxs.append(word_idx)
                        st.session_state.selected_word_idxs.sort() # Keep indices sorted
                        update_translation_display() # Trigger translation update

                    st.button(
                        word,
                        key=f"word_{i}",
                        type=button_type,
                        on_click=toggle_word_selection,
                        args=(i,)
                    )

                # TEMP
                # st.write(f"Selected word indices: {st.session_state.selected_word_idxs}")
                # st.write("Target Words:", label_target_words(
                #     st.session_state.selected_text,
                #     st.session_state.selected_word_idxs,
                # ))

    with right_column:
        st.subheader("Reading")
        st.text_area("Reading", st.session_state.reading, height=100, label_visibility="collapsed")
        st.subheader("Translation")
        st.text_area("Translation", st.session_state.translation, height=200, label_visibility="collapsed")
        st.subheader("Explanation")
        st.text_area("Explanation", st.session_state.explanation, height=300, label_visibility="collapsed")

def app():
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "settings":
        settings_page()

app()

