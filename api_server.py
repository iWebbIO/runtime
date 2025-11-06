# api_server.py - Moreweb AI Runtime v0.1.0
# Core backend server that runs g4f logic and serves the API.

import flask
from flask import Flask, request, jsonify, Response
from g4f.client import Client
import logging
import json
import time
import uuid

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

AUTO_PLUS_MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-4", "claude-3-opus", "gemini-pro", "deepseek-v3", "Llama3-70b-chat"]
AUTO_MODELS = ["gpt-3.5-turbo", "gpt-4", "Llama3-8b-chat", "gemini", "mistral-7b"]

app_gui = None

def create_app(gui_instance):
    global app_gui
    app_gui = gui_instance
    flask_app = Flask(__name__)

    @flask_app.route('/')
    def index():
        return "<h1>Moreweb AI Runtime</h1><p>API endpoint is at /v1/chat/completions</p>"
    
    @flask_app.route('/shutdown', methods=['POST'])
    def shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None: raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'

    @flask_app.route('/v1/chat/completions', methods=['POST'])
    def chat_completions():
        try:
            data = request.get_json()
            messages = data.get("messages")
            stream = data.get("stream", False)
            mode = app_gui.get_current_mode()

            if not messages: return jsonify({"error": "The 'messages' field is required."}), 400

            client = Client()
            
            def get_g4f_response_stream():
                if mode == "Manual":
                    model, provider = app_gui.get_manual_model(), app_gui.get_manual_provider()
                    app_gui.log(f"Manual mode request: {provider}/{model}")
                    try:
                        yield from client.chat.completions.create(model=model, provider=provider, messages=messages, stream=True)
                    except Exception as e:
                        app_gui.log(f"Manual request with {provider}/{model} failed: {e}")
                else:
                    model_list = AUTO_PLUS_MODELS if mode == "AUTO+" else AUTO_MODELS
                    app_gui.log(f"Auto mode request with list: {model_list}")
                    for model_name in model_list:
                        try:
                            app_gui.log(f"Attempting model: {model_name}")
                            yield from client.chat.completions.create(model=model_name, messages=messages, stream=True)
                            app_gui.log(f"Success with model: {model_name}!")
                            return
                        except Exception as e:
                            app_gui.log(f"Model {model_name} failed: {str(e)[:150]}...")
                            continue

            if stream:
                def sse_stream():
                    completion_id, created_time = f"chatcmpl-{uuid.uuid4().hex}", int(time.time())
                    model_name_reported = "g4f-stream"
                    try:
                        for chunk in get_g4f_response_stream():
                            if chunk.model: model_name_reported = chunk.model
                            if chunk.choices and chunk.choices[0].delta.content:
                                response_chunk = {"id": completion_id, "object": "chat.completion.chunk", "created": created_time, "model": model_name_reported, "choices": [{"index": 0, "delta": {"content": chunk.choices[0].delta.content}, "finish_reason": None }]}
                                yield f"data: {json.dumps(response_chunk)}\n\n"
                    except Exception as e:
                        app_gui.log(f"Error during stream generation: {e}")
                    yield "data: [DONE]\n\n"
                return Response(sse_stream(), mimetype='text/event-stream')
            else:
                app_gui.log(f"Received non-streaming request in '{mode}' mode.")
                full_response_chunks = list(get_g4f_response_stream())
                if not full_response_chunks: return jsonify({"error": "Failed to generate a response from any provider."}), 500

                full_text = "".join(chunk.choices[0].delta.content for chunk in full_response_chunks if chunk.choices and chunk.choices[0].delta.content)
                last_chunk = full_response_chunks[-1]
                
                usage_data = None
                if last_chunk.usage:
                    usage_data = {"prompt_tokens": last_chunk.usage.prompt_tokens, "completion_tokens": last_chunk.usage.completion_tokens, "total_tokens": last_chunk.usage.total_tokens}
                
                api_response = {"id": f"chatcmpl-{uuid.uuid4().hex}", "object": "chat.completion", "created": int(time.time()), "model": last_chunk.model or "g4f", "choices": [{"index": 0, "message": { "role": "assistant", "content": full_text }, "finish_reason": "stop"}], "usage": usage_data}
                return jsonify(api_response)
        except Exception as e:
            app_gui.log(f"An unexpected error occurred in the main endpoint: {e}")
            return jsonify({"error": f"An internal server error occurred: {e}"}), 500
    return flask_app

def run_server(app_instance, host='127.0.0.1', port=1337):
    app = create_app(app_instance)
    app.run(host=host, port=port, threaded=True)