from __future__ import annotations

import pandas as pd

from .config import PipelineConfig
from .profiler import ColumnProfile


def validate(
    df: pd.DataFrame,
    profiles: dict[str, ColumnProfile],
    config: PipelineConfig,
) -> None:
    assert df.shape[0] > 0, "Dataset is empty after cleaning"
    assert df.shape[1] > 0, "Dataset has no columns"

    if config.validate_no_missing:
        imputed_cols = [
            col for col, profile in profiles.items() if profile.impute_strategy != "skip"
        ]
        for col in imputed_cols:
            if col in df.columns:
                assert df[col].isna().sum() == 0, f"Missing values remain in column '{col}'"

    for col, profile in profiles.items():
        if profile.inferred_type != "numeric" or col not in df.columns:
            continue
        assert pd.api.types.is_numeric_dtype(df[col]), f"Column '{col}' must be numeric"
