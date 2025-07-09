# /core/memory_manager.py

import os
import json
import config

def initialize_memory_file():
    """Creates a new, empty memory file."""
    print("Initializing new memory file.")
    config.vonet_memory_data = {
        "user_info": {
            "name": None
        },
        "chat_session": {
            "count": 0
        },
        "conversation_history": []
    }
    save_memory()

def load_memory():
    """Loads memory from the JSON file into the global variable."""
    if config.MEMORY_FILE_PATH is None:
        config.MEMORY_FILE_PATH = config.resource_path('assets/vonet_memory.json')

    if os.path.exists(config.MEMORY_FILE_PATH):
        try:
            with open(config.MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                config.vonet_memory_data = json.load(f)
            # Ensure conversation_history is a list
            if 'conversation_history' not in config.vonet_memory_data or not isinstance(config.vonet_memory_data.get('conversation_history'), list):
                 config.vonet_memory_data['conversation_history'] = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading memory file: {e}. Starting with fresh memory.")
            initialize_memory_file()
    else:
        initialize_memory_file()

def save_memory():
    """Saves the current state of the global memory variable to the JSON file."""
    try:
        os.makedirs(os.path.dirname(config.MEMORY_FILE_PATH), exist_ok=True)
        with open(config.MEMORY_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config.vonet_memory_data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving memory file: {e}")

def save_session_history(user_message, ai_message):
    """Saves the current chat session's history to the memory file."""
    current_history = config.vonet_memory_data.get("conversation_history", [])

    current_history.append({'role': 'user', 'parts': [{'text': user_message}]})
    current_history.append({'role': 'model', 'parts': [{'text': ai_message}]})

    # Trim history if it exceeds the max length
    if len(current_history) > config.MAX_HISTORY_TURNS:
        current_history = current_history[-config.MAX_HISTORY_TURNS:]

    config.vonet_memory_data["conversation_history"] = current_history
    save_memory()