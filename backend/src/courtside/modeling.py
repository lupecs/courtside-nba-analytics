
from __future__ import annotations

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "HOME_PRIOR_WIN_PCT",
    "HOME_LAST_5_PTS_FOR",
    "HOME_LAST_5_PTS_ALLOWED",
    "HOME_LAST_5_WIN_PCT",
    "HOME_LAST_10_PTS_FOR",
    "HOME_LAST_10_PTS_ALLOWED",
    "HOME_LAST_10_WIN_PCT",
    "AWAY_PRIOR_WIN_PCT",
    "AWAY_LAST_5_PTS_FOR",
    "AWAY_LAST_5_PTS_ALLOWED",
    "AWAY_LAST_5_WIN_PCT",
    "AWAY_LAST_10_PTS_FOR",
    "AWAY_LAST_10_PTS_ALLOWED",
    "AWAY_LAST_10_WIN_PCT",
]

TARGET_COLUMN = "HOME_WIN"
DEFAULT_TEST_START_SEASON = "2021-22"


def prepare_modeling_data(
    df: pd.DataFrame,
    test_start_season: str = DEFAULT_TEST_START_SEASON,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Prepare chronological training and testing datasets."""

    required_columns = [
        "SEASON",
        "IS_NEUTRAL",
        TARGET_COLUMN,
        *FEATURE_COLUMNS,
    ]

    missing_columns = sorted(set(required_columns) - set(df.columns))
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df.loc[~df["IS_NEUTRAL"]].copy()

    data[TARGET_COLUMN] = pd.to_numeric(
        data[TARGET_COLUMN],
        errors="coerce",
    )

    if data[TARGET_COLUMN].isna().any():
        raise ValueError("Target column contains missing values.")

    if not data[TARGET_COLUMN].isin([0, 1]).all():
        raise ValueError("Target column must contain only 0 and 1.")

    data["SEASON"] = data["SEASON"].astype(str)

    train = data[data["SEASON"] < test_start_season].copy()
    test = data[data["SEASON"] >= test_start_season].copy()

    if train.empty or test.empty:
        raise ValueError(
            "Chronological split produced an empty training or testing set."
        )

    X_train = (
        train[FEATURE_COLUMNS]
        .apply(pd.to_numeric, errors="coerce")
        .astype("float64")
    )
    y_train = train[TARGET_COLUMN].astype(int)

    X_test = (
        test[FEATURE_COLUMNS]
        .apply(pd.to_numeric, errors="coerce")
        .astype("float64")
    )
    y_test = test[TARGET_COLUMN].astype(int)

    return X_train, y_train, X_test, y_test


def create_logistic_regression_pipeline() -> Pipeline:
    """Create a preprocessing and logistic regression pipeline."""

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )

def create_random_forest_pipeline() -> Pipeline:
    """Create a preprocessing and random forest pipeline."""

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=12,
                    min_samples_leaf=5,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def create_gradient_boosting_pipeline() -> Pipeline:
    """Create a preprocessing and gradient boosting pipeline."""

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                GradientBoostingClassifier(
                    n_estimators=150,
                    learning_rate=0.05,
                    max_depth=2,
                    min_samples_leaf=5,
                    random_state=42,
                ),
            ),
        ]
    )


def calculate_classification_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
    y_probability: pd.Series,
) -> dict:
    """Calculate classification and probability metrics."""

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(
            precision_score(y_true, y_pred, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, y_pred, zero_division=0)
        ),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_probability)),
        "brier_score": float(
            brier_score_loss(y_true, y_probability)
        ),
        "log_loss": float(log_loss(y_true, y_probability)),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
        ).tolist(),
    }

def calculate_calibration_table(
    y_true: pd.Series,
    y_probability: pd.Series,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Group predicted probabilities into bins and compare them with outcomes."""

    if n_bins < 1:
        raise ValueError("n_bins must be at least 1.")

    if len(y_true) != len(y_probability):
        raise ValueError(
            "y_true and y_probability must have the same length."
        )

    if y_true.empty:
        raise ValueError("Calibration data cannot be empty.")

    if y_true.isna().any() or y_probability.isna().any():
        raise ValueError("Calibration data cannot contain missing values.")

    if not y_probability.between(0, 1).all():
        raise ValueError("Predicted probabilities must be between 0 and 1.")

    bins = pd.cut(
        y_probability,
        bins=[i / n_bins for i in range(n_bins + 1)],
        include_lowest=True,
    )

    calibration_df = pd.DataFrame(
        {
            "bin": bins,
            "y_true": y_true,
            "y_probability": y_probability,
        }
    )

    calibration_table = (
        calibration_df.groupby("bin", observed=False)
        .agg(
            games=("y_true", "count"),
            mean_predicted_probability=("y_probability", "mean"),
            actual_home_win_rate=("y_true", "mean"),
        )
        .reset_index()
    )

    calibration_table = calibration_table.dropna(
        subset=["mean_predicted_probability"]
    )

    calibration_table["bin"] = calibration_table["bin"].astype(str)

    return calibration_table.reset_index(drop=True)

def evaluate_model(
    model: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Train a model and evaluate its predictions."""

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = calculate_classification_metrics(
        y_test,
        predictions,
        probabilities,
    )

    prediction_results = pd.DataFrame(
        {
            "ACTUAL_HOME_WIN": y_test,
            "PREDICTED_HOME_WIN": predictions,
            "HOME_WIN_PROBABILITY": probabilities,
        },
        index=y_test.index,
    )

    return {
        "model": model,
        "metrics": metrics,
        "calibration": calculate_calibration_table(
            y_test,
            prediction_results["HOME_WIN_PROBABILITY"],
        ),
        "predictions": prediction_results,
    }


def train_logistic_regression(
    df: pd.DataFrame,
    test_start_season: str = DEFAULT_TEST_START_SEASON,
) -> dict:
    """Train and evaluate logistic regression against a home-win baseline."""

    X_train, y_train, X_test, y_test = prepare_modeling_data(
        df,
        test_start_season=test_start_season,
    )

    training_seasons = (
        df.loc[~df["IS_NEUTRAL"], "SEASON"]
        .astype(str)
    )
    training_seasons = training_seasons[
        training_seasons < test_start_season
    ]

    train_start_season = training_seasons.min()
    train_end_season = training_seasons.max()

    model = create_logistic_regression_pipeline()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    model_metrics = calculate_classification_metrics(
        y_test,
        predictions,
        probabilities,
    )

    baseline_predictions = pd.Series(
        1,
        index=y_test.index,
    )

    baseline_metrics = calculate_classification_metrics(
        y_test,
        baseline_predictions,
        baseline_predictions,
    )

    prediction_results = pd.DataFrame(
        {
            "ACTUAL_HOME_WIN": y_test,
            "PREDICTED_HOME_WIN": predictions,
            "HOME_WIN_PROBABILITY": probabilities,
        },
        index=y_test.index,
    )

    return {
        "model": model,
        "model_name": "Logistic Regression",
        "train_games": len(X_train),
        "test_games": len(X_test),
        "train_start_season": train_start_season,
        "train_end_season": train_end_season,
        "test_start_season": test_start_season,
        "features": FEATURE_COLUMNS.copy(),
        "metrics": model_metrics,
        "calibration": calculate_calibration_table(
            y_test,
            prediction_results["HOME_WIN_PROBABILITY"],
        ),
        "baseline_metrics": baseline_metrics,
        "baseline_calibration": calculate_calibration_table(
            y_test,
            baseline_predictions,
        ),
        "predictions": prediction_results,
    }

def compare_classification_models(
    df: pd.DataFrame,
    test_start_season: str = DEFAULT_TEST_START_SEASON,
) -> dict:
    """Train and compare three classification models."""

    X_train, y_train, X_test, y_test = prepare_modeling_data(
        df,
        test_start_season=test_start_season,
    )

    models = {
        "Logistic Regression": create_logistic_regression_pipeline(),
        "Random Forest": create_random_forest_pipeline(),
        "Gradient Boosting": create_gradient_boosting_pipeline(),
    }

    results = {}

    for name, model in models.items():
        print(f"Training {name}...")

        results[name] = evaluate_model(
            model,
            X_train,
            y_train,
            X_test,
            y_test,
        )

    baseline_predictions = pd.Series(
        1,
        index=y_test.index,
    )

    baseline_metrics = calculate_classification_metrics(
        y_test,
        baseline_predictions,
        baseline_predictions,
    )

    return {
        "train_games": len(X_train),
        "test_games": len(X_test),
        "test_start_season": test_start_season,
        "baseline_metrics": baseline_metrics,
        "baseline_calibration": calculate_calibration_table(
            y_test,
            baseline_predictions,
        ),
        "models": results,
    }