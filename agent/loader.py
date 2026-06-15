from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from .config import PipelineConfig


def _looks_numeric(value: str) -> bool:
    try:
        float(str(value).strip().replace(",", ""))
        return True
    except (TypeError, ValueError):
        return False


def _find_data_start(file_path: str | Path, sep: str = ",") -> int:
    """Skip leading rows that do not match the most common field count."""
    counts: list[tuple[int, int]] = []
    with open(file_path, encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            stripped = line.strip()
            if not stripped:
                continue
            counts.append((index, len(stripped.split(sep))))

    if not counts:
        return 0

    expected = Counter(count for _, count in counts).most_common(1)[0][0]
    for index, count in counts:
        if count == expected:
            return index
    return 0


def _infer_has_header(file_path: str | Path, sep: str = ",", skiprows: int = 0) -> bool:
    """Guess whether the first row is a header or data."""
    peek = pd.read_csv(
        file_path,
        header=None,
        nrows=1,
        sep=sep,
        dtype=str,
        keep_default_na=False,
        skiprows=range(skiprows) if skiprows else None,
    )
    if peek.empty:
        return True

    first_row = peek.iloc[0].astype(str).str.strip()
    numeric_cells = sum(_looks_numeric(v) for v in first_row if v and v.lower() != "nan")
    non_empty = sum(bool(v and v.lower() != "nan") for v in first_row)
    if non_empty == 0:
        return True

    numeric_ratio = numeric_cells / non_empty
    # Header rows are usually mostly non-numeric tokens.
    if numeric_ratio >= 0.6:
        return False

    with_header = pd.read_csv(
        file_path,
        nrows=0,
        sep=sep,
        skiprows=range(skiprows) if skiprows else None,
    )
    col_names = [str(c) for c in with_header.columns]
    header_like = sum(not _looks_numeric(name) for name in col_names) / max(len(col_names), 1)
    return header_like >= 0.6


def load_data(file_path: str | Path, config: PipelineConfig) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    skiprows = config.skiprows
    if skiprows is None:
        skiprows = _find_data_start(path)

    has_header = config.has_header
    if has_header is None:
        has_header = _infer_has_header(path, skiprows=skiprows)

    skiprows_arg = range(skiprows) if skiprows else None
    read_kwargs = {
        "na_values": config.na_values,
        "skipinitialspace": config.strip_whitespace,
        "keep_default_na": True,
        "skiprows": skiprows_arg,
    }

    if has_header:
        df = pd.read_csv(path, header=0, **read_kwargs)
    else:
        names = config.column_names
        if names is None:
            width = pd.read_csv(path, header=None, nrows=1, skiprows=skiprows_arg).shape[1]
            names = [f"col_{i + 1}" for i in range(width)]
        df = pd.read_csv(path, header=None, names=names, **read_kwargs)

    df.columns = [str(c).strip() for c in df.columns]
    return df
