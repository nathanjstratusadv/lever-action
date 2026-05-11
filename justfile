set windows-shell := ["powershell.exe", "-c"]
set dotenv-load
set dotenv-filename := "development.env"

PYTHON := if os() == "linux" { ".venv/bin/python" } else { ".venv/Scripts/python.exe" }

export PYTHONPATH := "src"

default:
	@just --list --no-aliases

run:
	{{PYTHON}} main.py

fmt:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

clean:
	uv run pytest --cache-clear
	Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .ruff_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
	Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
	Get-ChildItem -Path . -Recurse -Directory -Filter ".pytest_cache" | Remove-Item -Recurse -Force

test:
	uv run pytest tests/ -v --tb=short

test-coverage:
	uv run pytest tests/ -v --cov=src/lever_action/services --cov=src/lever_action/storage --cov-report=term-missing --tb=short

prod:
	{{PYTHON}} main.py

package:
	uv run python generate_icon.py
	uv run pyinstaller lever_action.spec --clean -y

exe:
	.\dist\lever_action\lever_action.exe

release: package
	git tag v$($PYTHON -c "from lever_action import __version__; print(__version__)")
	$env:DistDir = "$PWD\dist\lever_action"
	& iscc installer\setup.iss
	git add -A && git commit -m "Release v$($PYTHON -c "from lever_action import __version__; print(__version__)")" || true
	git push
	& "C:\Program Files\GitHub CLI\gh.exe" release create v$($PYTHON -c "from lever_action import __version__; print(__version__)") dist\LeverAction-Setup.exe --title "Lever Action v$($PYTHON -c "from lever_action import __version__; print(__version__)")" --notes "Release" --repo nathanjstratusadv/lever-action

msix:
	@if (-not (Get-Command MakeAppx.exe -ErrorAction SilentlyContinue)) { winget install --id Microsoft.MSIX-Toolkit -e --accept-source-agreements --accept-package-agreements }
	New-Item -ItemType Directory -Force -Path dist\lever_action\Package
	Copy-Item -Path AppxManifest.xml -Destination dist\lever_action\Package\AppxManifest.xml -Force
	MakeAppx.exe package /d dist\lever_action /p lever_action.msix /v

msi: package
	@if (-not (Get-Command iscc -ErrorAction SilentlyContinue)) { winget install --id JRSoftware.InnoSetup -e --accept-source-agreements --accept-package-agreements }
	$version = & .venv/Scripts/python.exe -c "from lever_action import __version__; print(__version__)" ; powershell -ExecutionPolicy Bypass -File installer\build_msi.ps1 -Version $version