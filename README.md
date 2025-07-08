# Vonet - The Autonomous AI PC Agent

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-experimental-orange.svg)

Vonet is an experimental, autonomous AI agent for Windows, powered by Google's Gemini model. It's designed to understand your commands in natural language and execute them using PowerShell, effectively acting as an AI assistant with direct control over your PC.

It features a user-friendly interface built with CustomTkinter, text-to-speech (TTS) for voice feedback, and a memory system to provide a personalized experience.


*(Suggestion: Record a short GIF of Vonet in action and replace the link above!)*

---

## ⚠️ Important Warning

**Vonet is designed to execute PowerShell commands on your computer with administrative-level access.** This gives it the ability to modify system files, install/uninstall software, and change system settings.

---

## ✨ Key Features

-   **🤖 Autonomous Control:** Give high-level goals, and Vonet will plan and execute the necessary PowerShell commands.
-   **🧠 Natural Language Understanding:** Powered by Google's Gemini, Vonet understands complex requests and conversational language.
-   **💾 Persistent Memory:** Vonet remembers your name and conversation history across sessions for a continuous, personalized experience.
-   **🗣️ Text-to-Speech (TTS):** Provides audible feedback for a more interactive feel, using the offline Piper TTS engine.
-   **🖥️ System Awareness:** Gathers static and dynamic information about your PC to inform its actions.
-   **🎨 Modern GUI:** A clean and responsive user interface built with CustomTkinter.

---

## ⚙️ How It Works

Vonet operates in a loop, taking input from the user or the system and generating a structured response.

1.  **Input:** The user types a message.
2.  **Prompting:** The message is combined with a detailed system prompt, conversation history, and system information.
3.  **AI Generation:** This complete context is sent to the Gemini API.
4.  **Parsing:** Gemini returns a structured response within `[VONET]` tags, which includes:
    -   `<thinking>`: The AI's internal monologue and plan.
    -   `<tts>`: The message to be spoken to the user.
    -   `<command>`: The PowerShell command to be executed.
    -   `<state>`: The agent's current state (e.g., `wait_for_user`).
    -   `<display>`: Status information for the GUI.
5.  **Execution:** The application parses these tags, speaks the TTS message, and runs the PowerShell command. The output of the command is then fed back into the loop as a `[SYSTEM]` message for the AI to analyze.

---

## 🚀 Getting Started

### Prerequisites

-   Windows 10 or 11
-   Python 3.9+
-   A Google AI API Key (from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Installation

First, clone the repository to your local machine.

```bash
git clone https://github.com/YourUsername/Vonet.git
cd Vonet
```

Next, install the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 2. API Key Setup 

**Set the environment variable** on your system. Open a Command Prompt or PowerShell and run this command, replacing `YOUR_API_KEY_HERE` with your actual key.

  ```cmd
  set GOOGLE_API_KEY=YOUR_API_KEY_HERE
  ```

### 3. Piper TTS Setup

The project expects the [Piper](https://github.com/rhasspy/piper) TTS engine to be in a directory named `piper/` within the project folder. Ensure you have downloaded and placed the Piper executable and model files there.

**Download the full setup PIPER [Here](https://github.com/rhasspy/piper)**. Extract it and move it into `piper/` directory within the project folder.

### 4. Running Vonet

Once the dependencies are installed and your API key is configured, you can run the application:

```bash
python main.py
```

---

## 📁 Project Structure

```
Vonet/
├── assets/
│   ├── vonet_icon.png
│   ├── ...
├── core/
│   ├── ai_handler.py
│   ├── ...
├── gui/
│   ├── app.py
├── piper/
│   ├── piper.exe
│   └── ... (model files)
├── pws_script/
│   └── powershell_command.ps1 (created at runtime)
├── config.py  
├── main.py
├── prompts.py               
├── requirements.txt       
└── README.md        
```

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🙏 Acknowledgments

-   **Google** for the powerful Gemini Pro model.
-   The **CustomTkinter** team for the beautiful modern GUI toolkit.
-   The **Piper TTS** project for the high-quality, offline text-to-speech engine.
