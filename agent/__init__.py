"""Schema-agnostic data cleaning pipeline."""

from .config import PipelineConfig
from .pipeline import PipelineReport, run_pipeline

__all__ = ["PipelineConfig", "PipelineReport", "run_pipeline"]
