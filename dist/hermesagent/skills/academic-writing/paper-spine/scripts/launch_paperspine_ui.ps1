param(
    [string]$OutputDir = "paper_rewriting_output",
    [switch]$InPlace
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wizard = Join-Path $scriptDir "intake_wizard.py"

if (-not (Test-Path -LiteralPath $wizard)) {
    throw "PaperSpine intake wizard not found: $wizard"
}

if ($InPlace) {
    chcp 65001 > $null
    $env:PYTHONUTF8 = "1"
    $OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
    python $wizard --keyboard-ui --output-dir $OutputDir
    exit $LASTEXITCODE
}

$cwd = (Get-Location).Path
$escapedCwd = $cwd.Replace("'", "''")
$escapedWizard = $wizard.Replace("'", "''")
$escapedOutput = $OutputDir.Replace("'", "''")

$command = @"
Set-Location -LiteralPath '$escapedCwd'
chcp 65001 > `$null
`$env:PYTHONUTF8 = '1'
`$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
python '$escapedWizard' --keyboard-ui --output-dir '$escapedOutput'
Write-Host ''
Write-Host 'PaperSpine intake finished. Config files are in: $escapedOutput'
Write-Host 'Close this window after checking the result.'
"@

Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    $command
)
