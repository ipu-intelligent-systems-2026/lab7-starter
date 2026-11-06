# Quickstart (Windows PowerShell)
Write-Host "Running doctor check..." -ForegroundColor Cyan
python -m lab doctor
if ($LASTEXITCODE -ne 0) {
    Write-Error "Doctor check failed. See the checks marked ok=false above."
    exit 1
}
Write-Host "Starting OpenCode..." -ForegroundColor Green
if (Get-Command opencode -ErrorAction SilentlyContinue) {
    opencode
} else {
    Write-Warning "OpenCode CLI is not on PATH. Install it from https://opencode.ai/docs/"
}
