import streamlit as st
from utils.screens import list_monitors

st.title("Screen Selector")

available_screens = list_monitors()

selected_screen = st.selectbox("Select a screen:", available_screens)

st.write(f"You selected: {selected_screen}")

# Here you would add logic to display the selected screen's content
