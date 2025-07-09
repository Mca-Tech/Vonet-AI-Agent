# /core/ai_handler.py

import re
import time
import traceback
from httpx import ConnectError
from google.genai import types
from google import genai
import config
import os
from . import memory_manager, tts_handler, system_utils

def init_gemini(history=None):
    """Initializes the Gemini chat session with system instructions and history."""
    print("Initializing Gemini AI...")

    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options=types.HttpOptions(timeout=120_000)
    )

    cfg = types.GenerateContentConfig(
        system_instruction=config.INSTRUCTION,
        temperature=0.0,
        top_p=1.0,
        top_k=1,
        max_output_tokens=8192,
        stop_sequences=["[/VONET]"],
        response_mime_type="text/plain",
    )
    
    # Create a ChatSession with persistent history and system instructions
    config.chat_session = client.chats.create(
        model="gemini-2.0-flash",
        config=cfg,
        history=history if history else []
    )

def extract_sections(text):
    tts = re.search(r'<tts>\s*(.*?)\s*(?:<|$)', text, re.DOTALL)
    cmd = re.search(r'<command>\s*(.*?)\s*(?:<|$)', text, re.DOTALL)
    per_task = re.search(r'<state>\s*(.*?)\s*(?:<|$)', text, re.DOTALL)
    urq = re.search(r'<thinking>\s*(.*?)\s*(?:<|$)', text, re.DOTALL)
    dsp = re.search(r'<display>\s*(.*?)\s*(?:<|$)', text, re.DOTALL)
    return {
        'tts': tts.group(1).strip() if tts else None,
        'command': cmd.group(1).strip() if cmd else None,
        'state': per_task.group(1).strip() if per_task else None,
        'thinking': urq.group(1).strip() if per_task else None,
        'display': dsp.group(1).strip() if dsp else None
    }
def process_ai_response(full_response_text, original_input_message):
    """Processes the parsed AI response to perform actions."""
    print(f"AI Raw Response:\n{full_response_text}")
    parsed = extract_sections(full_response_text)

    # Save the full turn to conversation history
    memory_manager.save_session_history(original_input_message, full_response_text)

    print(f"\n[THINKING]: {parsed.get('thinking')}")
    print(f"[TTS]: {parsed.get('tts')}")
    print(f"[COMMAND]: {parsed.get('command')}")
    print(f"[DISPLAY]: {parsed.get('display')}")
    print(f"[STATE]: {parsed.get('state')}")

    if config.app_instance:
        config.app_instance.after(0, config.app_instance.loading, "end")
        display_text = parsed.get('display', '')
        tts_text = parsed.get('tts', '')
        if tts_text or display_text:
            bubble_text = f"{tts_text}\n__{display_text}__" if display_text else tts_text
            config.app_instance.after(0, config.app_instance.chat_bubble, "vonet", bubble_text)

    if parsed.get('tts'):
        while config.TTS_SPEAKING: time.sleep(0.1)
        tts_handler.text_to_speech(parsed['tts'])
        while config.TTS_SPEAKING: time.sleep(0.1)

    if parsed.get('command'):
        if config.app_instance:
            loading_msg = parsed.get('display') or "Executing command..."
            config.app_instance.after(0, config.app_instance.loading, "start", loading_msg)
        system_utils.run_background_command(parsed['command'])
    elif "self_continue" in parsed.get('state', ''):
        config.SYSTEM_MESSAGE_FOR_AI = "Continue." # Trigger next step

def message_listener():
    """The main loop that listens for user/system messages and sends them to the AI."""
    while True:
        message_to_send = None
        is_user_message = False

        if not config.TTS_SPEAKING and not config.SENDING_TO_AI:
            if config.USER_MESSAGE_FOR_AI:
                message_to_send = f"[USER]: {config.USER_MESSAGE_FOR_AI}"
                config.USER_MESSAGE_FOR_AI = ""
                is_user_message = True
            elif config.SYSTEM_MESSAGE_FOR_AI:
                message_to_send = f"[SYSTEM]: {config.SYSTEM_MESSAGE_FOR_AI}"
                config.SYSTEM_MESSAGE_FOR_AI = ""

        if message_to_send:
            config.SENDING_TO_AI = True
            print(f"Sending to AI: {message_to_send}")
            
            try:
                if config.app_instance and is_user_message:
                    config.app_instance.after(0, config.app_instance.loading, "start", "Vonet thinking...")
                if config.app_instance and not is_user_message:
                    config.app_instance.after(0, config.app_instance.loading, "start", "processing...")
                response = config.chat_session.send_message(message_to_send)
                full_response_text = response.text

            except (TimeoutError, ConnectError) as e:
                print(f"Connection Error: {e}")
                full_response_text = "<thinking>Connection failed.</thinking><tts>I'm having trouble connecting. Please check your internet and try again.</tts><command></command><state>pause</state><display>Connection error.</display>"
            except Exception as e:
                print(f"An unexpected error occurred: {e}\n{traceback.format_exc()}")
                full_response_text = "<thinking>An internal error occurred.</thinking><tts>Something went wrong. Maybe check your internet connection and try that again.</tts><command></command><state>pause</state><display>Internal error.</display>"

            process_ai_response(full_response_text, message_to_send)
            config.SENDING_TO_AI = False

        time.sleep(0.2)