from utils.screens import get_monitors, screenshot_monitor

monitors = get_monitors()

# TODO: try running on windows
img = screenshot_monitor(monitors[0])

img.save("./data/screenshots/test_screen.png")