import pandas as pd
import pytest

from courtside.modeling import FEATURE_COLUMNS, TARGET_COLUMN
from courtside.predictive_data import load_matchup_features


def create_valid_dataset() -> pd.DataFrame:
    """Create a minimal valid matchup feature dataset."""

    data = {
        "SEASON": ["2024-25"],
        "IS_NEUTRAL": [False],
        TARGET_COLUMN: [1],
    }

    data.update({column: [0.5] for column in FEATURE_COLUMNS})

    return pd.DataFrame(data)


def test_load_matchup_features(tmp_path):
    """Load a valid matchup feature dataset."""

    path = tmp_path / "features.csv"
    expected = create_valid_dataset()
    expected.to_csv(path, index=False)

    result = load_matchup_features(path)

    assert len(result) == 1
    assert list(result.columns) == list(expected.columns)


def test_load_matchup_features_missing_file(tmp_path):
    """Raise an error when the dataset does not exist."""

    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="not found"):
        load_matchup_features(path)


def test_load_matchup_features_empty_file(tmp_path):
    """Reject an empty dataset."""

    path = tmp_path / "empty.csv"
    pd.DataFrame().to_csv(path, index=False)

    with pytest.raises(ValueError, match="empty"):
        load_matchup_features(path)


def test_load_matchup_features_missing_columns(tmp_path):
    """Reject a dataset missing required modeling columns."""

    path = tmp_path / "incomplete.csv"
    pd.DataFrame({"SEASON": ["2024-25"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing columns"):
        load_matchup_features(path)
