from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_NA_VALUES = ["?", "NA", "N/A", "na", "null", "None", ""]


@dataclass
class PipelineConfig:
    """Runtime options for the cleaning pipeline."""

    has_header: bool | None = None  # None = auto-detect
    column_names: list[str] | None = None
    na_values: list[str] = field(default_factory=lambda: list(DEFAULT_NA_VALUES))
    lowercase_categoricals: bool = True
    strip_whitespace: bool = True
    impute_overrides: dict[str, str] = field(default_factory=dict)
    skip_impute_columns: list[str] = field(default_factory=list)
    skip_outlier_columns: list[str] = field(default_factory=list)
    outlier_columns: list[str] | None = None  # None = auto from profiler
    dedup_subset: list[str] | None = None  # None = auto from profiler
    skip_dedup_columns: list[str] = field(default_factory=list)
    validate_no_missing: bool = True
    skiprows: int | None = None  # None = auto-skip malformed leading rows
    id_unique_ratio_threshold: float = 0.95
    high_cardinality_threshold: float = 0.5
    zero_inflation_threshold: float = 0.85
    numeric_type_threshold: float = 0.9

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipelineConfig:
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})

    @classmethod
    def from_json(cls, path: str | Path) -> PipelineConfig:
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
