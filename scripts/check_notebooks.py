import nbformat, sys
from pathlib import Path

notebook_dir = Path("notebooks")
paths = sorted(notebook_dir.glob("*.ipynb"))
if not paths:
    print("ERR: no notebooks found in notebooks/ -- wrong working directory?")
    sys.exit(1)

failed = []
for path in paths:
    try:
        with open(path, encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        print(f"OK  {path}: {len(nb.cells)} cells, v{nb.nbformat}.{nb.nbformat_minor}")
    except Exception as e:
        print(f"ERR {path}: {e}")
        failed.append(str(path))

if failed:
    print(f"\n{len(failed)}/{len(paths)} notebooks failed to parse: {failed}")
    sys.exit(1)
print(f"\nAll {len(paths)} notebooks parse cleanly.")
