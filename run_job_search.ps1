#!/usr/bin/env pwsh
# Job Search Agent runner for Windows PowerShell
# Usage:
#   .\run_job_search.ps1              # Full search + analysis + report
#   .\run_job_search.ps1 -DryRun      # Test connectivity, skip Claude
#   .\run_job_search.ps1 -Top 20      # Show top stored results
#   .\run_job_search.ps1 -Report      # Regenerate report from stored data
#   .\run_job_search.ps1 -Sources greenhouse,lever  # Specific sources only

param(
    [switch]$DryRun,
    [switch]$Report,
    [int]$Top = 0,
    [string[]]$Sources = @("greenhouse", "lever", "websearch")
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir    = Join-Path $ScriptDir "logs"
$LogFile   = Join-Path $LogDir "job_search_$(Get-Date -Format 'yyyy-MM-dd').log"

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

# ── Load .env if ANTHROPIC_API_KEY not already set ───────────────────────────
if (-not $env:ANTHROPIC_API_KEY) {
    $EnvFile = Join-Path $ScriptDir ".env"
    if (Test-Path $EnvFile) {
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)\s*$') {
                [System.Environment]::SetEnvironmentVariable(
                    $Matches[1].Trim(), $Matches[2].Trim(), "Process")
            }
        }
    }
}

if (-not $env:ANTHROPIC_API_KEY) {
    Write-Error @"
ANTHROPIC_API_KEY is not set.
  Option 1 (this session):  `$env:ANTHROPIC_API_KEY = "sk-ant-..."
  Option 2 (permanent):     Create a .env file in $ScriptDir
                             containing:  ANTHROPIC_API_KEY=sk-ant-...
"@
    exit 1
}

# ── Create venv if needed ────────────────────────────────────────────────────
$Venv   = Join-Path $ScriptDir ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Creating Python virtual environment..."
    python -m venv $Venv
    & $Python -m pip install -q --upgrade pip
    & $Python -m pip install -q -r (Join-Path $ScriptDir "requirements.txt")
    if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed"; exit 1 }
}

# ── Build argument list ──────────────────────────────────────────────────────
$AgentArgs = @("--sources") + $Sources
if ($DryRun)   { $AgentArgs += "--dry-run" }
if ($Report)   { $AgentArgs += "--report" }
if ($Top -gt 0){ $AgentArgs += @("--top", $Top) }

# ── Run ──────────────────────────────────────────────────────────────────────
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"$Timestamp — Starting job search agent" | Tee-Object -FilePath $LogFile -Append

Set-Location $ScriptDir
& $Python -m job_search.agent @AgentArgs 2>&1 | Tee-Object -FilePath $LogFile -Append

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"$Timestamp — Done" | Tee-Object -FilePath $LogFile -Append
