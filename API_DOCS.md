# API Docs

Welcome to the documentation for the Moreweb AI Runtime. This guide provides all the information you need to integrate the local AI server into your applications, scripts, and services.

The API is designed to be **OpenAI-compatible**, meaning you can often use it as a drop-in replacement with libraries and tools that support the OpenAI Chat Completions API.

## Base URL

By default, the Moreweb AI Runtime server runs on your local machine.

*   **Base URL:** `http://127.0.0.1:1337`
*   **Full Endpoint:** `http://127.0.0.1:1337/v1/chat/completions`

---

## Endpoint: Chat Completions

This is the primary endpoint for all text generation tasks.

### `POST /v1/chat/completions`

This endpoint creates a model response for the given conversation. It supports both standard (blocking) and streaming responses.

#### Headers

| Header          | Value                 | Required |
| --------------- | --------------------- | -------- |
| `Content-Type`  | `application/json`    | Yes      |

#### Request Body

The request body is a JSON object with the following fields:

| Field      | Type               | Required | Description                                                                                                                              |
| ---------- | ------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `messages` | `array` of objects | Yes      | A list of message objects representing the conversation history.                                                                         |
| `stream`   | `boolean`          | No       | If `true`, the server will send back a stream of partial completions as they are generated. Defaults to `false`.                           |

#### The `message` Object

Each object in the `messages` array has the following structure:

| Field     | Type     | Required | Description                                                                                             |
| --------- | -------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `role`    | `string` | Yes      | The role of the message author. Must be one of `system`, `user`, or `assistant`.                        |
| `content` | `string` | Yes      | The text content of the message.                                                                        |

---

## Responses

### Successful Response (Non-Streaming)

If `stream` is `false` or omitted, you will receive a single JSON object upon completion.

**Status Code:** `200 OK`

**Example Body:**
```json
{
  "id": "chatcmpl-a1b2c3d4e5",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "g4f",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```

### Successful Response (Streaming)

If `stream` is `true`, the server uses **Server-Sent Events (SSE)**. You will receive a stream of `data:` chunks, where each chunk is a JSON object representing a part of the response.

**Status Code:** `200 OK`
**Content-Type:** `text/event-stream`

The stream is terminated by a final message: `data: [DONE]`.

**Example Stream:**
```
data: {"id":"chatcmpl-x1y2z3","object":"chat.completion.chunk","created":1677652288,"model":"g4f-stream","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-x1y2z3","object":"chat.completion.chunk","created":1677652288,"model":"g4f-stream","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-x1y2z3","object":"chat.completion.chunk","created":1677652288,"model":"g4f-stream","choices":[{"index":0,"delta":{"content":" How can"},"finish_reason":null}]}

data: {"id":"chatcmpl-x1y2z3","object":"chat.completion.chunk","created":1677652288,"model":"g4f-stream","choices":[{"index":0,"delta":{"content":" I assist you"},"finish_reason":null}]}

data: {"id":"chatcmpl-x1y2z3","object":"chat.completion.chunk","created":1677652288,"model":"g4f-stream","choices":[{"index":0,"delta":{"content":" today?"},"finish_reason":null}]}

data: [DONE]

```

### Error Response

If a request fails, you will receive a JSON object with an error description.

**Status Code:** `4xx` or `5xx`

**Example Body:**
```json
{
  "error": "The 'messages' field is required."
}
```

---

## Usage Examples

### cURL

#### Non-Streaming Request
```bash
curl http://127.0.0.1:1337/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

#### Streaming Request
The `-N` flag disables buffering, which is essential for viewing streams.
```bash
curl -N http://127.0.0.1:1337/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Write a short poem about the moon."}
    ],
    "stream": true
  }'
```

### Python (with `requests`)

#### Non-Streaming Request
```python
import requests
import json

API_URL = "http://127.0.0.1:1337/v1/chat/completions"

payload = {
    "messages": [
        {"role": "user", "content": "What is the capital of France?"}
    ]
}

try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    data = response.json()
    print(data['choices'][0]['message']['content'])
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

#### Streaming Request
```python
import requests
import json

API_URL = "http://127.0.0.1:1337/v1/chat/completions"

payload = {
    "messages": [
        {"role": "user", "content": "Write a short poem about the moon."}
    ],
    "stream": True
}

try:
    with requests.post(API_URL, json=payload, stream=True) as response:
        response.raise_for_status()
        print("AI Response: ", end="", flush=True)
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    content = decoded_line[5:].strip()
                    if content == "[DONE]":
                        break
                    try:
                        chunk = json.loads(content)
                        text_chunk = chunk['choices'][0]['delta'].get('content', '')
                        print(text_chunk, end="", flush=True)
                    except json.JSONDecodeError:
                        continue
    print() # Final newline
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

### JavaScript (Node.js with `node-fetch`)

#### Non-Streaming Request
```javascript
const fetch = require('node-fetch');

const API_URL = "http://127.0.0.1:1337/v1/chat/completions";

const payload = {
    messages: [
        { role: "user", content: "What is the capital of France?" }
    ]
};

async function getCompletion() {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data.choices[0].message.content);
    } catch (error) {
        console.error("Error fetching completion:", error);
    }
}

getCompletion();
```

#### Streaming Request
```javascript
const fetch = require('node-fetch');

const API_URL = "http://127.0.0.1:1337/v1/chat/completions";

const payload = {
    messages: [
        { role: "user", content: "Write a short poem about the moon." }
    ],
    stream: true
};

async function getStreamingCompletion() {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        process.stdout.write("AI Response: ");
        const decoder = new TextDecoder();
        for await (const chunk of response.body) {
            const decodedChunk = decoder.decode(chunk);
            const lines = decodedChunk.split('\n').filter(line => line.trim() !== '');
            for (const line of lines) {
                if (line.startsWith('data:')) {
                    const content = line.substring(5).trim();
                    if (content === '[DONE]') {
                        process.stdout.write('\n');
                        return;
                    }
                    try {
                        const jsonChunk = JSON.parse(content);
                        const textChunk = jsonChunk.choices[0].delta.content || '';
                        process.stdout.write(textChunk);
                    } catch (e) {
                        // Ignore non-JSON lines
                    }
                }
            }
        }
    } catch (error) {
        console.error("\nError fetching streaming completion:", error);
    }
}

getStreamingCompletion();
```