from pathlib import Path

import pandas as pd

from courtside.coverage import PROCESSED_DATA_DIR
from courtside.modeling import FEATURE_COLUMNS, TARGET_COLUMN

MATCHUP_FEATURES_FILE = (
    PROCESSED_DATA_DIR / "nba_historical_matchup_features.csv"
)


def load_matchup_features(
    path: Path = MATCHUP_FEATURES_FILE,
) -> pd.DataFrame:
    """Load and validate the processed historical matchup features."""

    if not path.exists():
        raise FileNotFoundError(
            f"Matchup feature dataset not found: {path}"
        )

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("Matchup feature dataset is empty.") from exc

    if df.empty:
        raise ValueError("Matchup feature dataset is empty.")

    required_columns = [
        "SEASON",
        "IS_NEUTRAL",
        TARGET_COLUMN,
        *FEATURE_COLUMNS,
    ]

    missing_columns = sorted(set(required_columns) - set(df.columns))

    if missing_columns:
        raise ValueError(
            f"Matchup feature dataset is missing columns: "
            f"{missing_columns}"
        )

    return df
