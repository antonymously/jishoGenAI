import streamlit as st
import os
from utils.screens import screenshot_monitor
from utils.screens import get_monitors
from ocr.ocr_engine import extract_japanese_text_from_image, DetectedText
from sensei.sensei_engine import SetsumeiSensei

st.set_page_config(layout="wide")
st.title("辞書GenAI")

if "sensei_engine" not in st.session_state:
    st.session_state.sensei_engine = SetsumeiSensei()

left_column, right_column = st.columns(2)

with left_column:
    monitors = get_monitors()
    available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]

    # NOTE: default to the 2nd screen
    selected_screen = st.selectbox(
        "Select a screen:",
        available_screens,
        index = 1,
    )

    if "detected_texts" not in st.session_state:
        st.session_state.detected_texts = []
    if "selected_text" not in st.session_state:
        st.session_state.selected_text = None
    if "translation" not in st.session_state:
        st.session_state.translation = "Placeholder for translation"
    if "explanation" not in st.session_state:
        st.session_state.explanation = "Placeholder for explanation"
    if "translation" not in st.session_state:
        st.session_state.translation = "Placeholder for translation"
    if "explanation" not in st.session_state:
        st.session_state.explanation = "Placeholder for explanation"

    if st.button("Analyze Screen"):
        # Clear previous texts, selected text, translation, and explanation when a new screenshot is taken
        st.session_state.detected_texts = []
        st.session_state.selected_text = None
        st.session_state.translation = "Placeholder for translation"
        st.session_state.explanation = "Placeholder for explanation"
        # Get the index of the selected screen
        selected_index = available_screens.index(selected_screen)
        
        # Get the monitor dictionary for the selected screen
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
        detected_texts = extract_japanese_text_from_image(screenshot_img)

        # Store detected texts in session state
        st.session_state.detected_texts = detected_texts
        st.session_state.merged_texts = st.session_state.sensei_engine.merge_texts(detected_texts)

    # Display detected sentences/phrases if available
    if 'merged_texts' in st.session_state and st.session_state.merged_texts:
        st.subheader("Detected Japanese Sentences/Phrases:")
        with st.container(height=250, gap=None):
            for i, merged_text in enumerate(st.session_state.merged_texts):
                is_selected = (st.session_state.selected_text == merged_text.text)
                button_type = "primary" if is_selected else "secondary"

                def set_selected_text_merged(dt: DetectedText):
                    st.session_state.selected_text = dt.text
                    sensei = st.session_state.sensei_engine
                    sensei.reset_texts()
                    sensei.add_texts(st.session_state.detected_texts) # Use original detected texts as context
                    
                    result = sensei.translate_text(dt, explain=True)
                    st.session_state.translation = result.get("translation", "Translation not available.")
                    st.session_state.explanation = result.get("explanation", "Explanation not available.")

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
        st.subheader("Detected Japanese Texts (Individual):")
        
        # Create a scrollable area
        with st.container(height=300, gap=None):
            for i, detected_text in enumerate(st.session_state.detected_texts):
                is_selected = (st.session_state.selected_text == detected_text.text)
                button_type = "primary" if is_selected else "secondary"
                
                # Define a callback function for the button
                def set_selected_text(dt: DetectedText):
                    st.session_state.selected_text = dt.text
                    sensei = st.session_state.sensei_engine
                    sensei.reset_texts()
                    sensei.add_texts(st.session_state.detected_texts)
                    
                    result = sensei.translate_text(dt, explain=True)
                    st.session_state.translation = result.get("translation", "Translation not available.")
                    st.session_state.explanation = result.get("explanation", "Explanation not available.")
    
                # Make each detected text clickable
                if st.button(
                    detected_text.text,
                    key=f"detected_text_{i}",
                    type=button_type,
                    on_click=set_selected_text,
                    args=(detected_text,)
                ):
                    st.write(f"You clicked: {detected_text.text}")
                    # The translation and explanation will be updated by the callback

with right_column:
    st.subheader("Translation")
    st.text_area("Translation", st.session_state.translation, height=200, label_visibility="collapsed")
    st.subheader("Explanation")
    st.text_area("Explanation", st.session_state.explanation, height=300, label_visibility="collapsed")

