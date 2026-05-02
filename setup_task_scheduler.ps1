#!/usr/bin/env pwsh
# Installs a daily Windows Task Scheduler job that runs the job search agent at 7 AM.
# Run once from an elevated (Admin) PowerShell prompt.
# Safe to re-run — overwrites any existing "JobSearchAgent" task.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script    = Join-Path $ScriptDir "run_job_search.ps1"

$Action  = New-ScheduledTaskAction `
    -Execute   "powershell.exe" `
    -Argument  "-NonInteractive -ExecutionPolicy Bypass -File `"$Script`"" `
    -WorkingDirectory $ScriptDir

$Trigger  = New-ScheduledTaskTrigger -Daily -At 7am

$Settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
    -TaskName "JobSearchAgent" `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Force | Out-Null

Write-Host ""
Write-Host "Task Scheduler job installed successfully." -ForegroundColor Green
Write-Host "  Name:      JobSearchAgent"
Write-Host "  Schedule:  Daily at 7:00 AM"
Write-Host "  Script:    $Script"
Write-Host ""
Write-Host "To run immediately:  Start-ScheduledTask -TaskName 'JobSearchAgent'"
Write-Host "To remove:           Unregister-ScheduledTask -TaskName 'JobSearchAgent' -Confirm:`$false"
