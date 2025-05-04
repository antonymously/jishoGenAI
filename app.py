import streamlit as st
from utils.screens import get_monitors

st.title("Screen Selector")

monitors = get_monitors()
available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]

selected_screen = st.selectbox("Select a screen:", available_screens)

st.write(f"You selected: {selected_screen}")

# Here you would add logic to display the selected screen's content
