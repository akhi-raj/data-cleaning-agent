import pandas as pd


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate records using conservative identity rules.

    Parameters:
        df (pd.DataFrame): Dataframe after cleaning and outlier flagging

    Returns:
        pd.DataFrame: Deduplicated dataframe
    """

    dedup_columns = [
        "age",
        "workclass",
        "education",
        "education_num",
        "marital_status",
        "occupation",
        "relationship",
        "race",
        "sex",
        "hours_per_week",
        "native_country",
        "income",
    ]

    return df.drop_duplicates(subset=dedup_columns, keep="first")
