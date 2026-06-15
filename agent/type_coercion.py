from __future__ import annotations

import pandas as pd

from .config import PipelineConfig
from .profiler import ColumnProfile


def coerce_types(
    df: pd.DataFrame,
    profiles: dict[str, ColumnProfile],
    config: PipelineConfig,
) -> pd.DataFrame:
    df = df.copy()

    for col, profile in profiles.items():
        if profile.inferred_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif profile.inferred_type == "boolean":
            normalized = df[col].astype(str).str.strip().str.lower()
            mapping = {
                "true": True,
                "false": False,
                "yes": True,
                "no": False,
                "y": True,
                "n": False,
                "1": True,
                "0": False,
            }
            df[col] = normalized.map(mapping)
        elif profile.inferred_type == "categorical":
            df[col] = df[col].astype("string")
            if config.strip_whitespace:
                df[col] = df[col].str.strip()
            if config.lowercase_categoricals:
                df[col] = df[col].str.lower()

    return df
