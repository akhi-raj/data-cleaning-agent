import pandas as pd


def detect_outliers_iqr(series: pd.Series) -> pd.Series:
    """
    Detect outliers using the IQR method.

    Parameters:
        series (pd.Series): Numeric column

    Returns:
        pd.Series: Boolean mask where True indicates an outlier
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return (series < lower_bound) | (series > upper_bound)


def add_outlier_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add outlier flag columns for eligible numeric features.

    Parameters:
        df (pd.DataFrame): Cleaned dataframe

    Returns:
        pd.DataFrame: Dataframe with outlier flags added
    """

    outlier_columns = ["age", "education_num", "hours_per_week"]

    for col in outlier_columns:
        df[f"{col}_outlier"] = detect_outliers_iqr(df[col])

    return df