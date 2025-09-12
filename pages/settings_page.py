import streamlit as st
from utils.screens import get_monitors
from utils.settings_manager import save_settings

def settings_page():
    st.title("Settings")
    st.write("This is the settings page.")
    
    # Example settings (will be moved from settings_modal.py)
    monitors = get_monitors()
    available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]

    # NOTE: default to the 2nd screen
    selected_screen_value = st.selectbox(
        "Select a screen:",
        available_screens,
        index = st.session_state.get("selected_screen_index", 1), # Persist selection
        key="selected_screen_selectbox"
    )
    st.session_state.selected_screen_index = available_screens.index(selected_screen_value)
    st.session_state.selected_screen = selected_screen_value

    # Dropdown for OCR method
    ocr_methods = ["gemini", "easyocr"]
    selected_ocr_method = st.selectbox(
        "Select OCR Method:",
        ocr_methods,
        index=ocr_methods.index(st.session_state.get("ocr_method", "gemini")), # Persist selection, default to gemini
        key="ocr_method_selectbox"
    )
    st.session_state.ocr_method = selected_ocr_method

    def navigate_to_main():
        settings = {
            "selected_screen_index": st.session_state.selected_screen_index,
            "ocr_method": st.session_state.ocr_method,
            # Add other settings here as they are introduced
        }
        save_settings(settings)
        st.session_state.page = "main"
    st.button("Save", on_click=navigate_to_main)