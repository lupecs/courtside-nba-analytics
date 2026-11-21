import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from courtside.modeling import calculate_feature_importance


def test_calculate_feature_importance():
    """Return sorted permutation importance for model features."""

    X = pd.DataFrame(
        {
            "strong_feature": [0, 0, 0, 1, 1, 1, 0, 1],
            "weak_feature": [1, 0, 1, 0, 1, 0, 1, 0],
        }
    )
    y = pd.Series([0, 0, 0, 1, 1, 1, 0, 1])

    model = LogisticRegression(random_state=42)
    model.fit(X, y)

    result = calculate_feature_importance(
        model,
        X,
        y,
        n_repeats=3,
    )

    assert list(result.columns) == [
        "feature",
        "importance_mean",
        "importance_std",
    ]
    assert len(result) == 2
    assert result["importance_mean"].is_monotonic_decreasing


def test_calculate_feature_importance_invalid_repeats():
    """Reject invalid permutation repeat counts."""

    with pytest.raises(ValueError, match="at least 1"):
        calculate_feature_importance(
            None,
            pd.DataFrame(),
            pd.Series(dtype=int),
            n_repeats=0,
        )
