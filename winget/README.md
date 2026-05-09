# Winget Package Submission

## Overview

This directory contains the winget manifest files for submitting Lever Action to the Windows Package Manager repository.

## Prerequisites

1. **GitHub Releases**: You must have a GitHub release with the MSI attached.
2. **WiX Toolset**: Install via `winget install --id WiXToolset.WiXToolset` (requires admin).
3. **Git**: Required for submitting the PR.

## Build the MSI

```powershell
just msi
```

This will create `dist\LeverAction.msi`.

## Prepare for Submission

### 1. Create a GitHub Release

Push a tag and create a release on GitHub:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Then attach `dist\LeverAction.msi` to the release on GitHub.

### 2. Compute SHA256 Hash

```powershell
$hash = (Get-FileHash dist\LeverAction.msi -Algorithm SHA256).Hash
Write-Host $hash
```

### 3. Update Manifest Files

Edit `winget/default.yaml`:
- Replace `PackageVersion` with your version
- Replace both `Url` values with your GitHub release URL
- Replace `Sha256` and `InstallerSha256` with the hash from step 2

Edit `winget/license.yaml`:
- Replace the license text or URL

Edit `winget/installer.yaml`:
- Update version and URLs

### 4. Submit to winget-pkgs

```powershell
# Clone the winget-pkgs repo
git clone https://github.com/microsoft/winget-pkgs.git
cd winget-pkgs

# Create the manifest directory
mkdir -Path "manifests/l/LeverAction/LeverAction" -Force

# Copy manifest files
Copy-Item -Path "path/to/lever_action/winget/*.yaml" -Destination "manifests/l/LeverAction/LeverAction/"

# Create PR
git checkout -b lever-action-0.1.0
git add manifests/l/LeverAction/LeverAction/
git commit -m "Add Lever Action v0.1.0"
git push origin lever-action-0.1.0
```

Then create a pull request on https://github.com/microsoft/winget-pkgs

## Install via Winget (After Submission is Approved)

```powershell
winget install LeverAction.LeverAction
```

## Local Testing

You can test the manifest locally:

```powershell
winget validate --manifest winget/*.yaml
```
