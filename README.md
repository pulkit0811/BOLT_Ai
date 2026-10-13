# Bolt AI

Bolt AI is a Windows-first personal desktop AI assistant with a Python provider and storage layer plus a React workspace frontend. It combines private conversations, Ollama model connectivity, persistent SQLite history, and a focused archive-style interface.

## Frontend development

Start the local Bolt API from the project root:

```powershell
python -m app.web_server
```

In another terminal, start the React workspace:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite address shown in the terminal. The frontend proxies `/api` requests to the local Bolt API on port 8765.

## Bolt launcher

The PySide6 launcher starts the local API, serves the built React workspace, opens the browser interface, and adds Bolt to the Windows system tray:

```powershell
cd frontend
npm run build
cd ..
.\.venv\Scripts\python.exe -m app.launcher
```

For the fastest repeatable Ollama demo, use the included PowerShell launcher after building the frontend:

```powershell
.\run_bolt.ps1
```

It uses `gemma4:cloud` by default and opens the Bolt workspace automatically. Override the model before launching when using another Ollama model:

```powershell
$env:BOLT_MODEL = "gemma4:e2b"
.\run_bolt.ps1
```

Set `BOLT_OPEN_BROWSER=0` before launching when you want to open the workspace manually in another browser.

Use the tray menu to reopen Bolt, preview the listening glow, toggle voice listening, or quit the launcher. The local Vosk engine waits for “Bolt”, shows the listening glow, transcribes the question, and submits it to the active conversation.

The voice model is loaded from `models/vosk-model-small-en-us-0.15`. Set `BOLT_VOICE_MODEL` to use another local Vosk model or `BOLT_VOICE_DEVICE` to select a specific Windows microphone device. Set `BOLT_OPEN_BROWSER=0` when starting the launcher if you want to open `http://127.0.0.1:5173` manually in another browser.

The launcher uses the local API on port 8765 and the built workspace on port 5173. `AI_API_ENDPOINT` is `http://127.0.0.1:11434/v1` for the local Ollama bridge.
