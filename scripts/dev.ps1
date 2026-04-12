param(
    [ValidateSet("bootstrap", "install", "test", "run", "copy-config", "run-starter", "stage-feed", "publish")]
    [string]$Task = "run"
)

$ErrorActionPreference = "Stop"

function Get-VenvPython {
    return Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
}

function Ensure-Venv {
    $venvPython = Get-VenvPython
    if (-not (Test-Path $venvPython)) {
        Write-Host "Creating virtual environment with py -3..."
        Push-Location (Join-Path $PSScriptRoot "..")
        try {
            py -3 -m venv .venv
        }
        finally {
            Pop-Location
        }
    }
}

function Run-InRepo([string]$Command) {
    Push-Location (Join-Path $PSScriptRoot "..")
    try {
        Invoke-Expression $Command
    }
    finally {
        Pop-Location
    }
}

switch ($Task) {
    "bootstrap" {
        Ensure-Venv
        Run-InRepo ".\.venv\Scripts\python -m pip install --upgrade pip"
        Run-InRepo ".\.venv\Scripts\python -m pip install -r requirements.txt"
    }
    "install" {
        Ensure-Venv
        Run-InRepo ".\.venv\Scripts\python -m pip install -r requirements.txt"
    }
    "test" {
        Ensure-Venv
        Run-InRepo ".\.venv\Scripts\python -m pytest -q -rA"
    }
    "run" {
        Ensure-Venv
        Run-InRepo ".\.venv\Scripts\python -m src.aggregator"
    }
    "copy-config" {
        Run-InRepo "Copy-Item config.starter.yaml config.yaml -Force"
    }
    "run-starter" {
        Ensure-Venv
        Run-InRepo "`$env:NEWS_FEED_CONFIG_PATH='config.starter.yaml'; .\.venv\Scripts\python -m src.aggregator"
    }
    "stage-feed" {
        Run-InRepo "git add output/*.xml state/seen_hashes.json"
    }
    "publish" {
        Ensure-Venv
        Run-InRepo "`$env:NEWS_FEED_CONFIG_PATH='config.starter.yaml'; .\.venv\Scripts\python -m src.aggregator"
        Run-InRepo "git add output/*.xml state/seen_hashes.json"
        Run-InRepo "git diff --cached --quiet; if (`$LASTEXITCODE -ne 0) { git commit -m 'chore: update generated feed artifacts' } else { Write-Host 'No feed artifact changes to commit.' }"
    }
}
