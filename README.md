
# Moreweb AI Runtime

Moreweb AI Runtime is a complete suite that turns your local machine into a powerful, OpenAI-compatible AI server. Powered by the versatile `g4f` library, it provides free, reliable AI endpoints that you can control and use for all your development projects—from VS Code extensions to custom scripts and applications.

---

## ✨ Key Features

*   **🖥️ GUI Control Panel:** An elegant and simple interface to start, stop, and configure the AI server.
*   **⚡ OpenAI-Compatible API:** Use the local server as a drop-in replacement for the OpenAI API in your existing tools and code.
*   **🌊 Real-time Streaming:** Get responses token-by-token with full streaming support, eliminating timeouts and enhancing user experience.
*   **⚙️ Smart Provider Modes:**
    *   **AUTO+:** Prioritizes high-quality, reliable models.
    *   **Auto:** Uses a broad range of capable models.
    *   **Manual:** Pinpoint a specific provider and model for consistent results.
*   **🧪 Dedicated GUI Tester:** A user-friendly testing application to interact with your API, send prompts, and inspect raw responses in real-time.
*   **💻 Feature-Rich CLI:** A beautiful and powerful command-line client for both quick, one-shot prompts and stateful, back-and-forth interactive chats.

---

## 📸 Screenshots

#### The Runtime Control Panel
The main application for managing the local AI server.



#### The API Tester
A separate GUI for sending requests to your running server.



#### The CLI in Action
A powerful and beautiful command-line interface for both single prompts and interactive chat.
```bash
$ python moreweb_cli.py chat "Explain quantum computing in a single paragraph."
```


---

## 🚀 Getting Started

### Prerequisites

*   Python 3.8 or higher.
*   `pip` for package installation.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/moreweb-ai-runtime.git
    cd moreweb-ai-runtime
    ```

2.  **Install Dependencies:**
    Create a virtual environment (recommended) and install the required packages.
    ```bash
    # Create and activate a virtual environment (optional but good practice)
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install requirements
    pip install -r requirements.txt
    ```

---

## 📖 How to Use

The suite is composed of three main parts: the Runtime Server, the API Tester, and the CLI.

### 1. Launch the Moreweb AI Runtime

This is the core server. You must have this running to use the API, Tester, or CLI.

```bash
python main_app.py
```

In the GUI that appears:
1.  Select your desired **Mode** (AUTO+ is recommended for general use).
2.  Click **"Start Server"**.
3.  The status will turn green, and the server log will show activity.

Your local AI API is now live at `http://127.0.0.1:1337`!

### 2. Choose Your Client

You can now interact with your server using any of the following tools.

#### A) Using the API Tester (GUI)

For visual testing and debugging, launch the tester application in a **new terminal**.

```bash
python api_tester.py
```

Use the interface to type a prompt, toggle streaming, and send requests to your server.

#### B) Using the CLI Client

For quick prompts or interactive chat sessions, the CLI is the perfect tool.

**Start an Interactive Chat:**
Simply run the `chat` command without a prompt to enter a back-and-forth conversation.

```bash
python moreweb_cli.py chat
```
> **Tip:** Start a chat with a system prompt to set a persona:
> `python moreweb_cli.py chat -s "You are a pirate captain."`

**Send a One-Shot Prompt:**
Provide a prompt directly as an argument for a single request and response.

```bash
# Streaming response (default)
python moreweb_cli.py chat "Write a haiku about a cup of coffee."

# Non-streaming response in a formatted panel
python moreweb_cli.py chat "What are the primary colors?" --no-stream
```

**Pipe Content from other commands:**
The CLI integrates seamlessly with your shell.

```bash
echo "Summarize this text for me." | python moreweb_cli.py chat
cat my_code.py | python moreweb_cli.py chat "Explain what this Python code does."
```

#### C) Using the API Directly

Integrate the API into your own applications.

<details>
<summary><strong>Click to see API Details and Examples</strong></summary>

The API is OpenAI-compatible, making integration simple.

*   **Endpoint:** `POST http://127.0.0.1:1337/v1/chat/completions`
*   **Body:**
    ```json
    {
      "messages": [
        {"role": "user", "content": "Your prompt here..."}
      ],
      "stream": false // or true
    }
    ```

**Example with `curl`:**
```bash
curl -N http://1227.0.0.1:1337/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```
> For complete details, code samples in Python and JavaScript, and response schemas, please see the full **[API Documentation](API_DOCS.md)**.

</details>

---

## 📁 Project Structure

```
/moreweb-ai-runtime/
|-- main_app.py           # The main Runtime GUI controller
|-- api_server.py         # The Flask API server logic
|-- api_tester.py         # The GUI for testing the API
|-- moreweb_cli.py        # The command-line interface client
|-- requirements.txt      # Python dependencies
|-- README.md             # This file
|-- API_DOCS.md           # Full developer documentation for the API
```
