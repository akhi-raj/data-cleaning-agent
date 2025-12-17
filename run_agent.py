import sys
from agent.pipeline import run_pipeline


def main():
    """
    Entry point for running the data cleaning agent.
    Usage:
        python run_agent.py <path_to_dataset>
    """

    if len(sys.argv) != 2:
        print("Usage: python run_agent.py <path_to_dataset>")
        sys.exit(1)

    file_path = sys.argv[1]

    print("🚀 Running data cleaning agent...")
    df = run_pipeline(file_path)

    output_path = "cleaned_output.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Data cleaning complete. Output saved to {output_path}")


if __name__ == "__main__":
    main()
