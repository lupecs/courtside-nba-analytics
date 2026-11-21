import pandas as pd
import pytest

import courtside.predictive_service as service


def test_get_predictive_results_caches_training(monkeypatch):
    """Train once and reuse the cached results."""

    service.get_predictive_results.cache_clear()

    calls = {"count": 0}
    expected = {"models": {"Logistic Regression": {}}}

    def fake_load_matchup_features():
        return "test dataset"

    def fake_compare_classification_models(df):
        calls["count"] += 1
        assert df == "test dataset"
        return expected

    monkeypatch.setattr(
        service,
        "load_matchup_features",
        fake_load_matchup_features,
    )
    monkeypatch.setattr(
        service,
        "compare_classification_models",
        fake_compare_classification_models,
    )

    first_result = service.get_predictive_results()
    second_result = service.get_predictive_results()

    assert first_result is expected
    assert second_result is expected
    assert calls["count"] == 1

    service.get_predictive_results.cache_clear()



def test_get_historical_predictions_filters_and_paginates(monkeypatch):
    df = pd.DataFrame(
        {
            "GAME_ID": ["001", "002", "003"],
            "GAME_DATE": ["2024-10-22", "2024-10-23", "2025-10-21"],
            "SEASON": ["2024-25", "2024-25", "2025-26"],
            "HOME_TEAM": ["Boston Celtics", "New York Knicks", "Denver Nuggets"],
            "AWAY_TEAM": ["New York Knicks", "Boston Celtics", "Los Angeles Lakers"],
            "HOME_PTS": [110, 105, 115],
            "AWAY_PTS": [100, 108, 109],
        },
        index=[10, 11, 12],
    )

    predictions = pd.DataFrame(
        {
            "ACTUAL_HOME_WIN": [1, 0, 1],
            "PREDICTED_HOME_WIN": [1, 0, 1],
            "HOME_WIN_PROBABILITY": [0.72, 0.38, 0.81],
        },
        index=[10, 11, 12],
    )

    monkeypatch.setattr(
        service,
        "get_predictive_results",
        lambda: {
            "models": {
                "Logistic Regression": {
                    "predictions": predictions,
                }
            }
        },
    )
    monkeypatch.setattr(service, "load_matchup_features", lambda: df)

    result = service.get_historical_predictions(
        model_name="Logistic Regression",
        season="2024-25",
        limit=1,
        offset=1,
    )

    assert result["total"] == 2
    assert result["limit"] == 1
    assert result["offset"] == 1
    assert len(result["predictions"]) == 1
    assert result["predictions"][0]["GAME_ID"] == "002"
    assert result["predictions"][0]["GAME_DATE"] == "2024-10-23"
    assert result["predictions"][0]["HOME_WIN_PROBABILITY"] == 0.38


def test_get_historical_predictions_rejects_unknown_model(monkeypatch):
    monkeypatch.setattr(
        service,
        "get_predictive_results",
        lambda: {"models": {}},
    )

    with pytest.raises(ValueError, match="Unknown model"):
        service.get_historical_predictions("Invalid Model")


@pytest.mark.parametrize(
    ("limit", "offset", "message"),
    [
        (0, 0, "Limit must be between 1 and 500"),
        (501, 0, "Limit must be between 1 and 500"),
        (10, -1, "Offset cannot be negative"),
    ],
)
def test_get_historical_predictions_rejects_invalid_pagination(
    monkeypatch, limit, offset, message
):
    monkeypatch.setattr(
        service,
        "get_predictive_results",
        lambda: {"models": {"Logistic Regression": {}}},
    )

    with pytest.raises(ValueError, match=message):
        service.get_historical_predictions(
            model_name="Logistic Regression",
            limit=limit,
            offset=offset,
        )


def test_predict_matchup_returns_home_and_away_probabilities(monkeypatch):
    from sklearn.dummy import DummyClassifier

    from courtside.modeling import FEATURE_COLUMNS

    feature_columns = list(FEATURE_COLUMNS)

    training_data = pd.DataFrame(
        [[0.5] * len(feature_columns), [0.5] * len(feature_columns)],
        columns=feature_columns,
    )

    model = DummyClassifier(strategy="prior")
    model.fit(training_data, [0, 1])

    monkeypatch.setattr(
        service,
        "get_predictive_results",
        lambda: {
            "models": {
                "Logistic Regression": {
                    "model": model,
                }
            }
        },
    )

    features = {column: 0.5 for column in feature_columns}

    result = service.predict_matchup(
        home_team="Boston Celtics",
        away_team="New York Knicks",
        model_name="Logistic Regression",
        features=features,
    )

    assert result["home_team"] == "Boston Celtics"
    assert result["away_team"] == "New York Knicks"
    assert result["model"] == "Logistic Regression"
    assert result["predicted_winner"] in [
        "Boston Celtics",
        "New York Knicks",
    ]
    assert 0 <= result["home_win_probability"] <= 1
    assert 0 <= result["away_win_probability"] <= 1
    assert (
        result["home_win_probability"]
        + result["away_win_probability"]
    ) == pytest.approx(1.0)


def test_predict_matchup_rejects_unknown_model(monkeypatch):
    monkeypatch.setattr(
        service,
        "get_predictive_results",
        lambda: {"models": {}},
    )

    with pytest.raises(ValueError, match="Unknown model"):
        service.predict_matchup(
            home_team="Boston Celtics",
            away_team="New York Knicks",
            model_name="Invalid Model",
            features={},
        )


def test_predict_matchup_rejects_missing_features(monkeypatch):
    monkeypatch.setattr(
        service,
        "get_predictive_results",
        lambda: {
            "models": {
                "Logistic Regression": {
                    "model": None,
                }
            }
        },
    )

    with pytest.raises(ValueError, match="Missing required features"):
        service.predict_matchup(
            home_team="Boston Celtics",
            away_team="New York Knicks",
            model_name="Logistic Regression",
            features={},
        )
