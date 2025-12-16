import pandas as pd


def validate(df: pd.DataFrame) -> None:
    """
    Validate the final cleaned dataset.
    Raises AssertionError if any validation fails.
    """

    # Structural checks
    assert df.shape[0] > 0, "Dataset is empty"
    assert df.shape[1] >= 15, "Unexpected number of columns"

    # Missing values check
    assert df.isnull().sum().sum() == 0, "Missing values remain in dataset"

    # Type checks
    assert pd.api.types.is_numeric_dtype(df["age"]), "Age must be numeric"
    assert pd.api.types.is_numeric_dtype(df["education_num"]), "Education_num must be numeric"
    assert pd.api.types.is_numeric_dtype(df["hours_per_week"]), "Hours_per_week must be numeric"

    # Domain constraints
    assert (df["age"] >= 0).all() and (df["age"] <= 120).all(), "Invalid age values"
    assert (df["hours_per_week"] >= 0).all() and (df["hours_per_week"] <= 168).all(), "Invalid hours_per_week"

    # Target integrity
    assert df["income"].nunique() == 2, "Unexpected target classes"

    # If all assertions pass, data is valid
    return None
