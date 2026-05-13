"""Checkpoint helpers — save and load parquet files cleanly."""
import pandas as pd
from pathlib import Path


def save_checkpoint(df: pd.DataFrame, path: Path) -> None:
    """Save a DataFrame to parquet, creating parent dirs if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=True)
    print(f"[checkpoint] saved → {path.name}  ({len(df):,} rows)")


def load_checkpoint(path: Path) -> pd.DataFrame:
    """Load a parquet checkpoint. Raises FileNotFoundError if missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {path}")
    df = pd.read_parquet(path)
    print(f"[checkpoint] loaded ← {path.name}  ({len(df):,} rows)")
    return df


def checkpoint_exists(path: Path) -> bool:
    """Check whether a checkpoint file already exists."""
    return Path(path).exists()