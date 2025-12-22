import pandas as pd

def load_data(file_path: str, columns: list) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        names=columns,
        na_values="?",
        skipinitialspace=True
    )
    return df
