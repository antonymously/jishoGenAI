import streamlit as st
import os
from utils.screens import screenshot_monitor
from utils.screens import get_monitors

st.title("Screen Selector")

monitors = get_monitors()
available_screens = ["Display {}".format(i + 1) for i in range(len(monitors))]

selected_screen = st.selectbox("Select a screen:", available_screens)

st.write(f"You selected: {selected_screen}")

if st.button("Take Screenshot"):
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
    
    st.success(f"Screenshot saved to {save_path}")
