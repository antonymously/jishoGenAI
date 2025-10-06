import pygetwindow as gw
import pyautogui
import time
import streamlit as st # Assuming Streamlit might be used for error messages

def get_open_windows():
    """
    Returns a list of titles of all open, non-minimized windows.
    """
    windows = gw.getAllWindows()
    # Filter out minimized, unnamed, or irrelevant windows (e.g., the Streamlit app itself)
    # You might need to refine this filtering based on your specific needs.
    return sorted([w.title for w in windows if w.title and not w.isMinimized and w.title != "辞書GenAI"])

def screenshot_window(window_title: str):
    """
    Takes a screenshot of a specific window by its title.
    """
    try:
        window = gw.getWindowsWithTitle(window_title)
        if not window:
            st.error(f"Window with title '{window_title}' not found.")
            return None
        
        # If multiple windows have the same title, pick the first one
        target_window = window[0]
        
        # Bring the window to the foreground
        # NOTE: .activate() does now work, as described here: https://github.com/asweigart/PyGetWindow/issues/36
        # target_window.activate()

        # using this suggested approach instead
        if not target_window.isActive:
            pyautogui.press('altleft')
            target_window.activate()

        time.sleep(0.1) # Give it a moment to activate

        # Screenshot the window's region
        screenshot = pyautogui.screenshot(region=(target_window.left, target_window.top, target_window.width, target_window.height))
        return screenshot
    except Exception as e:
        st.error(f"Error taking screenshot of window '{window_title}': {e}")
        return None