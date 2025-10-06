import streamlit as st
from utils.windows import get_open_windows
from utils.settings_manager import save_settings

def settings_page():
    st.title("Settings")
    st.write("This is the settings page.")
    
    # Example settings (will be moved from settings_modal.py)
    # --- Window Selection ---
    open_windows = get_open_windows()
    if not open_windows:
        st.warning("No open windows detected. Please open some applications.")
        available_windows = ["No windows available"]
        selected_window_value = "No windows available"
        selected_window_index = 0 # Keep for consistency, though not strictly used for window
    else:
        available_windows = open_windows
        # Try to persist selection, default to the first available window
        default_index = 0
        if "selected_window_title" in st.session_state and st.session_state.selected_window_title in available_windows:
            default_index = available_windows.index(st.session_state.selected_window_title)

        selected_window_value = st.selectbox(
            "Select a window:",
            available_windows,
            index=default_index,
            key="selected_window_selectbox"
        )
        # Update the index based on the selected value
        selected_window_index = available_windows.index(selected_window_value) if selected_window_value in available_windows else 0

    # Store the selected window title and a dummy index in session state
    st.session_state.selected_window_index = selected_window_index # Keep for compatibility if needed elsewhere
    st.session_state.selected_window_title = selected_window_value

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
            "selected_window_title": st.session_state.selected_window_title, # SAVE THE SELECTED WINDOW TITLE
            "ocr_method": st.session_state.ocr_method,
            # Add other settings here as they are introduced
        }
        save_settings(settings)
        st.session_state.page = "main"
    st.button("Save", on_click=navigate_to_main)