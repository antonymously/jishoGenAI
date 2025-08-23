import streamlit as st
import os
from utils.screens import screenshot_monitor
from utils.screens import get_monitors
from ocr.ocr_engine import extract_japanese_text_from_image, DetectedText

st.title("辞書GenAI")



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

if st.button("Analyze Screen"):
    # Clear previous texts and selected text when a new screenshot is taken
    st.session_state.detected_texts = []
    st.session_state.selected_text = None
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

# Display detected texts if available
if 'detected_texts' in st.session_state and st.session_state.detected_texts:
    st.subheader("Detected Japanese Texts:")
    
    # Create a scrollable area
    with st.container(height=500, gap=None):
        for i, detected_text in enumerate(st.session_state.detected_texts):
            is_selected = (st.session_state.selected_text == detected_text.text)
            button_type = "primary" if is_selected else "secondary"
            
            # Define a callback function for the button
            def set_selected_text(text):
                st.session_state.selected_text = text

            # Make each detected text clickable
            if st.button(
                detected_text.text,
                key=f"detected_text_{i}",
                type=button_type,
                on_click=set_selected_text,
                args=(detected_text.text,)
            ):
                st.write(f"You clicked: {detected_text.text}")
                # You can add more actions here, e.g., copy to clipboard, translate, etc.

