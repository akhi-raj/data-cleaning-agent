from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .config import PipelineConfig
from .deduplication import deduplicate
from .loader import load_data
from .missing_values import handle_missing_values
from .outliers import add_outlier_flags
from .profiler import ColumnProfile, profile_dataframe
from .type_coercion import coerce_types
from .validation import validate


@dataclass
class PipelineReport:
    input_path: str
    rows_in: int
    rows_out: int
    columns_in: int
    columns_out: int
    has_header: bool
    profiles: dict[str, ColumnProfile] = field(repr=False)
    outlier_columns_added: list[str] = field(default_factory=list)
    dedup_columns_used: list[str] = field(default_factory=list)

    def summary_lines(self) -> list[str]:
        lines = [
            f"Input: {self.input_path}",
            f"Header detected: {self.has_header}",
            f"Rows: {self.rows_in} -> {self.rows_out}",
            f"Columns: {self.columns_in} -> {self.columns_out}",
        ]
        if self.outlier_columns_added:
            lines.append(f"Outlier flags: {', '.join(self.outlier_columns_added)}")
        if self.dedup_columns_used:
            lines.append(f"Dedup key: {', '.join(self.dedup_columns_used)}")
        return lines


def run_pipeline(
    file_path: str | Path,
    config: PipelineConfig | None = None,
) -> tuple[pd.DataFrame, PipelineReport]:
    config = config or PipelineConfig()
    path = Path(file_path)

    df = load_data(path, config)
    rows_in, columns_in = df.shape

    skiprows = config.skiprows if config.skiprows is not None else 0
    from .loader import _find_data_start, _infer_has_header

    if config.skiprows is None:
        skiprows = _find_data_start(path)

    has_header = config.has_header
    if has_header is None:
        has_header = _infer_has_header(path, skiprows=skiprows)

    profiles = profile_dataframe(df, config)
    df = coerce_types(df, profiles, config)
    df = handle_missing_values(df, profiles)
    df = add_outlier_flags(df, profiles)
    df = deduplicate(df, profiles)
    validate(df, profiles, config)

    outlier_cols = [c for c in df.columns if c.endswith("_outlier")]
    dedup_cols = [col for col, p in profiles.items() if p.dedup_include]

    report = PipelineReport(
        input_path=str(path),
        rows_in=rows_in,
        rows_out=len(df),
        columns_in=columns_in,
        columns_out=df.shape[1],
        has_header=bool(has_header),
        profiles=profiles,
        outlier_columns_added=outlier_cols,
        dedup_columns_used=dedup_cols,
    )
    return df, report
