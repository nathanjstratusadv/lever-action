from __future__ import annotations

import shutil
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base_path = Path(sys.executable).parent
    src = base_path / "pythonnet" / "runtime" / "Python.Runtime.dll"
    if src.exists():
        import importlib.util

        spec = importlib.util.find_spec("pythonnet")
        if spec and spec.origin:
            pythonnet_dir = Path(spec.origin).parent
            dest = pythonnet_dir / "runtime" / "Python.Runtime.dll"
            if not dest.exists():
                dest.parent.mkdir(exist_ok=True)
                shutil.copy2(str(src), str(dest))
