Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\backend"
try {
  if (-not (Test-Path ".venv")) {
    python -m venv .venv
  }
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  .\.venv\Scripts\python.exe -m pytest
}
finally {
  Pop-Location
}
