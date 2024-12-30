<div align="center">

# 🤖 FreeAiApi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Cost](https://img.shields.io/badge/Cost-FREE-brightgreen.svg)]()

✨ A completely free solution for AI integration - No API keys required! ✨

A powerful Flask-based API providing seamless integration with free AI models (ChatGPT and Grok), featuring robust session management and multi-conversation support. Zero cost involved except for hosting!

[Features](#-features) • [Installation](#-installation) • [API Reference](#️-api-routes) • [Documentation](#️-configuration-options) • [Contributing](#-contributing)


</div>

> 💡 **Zero Cost AI Solution**: This project requires NO API keys and has NO usage costs! Just deploy and start using AI capabilities completely free.

## ✨ Features

- 🤖 Multiple AI model support (ChatGPT, Grok)
- 🔄 Smart session management
- 🔒 IP-based access control
- 🎫 Token-based authentication
- ⚙️ Environment-based configuration
- 🧹 Automatic session cleanup
- 👨‍💼 Administrative controls
- 📝 Comprehensive logging
- 📂 File attachment support for Grok model
- ⏳ Asynchronous request processing via queue

## 📋 Requirements

- 🐍 Python 3.8 or higher
- 🌐 Chrome browser (for ChatGPT client)
- 🔑 Active Grok account (for Grok client)

## 🚀 Installation

<details>
<summary>Click to expand installation steps</summary>

1. Clone the repository:
```bash
git clone https://github.com/vibheksoni/FreeAiApi.git
cd FreeAiApi
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```env
# Authentication
AUTH_TOKEN=your_auth_token_here

# Model Tokens
GROK_BEARER_TOKEN=your_grok_bearer_token
GROK_CSRF_TOKEN=your_grok_csrf_token
GROK_COOKIES=your_grok_cookies

# Server Configuration
HOST=127.0.0.1
PORT=5000
DEBUG=false
RELOAD_ENV=true
ALLOWED_IPS=127.0.0.1,::1
LOCAL_ONLY=true

# Session Management
MAX_SESSIONS=100
SESSION_TIMEOUT_MINUTES=30
CLEANUP_INTERVAL_MINUTES=5
```

</details>

## 🛣️ API Routes

<details>
<summary><b>Chat Endpoints</b></summary>

### Send Message
- **URL:** `/api/chat/send`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
  - `X-Auth-Token: your_auth_token`
- **Request Body:**
```json
{
    "model": "gpt|grok",
    "message": "Your message here",
    "session_id": "optional_session_id",
    "files": [
      {
        "filename": "image.jpg",
        "base64": "base64_encoded_content"
      }
    ]
}
```
- **Success Response:**
```json
{
    "status": true,
    "message": "Success",
    "data": {
        "response": "AI model response",
        "session_id": "session_identifier"
    }
}
```
- **Error Response:**
```json
{
    "status": false,
    "message": "Error description",
    "data": null
}
```
- **Common HTTP Status Codes:**
  - 200: Success
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden (IP restricted)
  - 500: Internal Server Error
</details>

<details>
<summary><b>Queue Endpoints</b></summary>

### Submit Task
- **URL:** `/api/queue/submit`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
  - `X-Auth-Token: your_auth_token`
- **Request Body:**
```json
{
    "model": "gpt|grok",
    "message": "Your message here",
    "session_id": "optional_session_id",
    "files": [
      {
        "filename": "image.jpg",
        "base64": "base64_encoded_content"
      }
    ]
}
```
- **Success Response:**
```json
{
    "status": true,
    "message": "Task submitted",
    "data": {
        "transaction_id": "transaction_identifier"
    }
}
```
- **Error Response:**
```json
{
    "status": false,
    "message": "Error description",
    "data": null
}
```
- **Common HTTP Status Codes:**
  - 200: Success
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden (IP restricted)
  - 500: Internal Server Error

### Check Status
- **URL:** `/api/queue/status/<transaction_id>`
- **Method:** `GET`
- **Headers:**
  - `X-Auth-Token: your_auth_token`
- **Success Response:**
```json
{
    "status": true,
    "message": "Status retrieved",
    "data": {
        "transaction_id": "transaction_identifier",
        "status": "pending|completed|failed",
        "result": "AI model response if completed"
    }
}
```
- **Error Response:**
```json
{
    "status": false,
    "message": "Error description",
    "data": null
}
```
- **Common HTTP Status Codes:**
  - 200: Success
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden (IP restricted)
  - 500: Internal Server Error
</details>

<details>
<summary><b>Admin Endpoints</b></summary>

### Get Active Sessions
- **URL:** `/api/admin/sessions`
- **Method:** `GET`
- **Headers:**
  - `X-Auth-Token: your_auth_token`
- **Success Response:**
```json
{
    "status": true,
    "message": "Active sessions retrieved",
    "data": {
        "count": 1,
        "sessions": [
            {
                "session_id": "uuid",
                "model_type": "gpt",
                "created_at": "2024-01-01T00:00:00",
                "last_accessed": "2024-01-01T00:05:00",
                "conversation_length": 2
            }
        ]
    }
}
```

### Clear All Sessions
- **URL:** `/api/admin/sessions/clear`
- **Method:** `POST`
- **Headers:**
  - `X-Auth-Token: your_auth_token`
- **Success Response:**
```json
{
    "status": true,
    "message": "All sessions cleared",
    "data": {
        "cleared_count": 5
    }
}
```

### Get Session Statistics
- **URL:** `/api/admin/sessions/stats`
- **Method:** `GET`
- **Headers:**
  - `X-Auth-Token: your_auth_token`
- **Success Response:**
```json
{
    "status": true,
    "message": "Session statistics retrieved",
    "data": {
        "created_total": 10,
        "expired_total": 3,
        "cleared_total": 2,
        "active_count": 5,
        "active_by_model": {
            "gpt": 3,
            "grok": 2
        }
    }
}
```
</details>

<details>
<summary><b>Health Check</b></summary>

### Health Endpoint
- **URL:** `/api/health`
- **Method:** `GET`
- **Headers:**
  - `X-Auth-Token: your_auth_token`
- **Success Response:**
```json
{
    "status": true,
    "message": "API is running",
    "data": {
        "service": "healthy"
    }
}
```
</details>

## ⚙️ Configuration Options

<details>
<summary>Click to view all configuration options</summary>

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| AUTH_TOKEN | Authentication token for API access | Required |
| HOST | Server host address | 0.0.0.0 |
| PORT | Server port | 5000 |
| DEBUG | Enable debug mode | false |
| RELOAD_ENV | Auto-reload environment changes | true |
| ALLOWED_IPS | Comma-separated list of allowed IPs | 127.0.0.1,::1 |
| LOCAL_ONLY | Restrict to local addresses only | true |
| MAX_SESSIONS | Maximum concurrent sessions | 100 |
| SESSION_TIMEOUT_MINUTES | Session timeout period | 30 |
| CLEANUP_INTERVAL_MINUTES | Cleanup check interval | 5 |

</details>

## 🧪 Running Tests

```bash
python tests/test_api.py
```

## ⚠️ Error Handling

<details>
<summary>Error Response Format</summary>

All endpoints return consistent error responses:
```json
{
    "status": false,
    "message": "Error description",
    "data": null
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden (IP restricted)
- 500: Internal Server Error

</details>

## 📝 Logging

<details>
<summary>Logging Details</summary>

Logs are stored in the `logs` directory with the format `YYYY-MM-DD-HH-MM-error.log`. The logging system captures:
- API requests and responses
- Session management events
- Error messages and stack traces
- Configuration changes

</details>

## 🔒 Security Features

- 🔑 Token-based authentication
- 🛡️ IP address restrictions
- 🏠 Local-only mode option
- ⏰ Session timeouts
- 🧹 Automatic cleanup
- 🔄 Config hot-reloading
- 🔒 Thread-safe operations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🔱 Fork the repository
2. 🌿 Create your feature branch
3. 💻 Commit your changes
4. 🚀 Push to the branch
5. 📥 Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

<img src="https://github.com/vibheksoni.png" width="100" height="100" border-radius="50%">

**Vibhek Soni**
- GitHub: [@vibheksoni](https://github.com/vibheksoni)

## 🙏 Acknowledgements

Special thanks to these amazing projects:
- [Flask](https://flask.palletsprojects.com/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://requests.readthedocs.io/)
- [Selenium](https://www.selenium.dev/)
- [undetected_chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

---

<div align="center">
  
Made with ❤️ by [Vibhek Soni](https://github.com/vibheksoni)

<a href="#-freeaiapi">Back to top ⬆️</a>

</div>