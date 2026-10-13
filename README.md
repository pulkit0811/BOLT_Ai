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

The PySide6 launcher starts the local API, serves the built React workspace, and adds Bolt to the Windows system tray:

```powershell
cd frontend
npm run build
cd ..
.\.venv\Scripts\python.exe -m app.launcher
```

For the normal background assistant workflow, build the frontend once and run the included background launcher:

```powershell
cd frontend
npm run build
cd ..
.\run_bolt_background.ps1
```

The terminal returns immediately while Bolt stays in the system tray. It does not open a browser at startup. Say “Bolt” to wake it, wait for the glow near the taskbar, speak your question, and finish speaking. Bolt then opens the workspace and places the transcript in the composer for review and sending.

For a foreground launcher useful during development, use:

```powershell
.\run_bolt.ps1
```

It uses `gemma4:cloud` by default and keeps the browser closed until voice input is received. Override the model before launching when using another Ollama model:

```powershell
$env:BOLT_MODEL = "gemma4:e2b"
.\run_bolt.ps1
```

Set `BOLT_OPEN_BROWSER=1` before launching when you want the workspace to open immediately for UI testing.

Use the tray menu to reopen Bolt, preview the listening glow, toggle voice listening, or quit the launcher. The local Vosk engine waits for “Bolt”, shows the listening glow, transcribes the question, opens the workspace, and places the transcript in the composer.

The voice model is loaded from `models/vosk-model-small-en-us-0.15`. Set `BOLT_VOICE_MODEL` to use another local Vosk model or `BOLT_VOICE_DEVICE` to select a specific Windows microphone device. Bolt listens locally through the selected Windows microphone and does not send audio to Ollama.

The launcher uses the local API on port 8765 and the built workspace on port 5173. `AI_API_ENDPOINT` is `http://127.0.0.1:11434/v1` for the local Ollama bridge.
