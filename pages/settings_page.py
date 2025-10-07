import streamlit as st
from utils.screens import get_monitors, screenshot_monitor
from utils.settings_manager import save_settings
from PIL import Image

def settings_page():
    st.title("Settings")
    st.write("This is the settings page.")

    monitors = get_monitors()
    available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]

    # Initialize session state for selected_screen_index if not already set
    if "selected_screen_index" not in st.session_state:
        st.session_state.selected_screen_index = 1 # Default to the second screen

    col1, col2 = st.columns([1, 1]) # Create two columns

    with col1:
        # Define a callback function for when the screen selection changes
        def on_screen_select_change():
            # The new value is automatically stored in st.session_state.selected_screen_selectbox
            new_selected_screen_value = st.session_state.selected_screen_selectbox
            st.session_state.selected_screen_index = available_screens.index(new_selected_screen_value)
            st.session_state.selected_screen = new_selected_screen_value
            update_screen_preview() # Call the preview update after session state is updated

        selected_screen_value = st.selectbox(
            "Select a screen:",
            available_screens,
            index = st.session_state.selected_screen_index, # Use the session state value
            key="selected_screen_selectbox",
            on_change=on_screen_select_change # Use the new callback
        )
        # Ensure selected_screen and selected_screen_index are updated on initial load or rerun
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

    with col2:
        # Placeholder for the screen preview
        screen_preview_placeholder = st.empty()

        def update_screen_preview():
            selected_monitor_index = st.session_state.get("selected_screen_index", 1)
            if 0 <= selected_monitor_index < len(monitors):
                monitor_to_capture = monitors[selected_monitor_index]
                try:
                    screenshot_pil = screenshot_monitor(monitor_to_capture)
                    # Resize image to 400px width, maintaining aspect ratio
                    width = 400
                    height = int(screenshot_pil.height * (width / screenshot_pil.width))
                    resized_screenshot = screenshot_pil.resize((width, height), Image.LANCZOS)
                    screen_preview_placeholder.image(resized_screenshot, caption=f"Preview of {available_screens[selected_monitor_index]}", use_container_width=False)
                except Exception as e:
                    screen_preview_placeholder.warning(f"Could not capture screen preview: {e}. Please ensure the application has the necessary permissions to capture your screen.")
            else:
                screen_preview_placeholder.info("No screen selected or available for preview.")
        update_screen_preview() # Call the update function initially after session state is set

    def navigate_to_main():
        settings = {
            "selected_screen_index": st.session_state.selected_screen_index,
            "ocr_method": st.session_state.ocr_method,
            # Add other settings here as they are introduced
        }
        save_settings(settings)
        st.session_state.page = "main"
    st.button("Save", on_click=navigate_to_main)