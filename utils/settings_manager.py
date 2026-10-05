import json
import os
from pathlib import Path

# Anchor the settings file to the project root instead of the process working
# directory, so settings are found/saved regardless of where the app is launched.
SETTINGS_FILE = str(Path(__file__).resolve().parent.parent / "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)