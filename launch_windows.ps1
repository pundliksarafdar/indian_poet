<#
Windows PowerShell launcher for the multilingual agents project.

Usage:
  .\launch_windows.ps1          # create venv if needed, install deps, run
  .\launch_windows.ps1 -Reinstall # force reinstall requirements

# The script creates/uses a local .venv directory and runs `python agents.py`.
# It relies on agents.py to load `.env` next to the script.
#>

param(
    [switch]$Reinstall
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) {
    python -m venv $venv
}

$activate = Join-Path $venv "Scripts\Activate.ps1"
if (Test-Path $activate) {
    & $activate
} else {
    Write-Host "Activation script not found; ensure Python created the venv correctly." -ForegroundColor Yellow
}

if ($Reinstall) {
    pip install --upgrade pip
    pip install -r requirements.txt
} else {
    pip install -r requirements.txt
}

# Forward any provided arguments (e.g. -Topic "monsoon") to the Python script
& python agents.py @args