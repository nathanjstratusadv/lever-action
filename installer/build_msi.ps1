param(
    [string]$Version = "0.1.0.0",
    [string]$DistDir = "dist\lever_action",
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

$installerDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path $DistDir)) {
    Write-Host "ERROR: Dist directory not found. Run 'just package' first." -ForegroundColor Red
    exit 1
}

$isccPath = Get-Command iscc -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if (-not $isccPath) {
    $isccPath = Get-Command ISCC -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
}
if (-not $isccPath) {
    $searchPaths = @(
        "C:\Program Files (x86)\Inno Setup*\ISCC.exe",
        "C:\Program Files\Inno Setup*\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup*\ISCC.exe"
    )
    foreach ($pattern in $searchPaths) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $isccPath = $found.FullName
            break
        }
    }
}
if (-not $isccPath) {
    Write-Host "ERROR: 'iscc' not found. Inno Setup is required." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install it with:" -ForegroundColor Yellow
    Write-Host "  winget install --id JRSoftware.InnoSetup --accept-package-agreements --accept-source-agreements" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then run:" -ForegroundColor Yellow
    Write-Host "  just msi" -ForegroundColor Yellow
    exit 1
}

Write-Host "Building installer with Inno Setup..." -ForegroundColor Cyan

$issFile = Join-Path $installerDir "setup.iss"

$env:Version = $Version
$env:DistDir = (Resolve-Path $DistDir).Path
$env:ProjectDir = (Resolve-Path (Join-Path $installerDir "..")).Path

& $isccPath $issFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Installer created: $OutputDir\LeverAction-Setup.exe" -ForegroundColor Green
} else {
    Write-Host "ERROR: Inno Setup compilation failed." -ForegroundColor Red
    exit 1
}
