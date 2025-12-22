from .loader import load_data
from .type_coercion import coerce_types
from .missing_values import handle_missing_values
from .outliers import add_outlier_flags
from .deduplication import deduplicate
from .validation import validate


COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week",
    "native_country", "income"
]


def run_pipeline(file_path: str):
    """
    Run the full data cleaning pipeline.

    Parameters:
        file_path (str): Path to raw dataset

    Returns:
        pd.DataFrame: Cleaned and validated dataframe
    """

    # Load
    df = load_data(file_path, COLUMNS)

    # Step 2: Type coercion
    df = coerce_types(df)

    # Step 3: Missing values
    df = handle_missing_values(df)

    # Step 4: Outlier detection (flagging only)
    df = add_outlier_flags(df)

    # Step 5: Deduplication
    df = deduplicate(df)

    # Step 6: Validation
    validate(df)

    return df
