import argparse
import json
import sys
from pathlib import Path

from agent.config import PipelineConfig
from agent.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the schema-agnostic data cleaning pipeline on a CSV file."
    )
    parser.add_argument("dataset", help="Path to the input CSV file")
    parser.add_argument(
        "-o",
        "--output",
        default="cleaned_output.csv",
        help="Path for the cleaned CSV output (default: cleaned_output.csv)",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Optional JSON config file for pipeline overrides",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Treat the first row as data (no column header row)",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="Treat the first row as column names",
    )
    parser.add_argument(
        "--report",
        help="Optional path to write a JSON cleaning report",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.no_header and args.header:
        print("Error: use only one of --no-header or --header.")
        sys.exit(1)

    config = PipelineConfig.from_json(args.config) if args.config else PipelineConfig()

    if args.no_header:
        config.has_header = False
    elif args.header:
        config.has_header = True

    print("Running data cleaning pipeline...")
    df, report = run_pipeline(args.dataset, config)

    output_path = Path(args.output)
    df.to_csv(output_path, index=False)
    print(f"Cleaning complete. Output saved to {output_path}")

    for line in report.summary_lines():
        print(f"  {line}")

    if args.report:
        report_path = Path(args.report)
        payload = {
            "input_path": report.input_path,
            "has_header": report.has_header,
            "rows_in": report.rows_in,
            "rows_out": report.rows_out,
            "columns_in": report.columns_in,
            "columns_out": report.columns_out,
            "outlier_columns_added": report.outlier_columns_added,
            "dedup_columns_used": report.dedup_columns_used,
            "column_profiles": {
                name: {
                    "inferred_type": p.inferred_type,
                    "missing_pct": p.missing_pct,
                    "unique_ratio": p.unique_ratio,
                    "impute_strategy": p.impute_strategy,
                    "outlier_eligible": p.outlier_eligible,
                    "dedup_include": p.dedup_include,
                    "flags": p.flags,
                }
                for name, p in report.profiles.items()
            },
        }
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"  Report saved to {report_path}")


if __name__ == "__main__":
    main()
