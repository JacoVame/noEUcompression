# setup.ps1 — Phase 0 environment bootstrap (Windows, PowerShell)
# Run from inside phase2\ :  .\setup.ps1  [-VenvDir <path>]
# Binary DoD: this script ends with "PHASE 0 SMOKE: OK" and exit code 0.
#
# NOTE: the venv deliberately lives OUTSIDE the repo tree. nltk >= 3.10 ships a
# CWD-import security guard (nltk/inisec.py, CWE-427 mitigation) that blocks any
# dependency resolving from a subdirectory of the current working directory —
# a venv inside the project folder is a permanent false positive that fails
# every nltk import. Out-of-tree venv is the structural fix; do NOT disable the
# guard via NLTK_DISABLE_IMPORT_SECURITY.

param(
    [string]$VenvDir = "$env:LOCALAPPDATA\noeu-venvs\phase2"
)

$ErrorActionPreference = "Stop"
$env:PYTHONSAFEPATH = "1"   # hygiene; also covers spawned worker interpreters

Write-Host "== [1/5] Creating venv at $VenvDir" -ForegroundColor Cyan
if (-not (Test-Path $VenvDir)) { python -m venv $VenvDir }
$py = Join-Path $VenvDir "Scripts\python.exe"
Set-Content -Path ".venv-path" -Value $py -Encoding ascii
& $py -m pip install --upgrade pip | Out-Null

Write-Host "== [2/5] Installing torch (CPU wheel)" -ForegroundColor Cyan
& $py -m pip install torch --index-url https://download.pytorch.org/whl/cpu

Write-Host "== [3/5] Installing requirements" -ForegroundColor Cyan
& $py -m pip install -r requirements.txt
& $py -m pip freeze > requirements.lock.txt

Write-Host "== [4/5] Downloading WordNet" -ForegroundColor Cyan
& $py -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"

Write-Host "== [5/5] Smoke test (the Phase 0 gate)" -ForegroundColor Cyan
& $py smoke.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "PHASE 0: FAILED — do not proceed to Phase 1." -ForegroundColor Red
    exit 1
}
Write-Host "PHASE 0: DONE — venv: $VenvDir (pointer in .venv-path); lock: requirements.lock.txt" -ForegroundColor Green
exit 0
