from __future__ import annotations

import shutil
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base_path = Path(sys.executable).parent
    target_dir = base_path / "_internal" / "pythonnet"

    if not target_dir.exists():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass is None:
            meipass = str(base_path / "_internal")

        src_dir = Path(meipass) / "pythonnet"
        if src_dir.exists():
            shutil.copytree(src_dir, target_dir)

    internal_path = str(base_path / "_internal")
    if internal_path not in sys.path:
        sys.path.insert(0, internal_path)
