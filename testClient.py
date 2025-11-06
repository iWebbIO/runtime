# api_tester.py - Moreweb AI Tester v0.1.0
# GUI Client for testing the Moreweb AI Runtime API.

import customtkinter as ctk
import requests
import threading
import json

class MorewebTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Moreweb AI Tester")
        self.geometry("700x750")
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("green")

        self.header_font = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.label_font = ctk.CTkFont(family="Roboto", size=12)
        self.monospace_font = ctk.CTkFont(family="Courier New", size=11)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3); self.grid_rowconfigure(4, weight=5); self.grid_rowconfigure(6, weight=4)

        prompt_frame = ctk.CTkFrame(self, fg_color="transparent")
        prompt_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        ctk.CTkLabel(prompt_frame, text="1. Compose Your Prompt", font=self.header_font, text_color="#00E676").grid(row=0, column=0, sticky="w")
        self.prompt_textbox = ctk.CTkTextbox(self, height=150, border_width=1, border_color="#333", font=self.label_font)
        self.prompt_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.prompt_textbox.insert("0.0", "Write a short story about a robot who discovers music.")

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=2); action_frame.grid_columnconfigure(2, weight=1)
        self.send_button = ctk.CTkButton(action_frame, text="Send Request", font=self.header_font, height=40, command=self.start_request_thread)
        self.send_button.grid(row=0, column=0, padx=(0,10), pady=0, sticky="ew")
        self.stream_switch = ctk.CTkSwitch(action_frame, text="Stream", font=self.label_font); self.stream_switch.select()
        self.stream_switch.grid(row=0, column=1, padx=10)
        self.status_label = ctk.CTkLabel(action_frame, text="Ready", font=self.label_font, text_color="gray", anchor="e")
        self.status_label.grid(row=0, column=2, padx=(10,0), sticky="ew")

        response_frame = ctk.CTkFrame(self, fg_color="transparent")
        response_frame.grid(row=3, column=0, padx=10, pady=(5,0), sticky="ew")
        ctk.CTkLabel(response_frame, text="2. AI Assistant Response", font=self.header_font, text_color="#00E676").grid(row=0, column=0, sticky="w")
        self.response_textbox = ctk.CTkTextbox(self, state="disabled", fg_color="#1E1E1E", border_width=0, font=self.label_font)
        self.response_textbox.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        raw_frame = ctk.CTkFrame(self, fg_color="transparent")
        raw_frame.grid(row=5, column=0, padx=10, pady=(5,0), sticky="ew")
        ctk.CTkLabel(raw_frame, text="3. Raw Events / JSON Output", font=self.header_font, text_color="#00E676").grid(row=0, column=0, sticky="w")
        self.json_textbox = ctk.CTkTextbox(self, state="disabled", fg_color="#1E1E1E", border_width=0, font=self.monospace_font)
        self.json_textbox.grid(row=6, column=0, padx=10, pady=5, sticky="nsew")
        
    def start_request_thread(self):
        self.send_button.configure(state="disabled", text="Sending...")
        self.status_label.configure(text="Connecting...", text_color="#FFCC00")
        self._update_textbox(self.response_textbox, ""); self._update_textbox(self.json_textbox, "")
        threading.Thread(target=self.perform_request, daemon=True).start()

    def perform_request(self):
        success = False
        try:
            url = f"http://127.0.0.1:1337/v1/chat/completions" # Default, user should know port
            prompt = self.prompt_textbox.get("0.0", "end")
            should_stream = bool(self.stream_switch.get())
            payload = {"messages": [{"role": "user", "content": prompt}], "stream": should_stream}
            
            with requests.post(url, json=payload, timeout=300, stream=should_stream) as response:
                response.raise_for_status()
                if should_stream:
                    # FIX: Use a lambda to correctly call configure from the main thread
                    self.after(0, lambda: self.status_label.configure(text="Streaming...", text_color="#00B0FF"))
                    for line in response.iter_lines():
                        if line:
                            decoded = line.decode('utf-8')
                            self.after(0, self.append_to_json, f"{decoded}\n")
                            if decoded.startswith('data:'):
                                content = decoded[5:].strip()
                                if content == "[DONE]": success = True; break
                                try:
                                    chunk = json.loads(content)
                                    text = chunk['choices'][0]['delta'].get('content', '')
                                    if text: self.after(0, self.append_to_response, text)
                                except (json.JSONDecodeError, IndexError): continue
                else:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "Error: No content.")
                    self.after(0, self._update_textbox, self.response_textbox, content)
                    self.after(0, self._update_textbox, self.json_textbox, json.dumps(data, indent=2))
                    success = True
        except Exception as e:
            self.after(0, self._update_textbox, self.response_textbox, f"An unexpected error occurred:\n\n{e}")
        finally:
            status = {"text": "Complete", "text_color": "#00C853"} if success else {"text": "Error", "text_color": "#D32F2F"}
            # FIX: Use lambdas to correctly pass keyword arguments to configure
            self.after(0, lambda: self.status_label.configure(**status))
            self.after(0, lambda: self.send_button.configure(state="normal", text="Send Request"))

    def append_to_response(self, text):
        self.response_textbox.configure(state="normal")
        self.response_textbox.insert("end", text); self.response_textbox.see("end")
        self.response_textbox.configure(state="disabled")

    def append_to_json(self, text):
        self.json_textbox.configure(state="normal")
        self.json_textbox.insert("end", text); self.json_textbox.see("end")
        self.json_textbox.configure(state="disabled")

    def _update_textbox(self, textbox, text):
        textbox.configure(state="normal")
        textbox.delete("0.0", "end"); textbox.insert("0.0", text)
        textbox.configure(state="disabled")

if __name__ == "__main__":
    MorewebTesterApp().mainloop()