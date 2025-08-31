import streamlit as st
from utils.screens import get_monitors

def settings_modal():
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