from __future__ import annotations

import pandas as pd

from .profiler import ColumnProfile


def deduplicate(
    df: pd.DataFrame,
    profiles: dict[str, ColumnProfile],
) -> pd.DataFrame:
    subset = [col for col, profile in profiles.items() if profile.dedup_include]
    if not subset:
        return df.copy()
    return df.drop_duplicates(subset=subset, keep="first")
