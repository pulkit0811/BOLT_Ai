$env:AI_PROVIDER = "ollama"
$env:AI_MODEL = if ($env:BOLT_MODEL) { $env:BOLT_MODEL } else { "gemma4:cloud" }
$env:AI_API_ENDPOINT = if ($env:AI_API_ENDPOINT) { $env:AI_API_ENDPOINT } else { "http://127.0.0.1:11434/v1" }
$env:BOLT_OPEN_BROWSER = "0"

Start-Process -FilePath "$PSScriptRoot\.venv\Scripts\pythonw.exe" -ArgumentList "-m app.launcher" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
