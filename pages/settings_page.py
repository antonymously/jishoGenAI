import os

import streamlit as st
from PIL import Image

from utils.screens import get_monitors, screenshot_monitor
from utils.settings_manager import save_settings
from llm.utils import (
    PROVIDERS,
    PROVIDER_API_KEY_ENV,
    PROVIDER_LABELS,
    PROVIDER_OPENROUTER,
    get_models,
    resolve_model,
)


def settings_page():
    st.title("Settings")
    st.write("This is the settings page.")

    monitors = get_monitors()
    available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]

    # Initialize session state for selected_screen_index if not already set
    if "selected_screen_index" not in st.session_state:
        st.session_state.selected_screen_index = 1  # Default to the second screen

    col1, col2 = st.columns([1, 1])  # Create two columns

    with col1:
        # Define a callback function for when the screen selection changes
        def on_screen_select_change():
            # The new value is automatically stored in st.session_state.selected_screen_selectbox
            new_selected_screen_value = st.session_state.selected_screen_selectbox
            st.session_state.selected_screen_index = available_screens.index(new_selected_screen_value)
            st.session_state.selected_screen = new_selected_screen_value
            update_screen_preview()  # Call the preview update after session state is updated

        selected_screen_value = st.selectbox(
            "Select a screen:",
            available_screens,
            index = st.session_state.selected_screen_index,  # Use the session state value
            key="selected_screen_selectbox",
            on_change=on_screen_select_change  # Use the new callback
        )
        # Ensure selected_screen and selected_screen_index are updated on initial load or rerun
        st.session_state.selected_screen_index = available_screens.index(selected_screen_value)
        st.session_state.selected_screen = selected_screen_value

        st.divider()

        # Dropdown for OCR method
        ocr_methods = ["llm", "easyocr"]
        stored_ocr_method = st.session_state.get("ocr_method", "llm")
        if stored_ocr_method == "gemini":  # migrate legacy value
            stored_ocr_method = "llm"
        selected_ocr_method = st.selectbox(
            "Select OCR Method:",
            ocr_methods,
            index=ocr_methods.index(stored_ocr_method) if stored_ocr_method in ocr_methods else 0,
            key="ocr_method_selectbox"
        )
        st.session_state.ocr_method = selected_ocr_method

        # Toggle: shrink the screenshot before sending it to the vision model.
        # Speeds up OCR (smaller upload + fewer image tokens) but can hurt
        # accuracy on very small on-screen text, so it stays user-controllable.
        st.session_state.downscale_screenshot = st.checkbox(
            "Downscale screenshot before OCR (faster)",
            value=st.session_state.get("downscale_screenshot", True),
            key="downscale_screenshot_checkbox",
            help="Shrinks the screenshot to 1280px on its longest side before the vision "
                 "model sees it. Turn this off if OCR accuracy drops on small text. "
                 "Only affects the 'llm' OCR method; EasyOCR always runs at full resolution.",
        )

        st.divider()

        # Dropdown for the LLM provider (Gemini or OpenRouter)
        current_provider = st.session_state.get("llm_provider", PROVIDERS[0])
        if current_provider not in PROVIDERS:
            current_provider = PROVIDERS[0]
        selected_provider = st.selectbox(
            "LLM Provider:",
            PROVIDERS,
            index=PROVIDERS.index(current_provider),
            format_func=lambda p: PROVIDER_LABELS.get(p, p),
            key="llm_provider_selectbox",
        )
        st.session_state.llm_provider = selected_provider

        # Dropdown for the text LLM model (depends on the selected provider)
        text_models = get_models(selected_provider, "text")
        current_text_model = resolve_model(selected_provider, st.session_state.get("llm_model"), "text")
        selected_text_model = st.selectbox(
            "LLM (text) Model:",
            text_models,
            index=text_models.index(current_text_model) if current_text_model in text_models else 0,
            key=f"llm_model_selectbox_{selected_provider}",
        )
        st.session_state.llm_model = selected_text_model

        # Dropdown for the vision model used for OCR / image understanding
        vision_models = get_models(selected_provider, "vision")
        current_vision_model = resolve_model(selected_provider, st.session_state.get("vision_model"), "vision")
        selected_vision_model = st.selectbox(
            "Vision Model (for OCR):",
            vision_models,
            index=vision_models.index(current_vision_model) if current_vision_model in vision_models else 0,
            key=f"vision_model_selectbox_{selected_provider}",
        )
        st.session_state.vision_model = selected_vision_model

        # API key handling for OpenRouter (the Gemini key is read from .env only)
        if selected_provider == PROVIDER_OPENROUTER:
            st.divider()
            st.subheader("OpenRouter API Key")
            env_key = os.getenv(PROVIDER_API_KEY_ENV[PROVIDER_OPENROUTER])
            if env_key:
                st.caption("An OpenRouter API key was found in your environment (.env).")
            else:
                st.caption("No OPENROUTER_API_KEY found in your environment. Enter one below to use OpenRouter for this session.")

            if "openrouter_api_key" not in st.session_state:
                st.session_state.openrouter_api_key = ""
            st.text_input(
                "OpenRouter API Key:",
                type="password",
                key="openrouter_api_key",
                help="Session-only override. For persistence, add OPENROUTER_API_KEY to your .env file.",
            )

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
        update_screen_preview()  # Call the update function initially after session state is set

    def navigate_to_main():
        settings = {
            "selected_screen_index": st.session_state.selected_screen_index,
            "ocr_method": st.session_state.ocr_method,
            "downscale_screenshot": st.session_state.get("downscale_screenshot", True),
            "llm_provider": st.session_state.llm_provider,
            "llm_model": st.session_state.llm_model,
            "vision_model": st.session_state.vision_model,
            # Add other settings here as they are introduced
        }
        save_settings(settings)
        st.session_state.page = "main"
    st.button("Save", on_click=navigate_to_main)