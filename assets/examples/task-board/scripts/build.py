import py_compile
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for path in (root / "app").glob("*.py"):
    py_compile.compile(str(path), doraise=True)
output = root / "dist"
output.mkdir(exist_ok=True)
shutil.copytree(root / "web", output / "web", dirs_exist_ok=True)
print("Python compiled; static assets copied to dist/web")
