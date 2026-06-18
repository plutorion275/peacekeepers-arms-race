import nbformat, sys

for path in [
    "notebooks/05_rq1_panel_regression.ipynb",
    "notebooks/07_rq3_clustering.ipynb",
]:
    try:
        with open(path, encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        print(f"OK  {path}: {len(nb.cells)} cells, v{nb.nbformat}.{nb.nbformat_minor}")
    except Exception as e:
        print(f"ERR {path}: {e}")
        sys.exit(1)

print("Both notebooks parse cleanly.")
