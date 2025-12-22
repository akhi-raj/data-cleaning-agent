import pandas as pd


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce columns into correct data types and normalize categorical text.

    Parameters:
        df (pd.DataFrame): Raw dataframe

    Returns:
        pd.DataFrame: Dataframe with corrected types
    """

    numeric_columns = [
        "age",
        "fnlwgt",
        "education_num",
        "capital_gain",
        "capital_loss",
        "hours_per_week",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    categorical_columns = [
        "workclass",
        "education",
        "marital_status",
        "occupation",
        "relationship",
        "race",
        "sex",
        "native_country",
        "income",
    ]

    for col in categorical_columns:
        df[col] = df[col].str.strip().str.lower()

    return df
