# /config.py

import sys
import os

# --- Global State Variables ---
# These are initialized here and modified by other modules.
app_instance = None
chat_session = None
piper_process = None
processes = {}  # For tracking background commands

# Message queues for communication between GUI, AI, and System
USER_MESSAGE_FOR_AI = ""
SYSTEM_MESSAGE_FOR_AI = ""

# State flags
VONET_ONLINE = False
SENDING_TO_AI = False
TTS_SPEAKING = False

# AI and Memory Data
INSTRUCTION = ""
vonet_memory_data = {}  # Global dictionary to hold memory contents.
system_static_info = ""

# --- Constants ---
MAX_HISTORY_TURNS = 50
MEMORY_FILE_PATH = None # Will be set in memory_manager.py

# --- GUI Color and Font Constants ---
USER_BG_COLOR = ("#1F6AA5", "#1D6093")
VONET_BG_COLOR = ("#3CC5C2", "#2c2c2c")
VONET_LOADING_BG_COLOR = ("#A8A8A8", "#4A4A4A")
TEXT_COLOR = ("#FFFFFF", "#E5F6FF")
PRIMARY_BLUE = "#2962FF"
SECONDARY_BLUE = "#1E88E5"
PRIMARY_TEAL = "#26C6DA"
ACCENT_TEAL = "#26C6DA"

# --- Helper Function ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)