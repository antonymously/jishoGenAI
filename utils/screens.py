import mss
from PIL import Image

SCT = mss.mss()

def get_monitors():
    # List all monitors
    monitors = SCT.monitors

    # NOTE: in windows, monitors[0] is a special combined region
        # covering all monitors.
        # let's remove this for now
        # reference: https://www.reddit.com/r/learnpython/comments/rkyq4v/question_about_mss_and_monitor_selection/?rdt=35944
    monitors = monitors[1:]
    
    return monitors

def list_monitors():
    monitors = get_monitors()
        
    monitor_names = ["Display {}".format(i + 1) for i in range(len(monitors))]
    return monitor_names

def screenshot_monitor(monitor_dict: dict):
    '''
    Args:
        monitor_dict: dict. item from output of SCT.monitors
    '''

    # Capture the screenshot of the specified monitor
    # NOTE: I think I'm getting an error here because I'm running on WSL
    # TODO: probably need to try running on windows directly
    screenshot = SCT.grab(monitor_dict)

    # Convert the screenshot to a PIL Image for further processing or saving
    img = Image.frombytes(
        "RGB", 
        screenshot.size, 
        screenshot.bgra, 
        "raw", 
        "BGRX"
    )

    return img