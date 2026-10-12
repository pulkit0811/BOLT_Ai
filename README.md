# Bolt AI

Bolt AI is a Windows-first personal desktop AI assistant built with PySide6. It combines a polished local chat workspace with a provider layer designed for real model integrations, persistent conversations, and future voice control.

## Current status

Stage 2 is implemented.

- Light premium interface using white, lavender, and purple accents.
- Persistent SQLite conversations and messages.
- Conversation search, rename, delete, and restore after restart.
- Settings dialog for provider, model, endpoint, timeout, and streaming.
- Local mock provider for offline development.
- OpenAI provider using the official Python SDK and Responses API.
- Ollama provider for local models and Ollama Cloud models.
- Background response worker with streaming text updates.
- Markdown response rendering and copy-response action.
- API keys remain in environment variables and are not stored in SQLite.

The microphone, wake word, local transcription, VAD, and listening overlay are not implemented yet. They are planned for Stage 3 and Stage 4.

## Structure

```text
app/
  main.py
  core/
  ai/
  storage/
  ui/
  workers/
tests/
```

## Requirements

- Windows 10 or 11.
- Python 3.11 through 3.14.
- A working desktop session for Qt.

## Install and run

From the repository root in PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m app.main
```

Run checks:

```powershell
python -m pytest -p no:cacheprovider
python -m ruff check .
```

## Mock mode

Mock mode is the default and requires no network or API key.

```powershell
$env:AI_PROVIDER = "mock"
python -m app.main
```

## OpenAI mode

Set the API key before launching Bolt AI:

```powershell
$env:AI_PROVIDER = "openai"
$env:AI_API_KEY = "your-api-key"
$env:AI_MODEL = "gpt-5.5"
$env:AI_STREAMING = "true"
python -m app.main
```

The optional `AI_API_ENDPOINT` variable can point to a compatible API base URL. `AI_REQUEST_TIMEOUT` defaults to 60 seconds. The settings dialog can persist the non-secret provider settings locally. Environment variables take precedence over saved values.

The OpenAI API key is never written to the local database. Do not commit `.env` files or credentials.

## Ollama local mode

Install Ollama and download the local Qwen model:

```powershell
ollama run qwen3.5
```

Use the local model in Bolt AI:

```powershell
$env:AI_PROVIDER = "ollama"
$env:AI_API_ENDPOINT = "http://localhost:11434/v1"
$env:AI_API_KEY = "ollama"
$env:AI_MODEL = "qwen3.5"
python -m app.main
```

The Settings dialog keeps Bolt's interface and lets you select Ollama without opening an Ollama interface. Qwen 3.5's default tag is currently about 6.6 to 7.6 GB; use `qwen3.5:4b` if your laptop has less available memory.

For Ollama Cloud models, sign in, create an API key, and use the cloud endpoint:

```powershell
ollama signin
$env:AI_PROVIDER = "ollama"
$env:AI_API_ENDPOINT = "https://ollama.com/v1"
$env:AI_API_KEY = "your-ollama-api-key"
$env:AI_MODEL = "deepseek-v4.1-flash:cloud"
python -m app.main
```

Cloud usage follows the allowance and billing rules of your Ollama account. The Qwen local configuration does not send prompts to Ollama Cloud.

## Local data

Bolt AI stores conversations and non-secret settings in `bolt_ai.db` under the Windows local application data directory by default. Set `BOLT_DATABASE_PATH` to choose another location.

## Privacy

Mock mode does not send messages over the network. OpenAI mode sends the conversation messages you submit to the configured provider. Raw audio is not captured or stored in Stage 2.

## Roadmap

1. Add microphone capture and a replaceable wake-word interface.
2. Add VAD-based query recording and local faster-whisper transcription.
3. Add the transparent animated listening overlay.
4. Add settings for voice lifecycle, system tray controls, and packaging.

## Screenshots

Screenshots will be added after the Windows UI review.

## License

No license has been selected.
