# Data Cleaning Agent

A schema-agnostic, modular data cleaning pipeline for structured CSV datasets. The pipeline profiles each column automatically and applies type coercion, imputation, outlier flagging, deduplication, and validation without hard-coded column names.

## Features

- **Auto-profiling** — infers numeric, categorical, and boolean columns from data
- **Smart loading** — auto-detects headers, skips malformed leading rows, handles common missing markers (`?`, `NA`, `null`, etc.)
- **Type coercion** — converts columns to appropriate types and normalizes categorical text
- **Missing value handling** — median for numerics, mode for low-cardinality categoricals, `"unknown"` for high-cardinality
- **Outlier detection** — IQR-based flags (does not remove rows); skips ID-like and zero-inflated columns
- **Deduplication** — removes duplicate rows on non-ID columns
- **Optional config** — override auto-detected behavior per dataset

## Project Structure

```
data-cleaning-agent/
├── agent/
│   ├── config.py          # Pipeline configuration
│   ├── profiler.py        # Column profiling and strategy selection
│   ├── loader.py          # CSV loading with auto-detection
│   ├── type_coercion.py
│   ├── missing_values.py
│   ├── outliers.py
│   ├── deduplication.py
│   ├── validation.py
│   └── pipeline.py
├── examples/
│   └── adult_config.json  # Optional config for UCI Adult dataset
├── notebooks/             # Exploratory notebooks (original profiling work)
├── dataset/
├── run_agent.py
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Usage

Basic (fully automatic):

```bash
python run_agent.py path/to/data.csv
```

With output path and cleaning report:

```bash
python run_agent.py path/to/data.csv -o cleaned.csv --report report.json
```

With optional JSON config:

```bash
python run_agent.py path/to/data.csv -c examples/adult_config.json
```

Force header behavior:

```bash
python run_agent.py data.csv --no-header
python run_agent.py data.csv --header
```

### Config options

| Key | Description |
|-----|-------------|
| `has_header` | `true` / `false` / omit for auto-detect |
| `column_names` | List of names when CSV has no header |
| `na_values` | Missing value tokens (default: `?`, `NA`, `N/A`, `null`, etc.) |
| `skiprows` | Number of leading rows to skip (omit for auto-detect) |
| `impute_overrides` | Per-column imputation: `median`, `mode`, `unknown`, `skip` |
| `skip_impute_columns` | Columns to leave unchanged |
| `skip_outlier_columns` | Numeric columns to exclude from IQR flagging |
| `outlier_columns` | Explicit list of columns to flag (overrides auto) |
| `dedup_subset` | Explicit dedup key columns |
| `skip_dedup_columns` | Columns excluded from dedup key |

## Example: UCI Adult dataset

```bash
python run_agent.py ./dataset/nyc.test -c examples/adult_config.json -o cleaned_output.csv
```

## Output

- Cleaned CSV at the path given by `-o` (default: `cleaned_output.csv`)
- Optional JSON report with row/column counts and per-column profiles

Outlier columns are added as boolean flags (e.g. `age_outlier`) rather than removing rows.

## Notes

- Works on any well-formed CSV; optional config fine-tunes behavior for known schemas.
- The `notebooks/` folder contains the original Adult-dataset profiling that informed default heuristics.
