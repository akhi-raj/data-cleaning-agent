from __future__ import annotations

import pandas as pd

from .profiler import ColumnProfile


def detect_outliers_iqr(series: pd.Series) -> pd.Series:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return pd.Series(False, index=series.index)

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return (series < lower_bound) | (series > upper_bound)


def add_outlier_flags(
    df: pd.DataFrame,
    profiles: dict[str, ColumnProfile],
) -> pd.DataFrame:
    df = df.copy()

    for col, profile in profiles.items():
        if not profile.outlier_eligible:
            continue
        df[f"{col}_outlier"] = detect_outliers_iqr(df[col])

    return df
