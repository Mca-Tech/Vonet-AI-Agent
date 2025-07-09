# /main.py

import threading
import os
import config
from gui.app import VonetAppGUI
from core import ai_handler, memory_manager, system_utils, tts_handler
from prompts import load_instruc
import datetime

def start_up_backend():
    """
    Initializes all backend components in a specific order:
    1. Load memory.
    2. Gather system info.
    3. Load AI prompt.
    4. Initialize AI.
    5. Start the main message listener loop.
    6. Send the initial welcome message.
    """
    print("Starting backend services...")

    # 1. Load or initialize Vonet's memory from the file
    memory_manager.load_memory()

    # 2. Gather system info
    static_info_path = config.resource_path("assets/system_static_info.txt")
    if not os.path.exists(static_info_path):
        system_utils.get_static_info()
    with open(static_info_path, 'r') as f:
        config.system_static_info = f.read()

    # 3. Prepare the instruction prompt with user info
    load_instruc()

    # 4. Initialize the Gemini chat session with history
    ai_handler.init_gemini(history=config.vonet_memory_data.get("conversation_history", []))

    # 5. Start the core message listener in a separate thread
    message_listener_thread = threading.Thread(target=ai_handler.message_listener, daemon=True)
    message_listener_thread.start()

    config.VONET_ONLINE = True
    print("Vonet is online.")

    # 6. Determine and send the appropriate welcome message
    # Get current date and time
    current_datetime = datetime.datetime.now()

    chat_session_count = config.vonet_memory_data['chat_session']['count']


    if chat_session_count > 0:
        config.SYSTEM_MESSAGE_FOR_AI = f"This is your {str(chat_session_count+1)} chat session attemps.\nCurrent Date and Time {current_datetime}\n\n SYSTEM IS READY - Great the user. Request user name-or what should you call them, if no name yet."
    else:
        config.SYSTEM_MESSAGE_FOR_AI = f"This is your {str(chat_session_count+1)} chat session attemps.\nCurrent Date and Time {current_datetime}\n\n SYSTEM IS READY – This is your first time coming online. Begin by introducing yourself in detail, including your mission and purpose. Ask the user for their name—or what you should call them—and once provided, save that personal information to your MEMORY so you can offer more personalized assistance in all future conversations."
    
    config.vonet_memory_data['chat_session']['count'] = config.vonet_memory_data['chat_session']['count'] + 1
    memory_manager.save_memory()

if __name__ == "__main__":
    print("Starting Vonet... Please Wait...")

    # Start the TTS engine first
    tts_handler.start_piper_tts()

    # Create the GUI application instance
    app = VonetAppGUI()
    
    # Store the instance in the config so other modules can access it
    config.app_instance = app

    # Start all backend initialization in a separate thread to keep the GUI responsive
    backend_thread = threading.Thread(target=start_up_backend, daemon=True)
    backend_thread.start()

    # Start the Tkinter main loop
    app.mainloop()