# /gui/app.py
import random
import customtkinter as ctk
import tkinter as tk
from PIL import Image
import config  # Import the config module to access shared variables and constants

class VonetAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vonet AI Agent")
        self.geometry("500x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self._configure_grid()

        self.loading_bubble_frame_widget = None
        self.loading_bubble_label_widget = None
        self.loading_animation_id = None
        self.current_loading_message_base = ""

        self.header_font = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.body_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.button_font = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.small_button_font = ctk.CTkFont(family="Segoe UI", size=12)
        self.special_text_font = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

        self.settings_window = None
        self.about_window = None

        # Load images using the resource_path function from the config module
        try:
            self.logo_image = ctk.CTkImage(light_image=Image.open(config.resource_path("assets/vonet_icon.png")),
                                           dark_image=Image.open(config.resource_path("assets/vonet_icon.png")),
                                           size=(32, 32))
        except FileNotFoundError:
            print("Warning: logo.png not found. Displaying text instead.")
            self.logo_image = None

        try:
            # Assuming these icons are also in the assets folder
            self.settings_icon = ctk.CTkImage(light_image=Image.open(config.resource_path("assets/settings_icon.png")),
                                              dark_image=Image.open(config.resource_path("assets/settings_icon.png")),
                                              size=(20, 20))
        except FileNotFoundError:
            print("Warning: settings_icon.png not found. Using text button.")
            self.settings_icon = None

        try:
            self.about_icon = ctk.CTkImage(light_image=Image.open(config.resource_path("assets/about_icon.png")),
                                           dark_image=Image.open(config.resource_path("assets/about_icon.png")),
                                           size=(20, 20))
        except FileNotFoundError:
            print("Warning: about_icon.png not found. Using text button.")
            self.about_icon = None

        self.create_widgets()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

    def create_widgets(self):
        # --- Header Frame ---
        header_frame_fg_color = ("#F5F5F5", "#2B2B2B")
        header_frame_border_color = ("#E0E0E0", "#3D3D3D")
        self.header_frame = ctk.CTkFrame(self, fg_color=header_frame_fg_color, border_color=header_frame_border_color, corner_radius=5, height=50)
        self.header_frame.grid(row=0, column=0, sticky="new")
        self.header_frame.grid_columnconfigure(0, weight=0)
        self.header_frame.grid_columnconfigure(1, weight=0)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=0)
        self.header_frame.grid_columnconfigure(4, weight=0)

        if self.logo_image:
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_image, text="")
        else:
            self.logo_label = ctk.CTkLabel(self.header_frame, text="V", font=ctk.CTkFont(size=24, weight="bold"), text_color=config.TEXT_COLOR[0])
        self.logo_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        self.title_label = ctk.CTkLabel(self.header_frame, text="VONET-V1", font=self.header_font, text_color=config.TEXT_COLOR[0])
        self.title_label.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

        self.settings_button = ctk.CTkButton(
            self.header_frame, text="Settings" if not self.settings_icon else "", image=self.settings_icon,
            width=30, height=30, fg_color="transparent", hover_color=config.SECONDARY_BLUE, command=self.open_settings_window
        )
        self.settings_button.grid(row=0, column=3, padx=(0, 5), pady=10, sticky="e")

        self.about_button = ctk.CTkButton(
            self.header_frame, text="About" if not self.about_icon else "", image=self.about_icon,
            width=30, height=30, fg_color="transparent", hover_color=config.SECONDARY_BLUE, command=self.open_about_window
        )
        self.about_button.grid(row=0, column=4, padx=(0, 10), pady=10, sticky="e")

        # --- Chat Container ---
        self.chat_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=(50, 0))
        self.chat_container.grid_columnconfigure(0, weight=1)
        self.chat_container.grid_rowconfigure(0, weight=1)

        self.chat_frame = ctk.CTkScrollableFrame(
            self.chat_container, fg_color="transparent",
            scrollbar_button_color=config.SECONDARY_BLUE, scrollbar_button_hover_color=config.PRIMARY_BLUE
        )
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # --- Input Frame ---
        input_frame_fg_color = ("#F5F5F5", "#2B2B2B")
        input_frame_border_color = ("#E0E0E0", "#3D3D3D")
        self.input_frame = ctk.CTkFrame(self, fg_color=input_frame_fg_color, corner_radius=20, border_width=1, border_color=input_frame_border_color)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(1, 1))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)

        self.user_input_entry = ctk.CTkTextbox(
            self.input_frame, height=40, font=self.body_font, fg_color="transparent", border_width=0, wrap="word"
        )
        self.user_input_entry.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=10)
        self.user_input_entry.bind("<Shift-Return>", lambda e: self.on_send_pressed())
        self.user_input_entry.bind("<Control-Return>", lambda e: self.on_send_pressed())
        self.user_input_entry.insert("1.0", "Type your message to VONET...")
        self.user_input_entry.configure(text_color="gray")
        self.user_input_entry.bind("<FocusIn>", self._clear_placeholder)
        self.user_input_entry.bind("<<Modified>>", self._on_text_modified)

        self.send_button = ctk.CTkButton(
            self.input_frame, text="Send", width=80, height=40, corner_radius=15, font=self.button_font,
            fg_color=config.PRIMARY_BLUE, hover_color=config.ACCENT_TEAL, text_color=config.TEXT_COLOR[0], command=self.on_send_pressed
        )
        self.send_button.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=10)

        disclaimer_text = "Warning: Vonet can control your computer—use with caution."
        disclaimer_font = ctk.CTkFont(family="Segoe UI", size=10)
        disclaimer_text_color = ("#606060", "#A0A0A0")
        self.disclaimer_label = ctk.CTkLabel(self, text=disclaimer_text, font=disclaimer_font, text_color=disclaimer_text_color, wraplength=450)
        self.disclaimer_label.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))

    def _clear_placeholder(self, event=None):
        if self.user_input_entry.get("1.0", "end-1c") == "Type your message to VONET...":
            self.user_input_entry.delete("1.0", "end")
            self.user_input_entry.configure(text_color=("black", "white"))

    def _update_textbox_height(self, event=None):
        content = self.user_input_entry.get("1.0", "end-1c")
        lines = content.count('\n') + 1
        max_lines = 5
        lines = min(lines, max_lines)
        new_height = lines * 24
        new_height = max(new_height, 40)
        self.user_input_entry.configure(height=new_height)

    def _on_text_modified(self, event=None):
        # This check prevents recursive calls
        if self.user_input_entry.edit_modified():
            self._update_textbox_height()
            self.user_input_entry.edit_modified(False)

    def on_send_pressed(self, event=None):
        # No 'global' needed; we modify the variable in the imported config module
        user_text = self.user_input_entry.get("1.0", "end-1c").strip()
        if user_text and config.VONET_ONLINE and user_text != "Type your message to VONET...":
            current_fg = self.send_button.cget("fg_color")
            self.send_button.configure(fg_color=config.ACCENT_TEAL)
            self.after(100, lambda: self.send_button.configure(fg_color=current_fg))

            self.chat_bubble("user", user_text)
            self.user_input_entry.delete("1.0", "end")
            config.USER_MESSAGE_FOR_AI = user_text # Set the shared variable

    def open_settings_window(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = ctk.CTkToplevel(self)
            self.settings_window.title("Settings")
            self.settings_window.geometry("250x200")
            self.settings_window.transient(self)
            self.settings_window.attributes("-topmost", True)
            self.settings_window.protocol("WM_DELETE_WINDOW", self._on_settings_close)

            ctk.CTkLabel(self.settings_window, text="Appearance Mode:", font=self.body_font).pack(pady=(10, 5))
            ctk.CTkButton(self.settings_window, text="Light Mode", command=lambda: self._set_appearance("Light"), font=self.small_button_font).pack(pady=5, padx=20, fill="x")
            ctk.CTkButton(self.settings_window, text="Dark Mode", command=lambda: self._set_appearance("Dark"), font=self.small_button_font).pack(pady=5, padx=20, fill="x")
            ctk.CTkButton(self.settings_window, text="System Default", command=lambda: self._set_appearance("System"), font=self.small_button_font).pack(pady=5, padx=20, fill="x")
        else:
            self.settings_window.focus()

    def _set_appearance(self, mode):
        pass
        # ctk.set_appearance_mode(mode)
        # if self.settings_window and self.settings_window.winfo_exists():
        #     self.settings_window.destroy()
        # self.settings_window = None
        # return

    def _on_settings_close(self):
        if self.settings_window:
            self.settings_window.destroy()
        self.settings_window = None

    def open_about_window(self):
        if self.about_window is None or not self.about_window.winfo_exists():
            self.about_window = ctk.CTkToplevel(self)
            self.about_window.title("About VONET AI")
            self.about_window.geometry("580x600")
            self.about_window.transient(self)
            self.about_window.attributes("-topmost", True)
            self.about_window.protocol("WM_DELETE_WINDOW", self._on_about_close)

            container = ctk.CTkFrame(self.about_window, corner_radius=20)
            container.pack(padx=20, pady=20, fill="both", expand=True)

            try:
                vonet_icon = ctk.CTkImage(Image.open(config.resource_path("assets/vonet_icon.png")), size=(50, 50))
                mcatech_logo = ctk.CTkImage(Image.open(config.resource_path("assets/mcatech_logo.webp")), size=(50, 50))
            except Exception as e:
                print("Image loading error:", e)
                vonet_icon = mcatech_logo = None

            if vonet_icon:
                ctk.CTkLabel(container, image=vonet_icon, text="").pack(pady=(10, 5))
            ctk.CTkLabel(container, text="VONET", font=ctk.CTkFont(size=20, weight="bold")).pack()
            ctk.CTkLabel(container, text="Version: 1.0.0", font=self.body_font).pack(pady=(5, 15))

            info_text = (
                "Vonet is an AI — a fully autonomous agent designed to control and manage your Windows PC "
                "by intelligently interacting with PowerShell commands. It can perform a wide range of tasks "
                "such as managing files, executing scripts, automating system operations, and most importantly, "
                "troubleshooting common issues — including slow performance, unresponsive programs, internet "
                "connectivity problems, startup errors, driver conflicts, missing updates, and corrupted system files.\n\n"
                "With just a simple prompt like 'my Wi-Fi is not working, fix it,' Vonet can attempt to diagnose "
                "and resolve the issue automatically — no technical knowledge required.\n\n"
                "Please note: Vonet is still in the experimental stage and may not work perfectly in all situations."
            )
            ctk.CTkLabel(container, text=info_text, font=self.body_font, justify="left", wraplength=520).pack(padx=15, pady=(0, 20), anchor="w")

            if mcatech_logo:
                ctk.CTkLabel(container, image=mcatech_logo, text="").pack(pady=(5, 2))
            ctk.CTkLabel(container, text="McaTech", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))
        else:
            self.about_window.focus()

    def _on_about_close(self):
        if self.about_window:
            self.about_window.destroy()
        self.about_window = None

    def chat_bubble(self, turn, chat_text):
        if not self.winfo_exists(): return

        def process_text(text):
            parts = []
            current_pos = 0
            while True:
                marker_start = text.find('__', current_pos)
                if marker_start == -1:
                    parts.append((text[current_pos:], False))
                    break
                if marker_start > current_pos:
                    parts.append((text[current_pos:marker_start], False))
                marker_end = text.find('__', marker_start + 2)
                if marker_end == -1:
                    parts.append((text[marker_start:], False))
                    break
                parts.append((text[marker_start + 2:marker_end], True))
                current_pos = marker_end + 2
            return parts

        bubble_max_width = self.chat_frame.winfo_width() - 40
        text_wraplength = bubble_max_width * 0.75 if bubble_max_width > 100 else 100

        bg_color = config.USER_BG_COLOR if turn == "user" else config.VONET_BG_COLOR
        anchor = "e" if turn == "user" else "w"
        padx = (50, 10) if turn == "user" else (10, 50)

        bubble_frame = ctk.CTkFrame(self.chat_frame, fg_color=bg_color, corner_radius=20)
        bubble_frame.pack(anchor=anchor, padx=padx, pady=5, expand=False)

        text_container = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        text_container.pack(padx=15, pady=12, fill="x", expand=True)

        for text_part, is_special in process_text(chat_text):
            if text_part.strip():
                if is_special:
                    italic_font = ctk.CTkFont(family=self.body_font.cget("family"), size=self.body_font.cget("size"), slant="italic")
                    highlight_frame = ctk.CTkFrame(text_container, fg_color="#3C3C3C", corner_radius=3)
                    highlight_frame.pack(fill="x", expand=True, pady=(2, 2))
                    ctk.CTkLabel(highlight_frame, text=text_part, wraplength=text_wraplength, font=italic_font, justify=tk.LEFT, text_color=config.TEXT_COLOR, anchor="w").pack(padx=10, pady=10, fill="x", expand=True)
                else:
                    ctk.CTkLabel(text_container, text=text_part, wraplength=text_wraplength, font=self.body_font, justify=tk.LEFT, text_color=config.TEXT_COLOR, anchor="w").pack(fill="x", expand=True)

        self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    def loading(self, state, message_base="VONET processing"):
        if not self.winfo_exists(): return

        if state == "start":
            if self.loading_animation_id: self.after_cancel(self.loading_animation_id)
            if self.loading_bubble_frame_widget: self.loading_bubble_frame_widget.destroy()

            self.current_loading_message_base = message_base
            bubble_max_width = self.chat_frame.winfo_width() - 40
            
            self.loading_bubble_frame_widget = ctk.CTkFrame(self.chat_frame, fg_color=config.VONET_LOADING_BG_COLOR, corner_radius=20)
            self.loading_bubble_frame_widget.pack(anchor="w", padx=(10, 50), pady=5, fill="x", expand=False)
            self.loading_bubble_label_widget = ctk.CTkLabel(
                self.loading_bubble_frame_widget, text=self.current_loading_message_base + ".",
                wraplength=bubble_max_width * 0.7, font=self.body_font, justify=tk.LEFT, text_color=config.TEXT_COLOR, anchor="w"
            )
            self.loading_bubble_label_widget.pack(padx=15, pady=12, fill="x", expand=True)
            self._animate_loading_dots()
            self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))
        elif state == "end":
            if self.loading_animation_id: self.after_cancel(self.loading_animation_id)
            if self.loading_bubble_frame_widget: self.loading_bubble_frame_widget.destroy()
            self.loading_bubble_frame_widget = None
            self.loading_animation_id = None

    def _animate_loading_dots(self, count=0):
        if not (self.loading_bubble_label_widget and self.loading_bubble_label_widget.winfo_exists()):
            self.loading_animation_id = None
            return

        # Use config.TTS_SPEAKING to access the shared state
        if not config.TTS_SPEAKING:
            phases = ["⠋", "⠙", "⠸", "⠴", "⠦", "⠇", "⠃"]
            current_text = phases[count % len(phases)] + " " + self.current_loading_message_base
            self.loading_bubble_label_widget.configure(text=current_text)
            self.loading_animation_id = self.after(10, self._animate_loading_dots, count + 1)
        else:
            phases = ["..", "...", "....", ".....", "......", ".....", "....", "...", "."]
            current_text = self.current_loading_message_base + " " + phases[count % len(phases)]
            self.loading_bubble_label_widget.configure(text=current_text)
            self.loading_animation_id = self.after(20, self._animate_loading_dots, count + 1)