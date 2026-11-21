import pytest
from fastapi.testclient import TestClient

import courtside.api as api_module
from courtside.api import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def use_original_test_seasons(monkeypatch):
    """Limit API tests to the four baseline seasons."""
    test_seasons = [
        "1946-47",
        "1979-80",
        "1996-97",
        "2025-26",
    ]

    test_data = api_module.nba_data[
        api_module.nba_data["SEASON"].isin(test_seasons)
    ].copy()

    monkeypatch.setattr(api_module, "nba_data", test_data)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_available_seasons():
    response = client.get("/seasons")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 4
    assert data["seasons"] == [
        "1946-47",
        "1979-80",
        "1996-97",
        "2025-26",
    ]


def test_get_season_summaries():
    response = client.get("/seasons/summary")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 4
    assert data[0]["SEASON"] == "1946-47"
    assert data[0]["TOTAL_GAMES"] == 331
    assert data[0]["TEAM_COUNT"] == 11


def test_get_team_performance():
    response = client.get("/seasons/1946-47/teams")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 11
    assert data[0]["SEASON"] == "1946-47"
    assert "WIN_PCT" in data[0]
    assert "POINT_DIFF" in data[0]


def test_compare_seasons():
    response = client.get(
        "/seasons/compare",
        params={
            "season_a": "1946-47",
            "season_b": "2025-26",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5
    assert data[0]["SEASON_A"] == "1946-47"
    assert data[0]["SEASON_B"] == "2025-26"
    assert "DIFFERENCE" in data[0]
    assert "PCT_CHANGE" in data[0]


def test_get_era_adjusted_team_performance():
    response = client.get("/seasons/2025-26/teams/era-adjusted")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 30
    assert data[0]["SEASON"] == "2025-26"
    assert "PTS_INDEX" in data[0]
    assert "DEF_INDEX" in data[0]
    assert "ERA_STRENGTH" in data[0]


def test_get_team_performance_invalid_season():
    response = client.get("/seasons/2030-31/teams")

    assert response.status_code == 404
    assert "season" in response.json()["detail"].lower()

def test_get_model_performance(monkeypatch):
    """Return performance metrics for all predictive models."""

    expected = {
        "train_games": 100,
        "test_games": 20,
        "test_start_season": "2021-22",
        "baseline_metrics": {"accuracy": 0.55},
        "models": {
            "Logistic Regression": {"metrics": {"accuracy": 0.62}},
            "Random Forest": {"metrics": {"accuracy": 0.63}},
            "Gradient Boosting": {"metrics": {"accuracy": 0.60}},
        },
    }

    monkeypatch.setattr(
        api_module,
        "get_predictive_results",
        lambda: expected,
    )

    response = client.get("/models/performance")

    assert response.status_code == 200

    data = response.json()

    assert data["train_games"] == 100
    assert data["test_games"] == 20
    assert data["baseline"]["accuracy"] == 0.55
    assert len(data["models"]) == 3


def test_get_model_calibration(monkeypatch):
    """Return calibration tables for all predictive models."""

    import pandas as pd

    expected = {
        "baseline_calibration": pd.DataFrame(
            [
                {
                    "bin": "(0.9, 1.0]",
                    "games": 20,
                    "mean_predicted_probability": 1.0,
                    "actual_home_win_rate": 0.55,
                }
            ]
        ),
        "models": {
            name: {
                "calibration": pd.DataFrame(
                    [
                        {
                            "bin": "(0.5, 0.6]",
                            "games": 10,
                            "mean_predicted_probability": 0.55,
                            "actual_home_win_rate": 0.50,
                        }
                    ]
                )
            }
            for name in [
                "Logistic Regression",
                "Random Forest",
                "Gradient Boosting",
            ]
        },
    }

    monkeypatch.setattr(
        api_module,
        "get_predictive_results",
        lambda: expected,
    )

    response = client.get("/models/calibration")

    assert response.status_code == 200

    data = response.json()

    assert len(data["baseline"]) == 1
    assert len(data["models"]) == 3
    assert data["models"]["Random Forest"][0]["games"] == 10

def test_get_model_feature_importance(monkeypatch):
    """Return feature importance for all predictive models."""

    import pandas as pd

    expected = {
        name: pd.DataFrame(
            [
                {
                    "feature": "HOME_LAST_10_PTS_FOR",
                    "importance_mean": 0.03,
                    "importance_std": 0.005,
                }
            ]
        )
        for name in [
            "Logistic Regression",
            "Random Forest",
            "Gradient Boosting",
        ]
    }

    monkeypatch.setattr(
        api_module,
        "get_feature_importance",
        lambda: expected,
    )

    response = client.get("/models/feature-importance")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data["Logistic Regression"][0]["feature"] == (
        "HOME_LAST_10_PTS_FOR"
    )

def test_get_historical_predictions(monkeypatch):
    """Return paginated historical predictions."""

    expected = {
        "model": "Logistic Regression",
        "season": "2024-25",
        "total": 100,
        "limit": 10,
        "offset": 0,
        "predictions": [
            {
                "GAME_ID": "001",
                "SEASON": "2024-25",
                "HOME_TEAM": "Boston Celtics",
                "AWAY_TEAM": "New York Knicks",
                "ACTUAL_HOME_WIN": 1,
                "PREDICTED_HOME_WIN": 1,
                "HOME_WIN_PROBABILITY": 0.72,
            }
        ],
    }

    monkeypatch.setattr(
        api_module,
        "get_historical_predictions",
        lambda **kwargs: expected,
    )

    response = client.get(
        "/predictions/historical",
        params={
            "model": "Logistic Regression",
            "season": "2024-25",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 100
    assert data["limit"] == 10
    assert len(data["predictions"]) == 1


def test_get_historical_predictions_invalid_model(monkeypatch):
    """Return a client error for an unknown model."""

    def raise_error(**kwargs):
        raise ValueError("Unknown model: Invalid Model")

    monkeypatch.setattr(
        api_module,
        "get_historical_predictions",
        raise_error,
    )

    response = client.get(
        "/predictions/historical",
        params={"model": "Invalid Model"},
    )

    assert response.status_code == 400
    assert "Unknown model" in response.json()["detail"]


def test_create_matchup_prediction(monkeypatch):
    expected = {
        "home_team": "Boston Celtics",
        "away_team": "New York Knicks",
        "model": "Logistic Regression",
        "predicted_winner": "Boston Celtics",
        "predicted_home_win": 1,
        "home_win_probability": 0.72,
        "away_win_probability": 0.28,
    }

    monkeypatch.setattr(
        api_module,
        "predict_matchup",
        lambda **kwargs: expected,
    )

    features = {
        column: 0.5 for column in api_module.FEATURE_COLUMNS
    }

    response = client.post(
        "/predictions",
        json={
            "home_team": "Boston Celtics",
            "away_team": "New York Knicks",
            "model": "Logistic Regression",
            "features": features,
        },
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_create_matchup_prediction_rejects_missing_features(monkeypatch):
    response = client.post(
        "/predictions",
        json={
            "home_team": "Boston Celtics",
            "away_team": "New York Knicks",
            "model": "Logistic Regression",
            "features": {},
        },
    )

    assert response.status_code == 400
    assert "Missing required features" in response.json()["detail"]


def test_create_matchup_prediction_rejects_unknown_model(monkeypatch):
    def raise_unknown_model(**kwargs):
        raise ValueError("Unknown model: Invalid Model")

    monkeypatch.setattr(
        api_module,
        "predict_matchup",
        raise_unknown_model,
    )

    features = {
        column: 0.5 for column in api_module.FEATURE_COLUMNS
    }

    response = client.post(
        "/predictions",
        json={
            "home_team": "Boston Celtics",
            "away_team": "New York Knicks",
            "model": "Invalid Model",
            "features": features,
        },
    )

    assert response.status_code == 400
    assert "Unknown model" in response.json()["detail"]
