from __future__ import annotations

import pandas as pd

from .profiler import ColumnProfile


def handle_missing_values(
    df: pd.DataFrame,
    profiles: dict[str, ColumnProfile],
) -> pd.DataFrame:
    df = df.copy()

    for col, profile in profiles.items():
        if profile.impute_strategy == "skip":
            continue

        if profile.impute_strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif profile.impute_strategy == "mode":
            mode = df[col].mode(dropna=True)
            if len(mode):
                df[col] = df[col].fillna(mode.iloc[0])
        elif profile.impute_strategy == "unknown":
            df[col] = df[col].fillna("unknown")

    return df
