# main_app.py - Moreweb AI Runtime v0.1.0
# Main graphical user interface for controlling the local AI server.

import customtkinter as ctk
import threading
import requests
import g4f
import api_server

def get_text_models():
    text_providers = {}
    for provider_class in g4f.Provider.__providers__:
        try:
            provider_name = provider_class.__name__
            if getattr(provider_class, 'supports_gpt_35_turbo', False) or getattr(provider_class, 'supports_gpt_4', False) or getattr(provider_class, 'working', False):
                if not getattr(provider_class, 'supports_image_generation', False) and provider_class.models:
                    text_providers[provider_name] = provider_class.models
        except Exception:
            continue
    return text_providers

class MorewebRuntimeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Moreweb AI Runtime")
        self.geometry("850x600")
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")

        self.title_font = ctk.CTkFont(family="Roboto", size=24, weight="bold")
        self.header_font = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.label_font = ctk.CTkFont(family="Roboto", size=12)
        self.monospace_font = ctk.CTkFont(family="Courier New", size=11)

        self.server_thread = None; self.is_server_running = False
        self.HOST = '127.0.0.1'; self.PORT = 1337
        self.text_model_data = get_text_models()
        self.provider_list = sorted(list(self.text_model_data.keys()))

        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=2); self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.left_frame, text="Moreweb AI Runtime", font=self.title_font, text_color="#00A7E1").grid(row=0, column=0, padx=20, pady=(20, 10))
        
        status_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        self.start_stop_button = ctk.CTkButton(status_frame, text="Start Server", font=self.label_font, command=self.toggle_server, height=35)
        self.start_stop_button.grid(row=0, column=0, columnspan=2, padx=0, pady=(0,10), sticky="ew")
        ctk.CTkLabel(status_frame, text="Status:", font=self.header_font).grid(row=1, column=0, sticky="w")
        self.status_label = ctk.CTkLabel(status_frame, text="Stopped", font=self.header_font, text_color="#D32F2F")
        self.status_label.grid(row=1, column=1, sticky="e")
        ctk.CTkLabel(status_frame, text="Port:", font=self.label_font).grid(row=2, column=0, sticky="w", pady=(10,0))
        self.port_entry = ctk.CTkEntry(status_frame, font=self.monospace_font)
        self.port_entry.grid(row=2, column=1, sticky="ew", pady=(10,0))
        self.port_entry.insert(0, str(self.PORT))
        ctk.CTkLabel(status_frame, text="API URL:", font=self.label_font).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10,0))
        self.url_entry = ctk.CTkEntry(status_frame, font=self.monospace_font)
        self.url_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.url_entry.configure(state="disabled")

        config_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        config_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(config_frame, text="Configuration", font=self.header_font).grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")
        ctk.CTkLabel(config_frame, text="Mode:", font=self.label_font).grid(row=1, column=0, sticky="w", padx=0, pady=5)
        self.mode_var = ctk.StringVar(value="AUTO+")
        self.mode_menu = ctk.CTkOptionMenu(config_frame, variable=self.mode_var, values=["Manual", "Auto", "AUTO+"], command=self.on_mode_change)
        self.mode_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(config_frame, text="Provider:", font=self.label_font).grid(row=2, column=0, sticky="w", padx=0, pady=5)
        self.provider_var = ctk.StringVar(value=self.provider_list[0] if self.provider_list else "")
        self.provider_menu = ctk.CTkOptionMenu(config_frame, variable=self.provider_var, values=self.provider_list, command=self.on_provider_change)
        self.provider_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(config_frame, text="Model:", font=self.label_font).grid(row=3, column=0, sticky="w", padx=0, pady=5)
        self.model_var = ctk.StringVar(value="")
        self.model_menu = ctk.CTkOptionMenu(config_frame, variable=self.model_var, values=[])
        self.model_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        self.right_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1); self.right_frame.grid_columnconfigure(0, weight=1)
        log_header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        log_header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        log_header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_header_frame, text="Server Log", font=self.header_font).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(log_header_frame, text="Clear Log", width=80, command=self.clear_log, fg_color="#424242").grid(row=0, column=1, sticky="e")
        self.log_textbox = ctk.CTkTextbox(self.right_frame, state="disabled", corner_radius=10, font=self.monospace_font, border_width=0, fg_color="#1E1E1E")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

        if self.provider_list: self.on_provider_change(self.provider_var.get())
        self.on_mode_change(self.mode_var.get())
        self.update_ui_for_server_stopped()

    def on_mode_change(self, mode):
        state = "normal" if mode == "Manual" else "disabled"
        self.provider_menu.configure(state=state); self.model_menu.configure(state=state)
        self.log(f"Mode switched to '{mode}'.")

    def on_provider_change(self, provider_name):
        models = self.text_model_data.get(provider_name, [])
        self.model_menu.configure(values=models)
        self.model_var.set(models[0] if models else "")
    
    def log(self, message):
        def _append():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", f"› {message}\n"); self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        self.after(0, _append)

    def clear_log(self):
        self.log_textbox.configure(state="normal"); self.log_textbox.delete("0.0", "end")
        self.log_textbox.configure(state="disabled"); self.log("Log cleared.")

    def toggle_server(self):
        if self.is_server_running: self.stop_server()
        else: self.start_server()

    def start_server(self):
        try:
            port = int(self.port_entry.get())
            if not 1024 <= port <= 65535:
                self.log("Error: Port must be between 1024 and 65535."); return
            self.PORT = port
        except ValueError:
            self.log("Error: Invalid port number."); return

        self.server_thread = threading.Thread(target=lambda: api_server.run_server(self, host=self.HOST, port=self.PORT), daemon=True)
        self.server_thread.start()
        self.is_server_running = True
        self.update_ui_for_server_running()
        self.log(f"Server starting at http://{self.HOST}:{self.PORT}")

    def stop_server(self):
        try: requests.post(f'http://{self.HOST}:{self.PORT}/shutdown', timeout=1)
        except requests.exceptions.RequestException: pass
        finally:
            self.server_thread = None; self.is_server_running = False
            self.update_ui_for_server_stopped()
            self.log("Server shutdown requested.")

    def update_ui_for_server_running(self):
        self.start_stop_button.configure(text="Stop Server", fg_color="#D32F2F", hover_color="#B71C1C")
        self.status_label.configure(text="Running", text_color="#00C853")
        self.port_entry.configure(state="disabled")
        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, "end"); self.url_entry.insert(0, f"http://{self.HOST}:{self.PORT}/v1/chat/completions")
        self.url_entry.configure(state="disabled", text_color="lightgray")

    def update_ui_for_server_stopped(self):
        default_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        hover_color = ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        self.start_stop_button.configure(text="Start Server", fg_color=default_color, hover_color=hover_color)
        self.status_label.configure(text="Stopped", text_color="#D32F2F")
        self.port_entry.configure(state="normal")
        self.url_entry.configure(state="normal"); self.url_entry.delete(0, "end"); self.url_entry.insert(0, "")
        self.url_entry.configure(state="disabled")

    def get_current_mode(self): return self.mode_var.get()
    def get_manual_provider(self): return self.provider_var.get()
    def get_manual_model(self): return self.model_var.get()

if __name__ == "__main__":
    MorewebRuntimeApp().mainloop()