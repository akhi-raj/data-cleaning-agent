import pandas as pd


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values using rule-based strategies
    derived from profiling.

    Parameters:
        df (pd.DataFrame): Dataframe after type coercion

    Returns:
        pd.DataFrame: Dataframe with missing values handled
    """

    # Numeric columns (safe for median imputation)
    df["age"] = df["age"].fillna(df["age"].median())
    df["education_num"] = df["education_num"].fillna(df["education_num"].median())
    df["hours_per_week"] = df["hours_per_week"].fillna(df["hours_per_week"].median())

    # Categorical columns
    df["workclass"] = df["workclass"].fillna(df["workclass"].mode()[0])

    # High-cardinality categoricals
    df["occupation"] = df["occupation"].fillna("unknown")
    df["native_country"] = df["native_country"].fillna("unknown")

    return df
