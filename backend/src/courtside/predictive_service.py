from functools import lru_cache

import pandas as pd

from courtside.modeling import (
    FEATURE_COLUMNS,
    calculate_feature_importance,
    compare_classification_models,
    prepare_modeling_data,
)
from courtside.predictive_data import load_matchup_features


@lru_cache(maxsize=1)
def get_predictive_results() -> dict:
    """Load the matchup dataset and train predictive models once."""

    df = load_matchup_features()

    return compare_classification_models(df)


@lru_cache(maxsize=1)
def get_feature_importance() -> dict:
    """Calculate and cache feature importance for all models."""

    df = load_matchup_features()
    results = get_predictive_results()

    _X_train, _y_train, X_test, y_test = prepare_modeling_data(
        df,
        test_start_season=results["test_start_season"],
    )

    return {
        name: calculate_feature_importance(
            result["model"],
            X_test,
            y_test,
        )
        for name, result in results["models"].items()
    }

def get_historical_predictions(
    model_name: str,
    season: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Return paginated historical predictions for a selected model."""

    results = get_predictive_results()

    if model_name not in results["models"]:
        raise ValueError(f"Unknown model: {model_name}")

    if limit < 1 or limit > 500:
        raise ValueError("Limit must be between 1 and 500.")

    if offset < 0:
        raise ValueError("Offset cannot be negative.")

    df = load_matchup_features()

    predictions = results["models"][model_name]["predictions"]

    historical = df.loc[
        predictions.index,
        [
            "GAME_ID",
            "GAME_DATE",
            "SEASON",
            "HOME_TEAM",
            "AWAY_TEAM",
            "HOME_PTS",
            "AWAY_PTS",
        ],
    ].join(predictions)

    if season is not None:
        historical = historical[
            historical["SEASON"].astype(str) == season
        ]

    total = len(historical)

    page = historical.iloc[offset : offset + limit].copy()

    page["GAME_DATE"] = pd.to_datetime(
        page["GAME_DATE"]
    ).dt.strftime("%Y-%m-%d")

    return {
        "model": model_name,
        "season": season,
        "total": total,
        "limit": limit,
        "offset": offset,
        "predictions": page.to_dict(orient="records"),
    }


def predict_matchup(
    home_team: str,
    away_team: str,
    model_name: str,
    features: dict[str, float | None],
) -> dict:
    """Predict the home team's win probability for an upcoming matchup."""

    results = get_predictive_results()

    if model_name not in results["models"]:
        raise ValueError(f"Unknown model: {model_name}")

    expected_features = list(FEATURE_COLUMNS)

    missing = set(expected_features) - set(features)
    unexpected = set(features) - set(expected_features)

    if missing:
        raise ValueError(f"Missing required features: {sorted(missing)}")

    if unexpected:
        raise ValueError(f"Unexpected features: {sorted(unexpected)}")

    feature_values = pd.DataFrame(
        [[features[column] for column in expected_features]],
        columns=expected_features,
    )

    model = results["models"][model_name]["model"]

    probability = float(model.predict_proba(feature_values)[0][1])
    predicted_home_win = int(probability >= 0.5)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "model": model_name,
        "predicted_winner": home_team if predicted_home_win else away_team,
        "predicted_home_win": predicted_home_win,
        "home_win_probability": probability,
        "away_win_probability": 1.0 - probability,
    }
