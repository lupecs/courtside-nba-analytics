"""FastAPI application for the Courtside analytics platform."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from courtside.analytics import (
    calculate_era_adjusted_team_performance,
    calculate_season_summary,
    calculate_team_performance,
    compare_seasons,
)
from courtside.historical import load_historical_data
from courtside.modeling import FEATURE_COLUMNS
from courtside.predictive_service import (
    get_feature_importance,
    get_historical_predictions,
    get_predictive_results,
    predict_matchup,
)


class MatchupPredictionRequest(BaseModel):
    """Validated input for predicting an upcoming NBA matchup."""

    home_team: str = Field(min_length=1)
    away_team: str = Field(min_length=1)
    model: str = "Logistic Regression"
    is_neutral: bool = False
    features: dict[str, float | None] = Field(
        description="The 14 pregame features required by the prediction model."
    )

    def validate_features(self) -> None:
        """Ensure the request contains exactly the model's expected features."""
        missing = set(FEATURE_COLUMNS) - set(self.features)
        unexpected = set(self.features) - set(FEATURE_COLUMNS)

        if missing:
            raise ValueError(
                f"Missing required features: {sorted(missing)}"
            )

        if unexpected:
            raise ValueError(
                f"Unexpected features: {sorted(unexpected)}"
            )


app = FastAPI(
    title="Courtside NBA Analytics API",
    description="Historical NBA analytics and team performance.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://courtside-nba-analytics-lilac.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load historical NBA data when the API starts.
nba_data = load_historical_data()


@app.get("/seasons")
def get_available_seasons():
    """Return all seasons available in the historical dataset."""
    seasons = sorted(nba_data["SEASON"].unique())

    return {
        "count": len(seasons),
        "seasons": seasons,
    }


@app.get("/health")
def health_check():
    """Check whether the API is running."""
    return {"status": "healthy"}


@app.get("/seasons/summary")
def get_season_summaries():
    """Return league-wide summaries for all available seasons."""
    summary = calculate_season_summary(nba_data)

    return summary.to_dict(orient="records")


@app.get("/seasons/{season}/teams")
def get_team_performance(season: str):
    """Return team performance statistics for a selected season."""
    try:
        performance = calculate_team_performance(nba_data, season)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return performance.to_dict(orient="records")


@app.get("/seasons/compare")
def get_season_comparison(season_a: str, season_b: str):
    """Compare league-wide statistics between two NBA seasons."""
    try:
        comparison = compare_seasons(nba_data, season_a, season_b)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return comparison.to_dict(orient="records")


@app.get("/seasons/{season}/teams/era-adjusted")
def get_era_adjusted_team_performance(season: str):
    """Return era-adjusted team performance for a selected season."""
    try:
        performance = calculate_era_adjusted_team_performance(nba_data, season)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return performance.to_dict(orient="records")

@app.get("/models/performance")
def get_model_performance():
    """Return performance metrics for all predictive models."""

    results = get_predictive_results()

    return {
        "train_games": results["train_games"],
        "test_games": results["test_games"],
        "test_start_season": results["test_start_season"],
        "baseline": results["baseline_metrics"],
        "models": {
            name: result["metrics"]
            for name, result in results["models"].items()
        },
    }


@app.get("/models/calibration")
def get_model_calibration():
    """Return calibration tables for all predictive models."""

    results = get_predictive_results()

    return {
        "baseline": results["baseline_calibration"].to_dict(
            orient="records"
        ),
        "models": {
            name: result["calibration"].to_dict(
                orient="records"
            )
            for name, result in results["models"].items()
        },
    }

@app.get("/models/feature-importance")
def get_model_feature_importance():
    """Return permutation feature importance for all models."""

    importance = get_feature_importance()

    return {
        name: result.to_dict(orient="records")
        for name, result in importance.items()
    }

@app.get("/predictions/historical")
def get_historical_prediction_results(
    model: str = "Logistic Regression",
    season: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """Return paginated historical predictions."""

    try:
        return get_historical_predictions(
            model_name=model,
            season=season,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/predictions")
def create_matchup_prediction(request: MatchupPredictionRequest):
    """Predict the outcome of an upcoming NBA matchup."""

    try:
        request.validate_features()

        return predict_matchup(
            home_team=request.home_team,
            away_team=request.away_team,
            model_name=request.model,
            features=request.features,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
