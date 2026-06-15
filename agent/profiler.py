from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .config import PipelineConfig


@dataclass
class ColumnProfile:
    name: str
    inferred_type: str  # numeric | categorical | boolean | empty
    missing_pct: float
    unique_ratio: float
    numeric_confidence: float
    suspected_id: bool
    zero_inflation: float
    impute_strategy: str  # median | mode | unknown | skip
    outlier_eligible: bool
    dedup_include: bool
    flags: list[str] = field(default_factory=list)


def _detect_column_type(series: pd.Series, config: PipelineConfig) -> tuple[str, float, bool]:
    non_null = series.dropna()
    if len(non_null) == 0:
        return "empty", 0.0, False

    as_str = non_null.astype(str).str.strip()
    lower = as_str.str.lower()
    bool_tokens = {"true", "false", "yes", "no", "0", "1", "y", "n"}
    if lower.isin(bool_tokens).mean() > 0.95 and non_null.nunique() <= 2:
        return "boolean", 1.0, False

    numeric_ratio = pd.to_numeric(non_null, errors="coerce").notna().mean()
    unique_ratio = non_null.nunique() / len(series)
    suspected_id = unique_ratio >= config.id_unique_ratio_threshold and numeric_ratio >= config.numeric_type_threshold

    if numeric_ratio >= config.numeric_type_threshold:
        return "numeric", round(float(numeric_ratio), 3), suspected_id

    return "categorical", round(float(numeric_ratio), 3), suspected_id


def _choose_impute_strategy(
    profile_type: str,
    missing_pct: float,
    unique_ratio: float,
    suspected_id: bool,
    zero_inflation: float,
    column_name: str,
    config: PipelineConfig,
) -> str:
    if column_name in config.skip_impute_columns:
        return "skip"
    if column_name in config.impute_overrides:
        return config.impute_overrides[column_name]
    if missing_pct == 0:
        return "skip"
    if suspected_id:
        return "skip"
    if profile_type == "numeric":
        if zero_inflation >= config.zero_inflation_threshold:
            return "skip"
        return "median"
    if profile_type == "boolean":
        return "mode"
    if unique_ratio >= config.high_cardinality_threshold:
        return "unknown"
    return "mode"


def profile_dataframe(df: pd.DataFrame, config: PipelineConfig) -> dict[str, ColumnProfile]:
    profiles: dict[str, ColumnProfile] = {}

    for col in df.columns:
        series = df[col]
        missing_pct = round(float(series.isna().mean()), 4)
        non_null = series.dropna()
        unique_ratio = round(float(non_null.nunique() / len(series)), 4) if len(series) else 0.0

        col_type, numeric_confidence, suspected_id = _detect_column_type(series, config)

        zero_inflation = 0.0
        if col_type == "numeric" and len(non_null):
            numeric_vals = pd.to_numeric(non_null, errors="coerce").dropna()
            if len(numeric_vals):
                zero_inflation = round(float((numeric_vals == 0).mean()), 4)

        impute_strategy = _choose_impute_strategy(
            col_type, missing_pct, unique_ratio, suspected_id, zero_inflation, col, config
        )

        flags: list[str] = []
        if suspected_id:
            flags.append("suspected_id")
        if zero_inflation >= config.zero_inflation_threshold:
            flags.append("zero_inflated")
        if missing_pct > 0:
            flags.append("has_missing")
        if unique_ratio >= config.high_cardinality_threshold and col_type == "categorical":
            flags.append("high_cardinality")

        outlier_eligible = (
            col_type == "numeric"
            and not suspected_id
            and col not in config.skip_outlier_columns
            and zero_inflation < config.zero_inflation_threshold
        )
        if config.outlier_columns is not None:
            outlier_eligible = col in config.outlier_columns

        dedup_include = col not in config.skip_dedup_columns and not suspected_id
        if config.dedup_subset is not None:
            dedup_include = col in config.dedup_subset

        profiles[col] = ColumnProfile(
            name=col,
            inferred_type=col_type,
            missing_pct=missing_pct,
            unique_ratio=unique_ratio,
            numeric_confidence=numeric_confidence,
            suspected_id=suspected_id,
            zero_inflation=zero_inflation,
            impute_strategy=impute_strategy,
            outlier_eligible=outlier_eligible,
            dedup_include=dedup_include,
            flags=flags,
        )

    return profiles
