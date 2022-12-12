"""Package the built browser workstation alongside the Python application."""
import shutil, subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run(["npm", "--prefix", "frontend", "run", "build"], cwd=root, check=True)
target = root / "docreview/web"
if target.exists():
    shutil.rmtree(target)
shutil.copytree(root / "frontend/dist", target)
subprocess.run([sys.executable, "-m", "build", "--wheel"], cwd=root, check=True)
