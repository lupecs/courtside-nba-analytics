
import numpy as np
import pandas as pd
import pytest

from courtside.modeling import (
    FEATURE_COLUMNS,
    calculate_calibration_table,
    calculate_classification_metrics,
    compare_classification_models,
    prepare_modeling_data,
    train_logistic_regression,
)


@pytest.fixture
def sample_matchup_data():
    rng = np.random.default_rng(42)
    rows = []

    seasons = ["2019-20", "2020-21", "2021-22", "2022-23"]

    for season_index, season in enumerate(seasons):
        for game_index in range(20):
            home_win = game_index % 2

            row = {
                "GAME_ID": season_index * 100 + game_index,
                "SEASON": season,
                "IS_NEUTRAL": False,
                "HOME_WIN": home_win,
            }

            for feature in FEATURE_COLUMNS:
                row[feature] = rng.normal(0.5, 0.1)

            rows.append(row)

    # Include neutral-site games to verify their exclusion.
    neutral_row = rows[-1].copy()
    neutral_row["GAME_ID"] = 999
    neutral_row["SEASON"] = "2022-23"
    neutral_row["IS_NEUTRAL"] = True
    rows.append(neutral_row)

    return pd.DataFrame(rows)


def test_prepare_modeling_data_uses_chronological_split(
    sample_matchup_data,
):
    X_train, y_train, X_test, y_test = prepare_modeling_data(
        sample_matchup_data
    )

    assert len(X_train) == 40
    assert len(X_test) == 40
    assert len(y_train) == 40
    assert len(y_test) == 40

    assert set(y_train.unique()) == {0, 1}
    assert set(y_test.unique()) == {0, 1}


def test_prepare_modeling_data_excludes_neutral_games(
    sample_matchup_data,
):
    X_train, _, X_test, _ = prepare_modeling_data(
        sample_matchup_data
    )

    assert len(X_train) + len(X_test) == 80


def test_prepare_modeling_data_handles_missing_features(
    sample_matchup_data,
):
    data = sample_matchup_data.copy()
    data.loc[0, "HOME_PRIOR_WIN_PCT"] = np.nan
    data.loc[60, "AWAY_LAST_5_PTS_FOR"] = np.nan

    X_train, _, X_test, _ = prepare_modeling_data(data)

    assert X_train["HOME_PRIOR_WIN_PCT"].isna().sum() == 1
    assert X_test["AWAY_LAST_5_PTS_FOR"].isna().sum() == 1


def test_calculate_classification_metrics_returns_expected_values():
    y_true = pd.Series([1, 1, 0, 0])
    y_pred = pd.Series([1, 0, 0, 1])
    y_probability = pd.Series([0.9, 0.4, 0.2, 0.8])

    metrics = calculate_classification_metrics(
        y_true,
        y_pred,
        y_probability,
    )

    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5
    assert metrics["roc_auc"] == 0.75
    assert metrics["confusion_matrix"] == [
        [1, 1],
        [1, 1],
    ]

def test_calculate_calibration_table_returns_expected_values():
    y_true = pd.Series([1, 1, 0, 0, 1, 0])
    y_probability = pd.Series([0.1, 0.2, 0.3, 0.4, 0.8, 0.9])

    calibration = calculate_calibration_table(
        y_true,
        y_probability,
        n_bins=5,
    )

    assert list(calibration.columns) == [
        "bin",
        "games",
        "mean_predicted_probability",
        "actual_home_win_rate",
    ]

    assert calibration["games"].sum() == 6
    assert len(calibration) == 4

    assert calibration["games"].tolist() == [2, 2, 1, 1]

    assert calibration["mean_predicted_probability"].tolist() == [
        pytest.approx(0.15),
        pytest.approx(0.35),
        pytest.approx(0.8),
        pytest.approx(0.9),
    ]

    assert calibration["actual_home_win_rate"].tolist() == [
        pytest.approx(1.0),
        pytest.approx(0.0),
        pytest.approx(1.0),
        pytest.approx(0.0),
    ]


def test_calculate_calibration_table_rejects_invalid_bin_count():
    y_true = pd.Series([1, 0])
    y_probability = pd.Series([0.8, 0.2])

    with pytest.raises(ValueError, match="n_bins"):
        calculate_calibration_table(
            y_true,
            y_probability,
            n_bins=0,
        )


def test_calculate_calibration_table_rejects_mismatched_lengths():
    y_true = pd.Series([1, 0])
    y_probability = pd.Series([0.8])

    with pytest.raises(ValueError, match="same length"):
        calculate_calibration_table(y_true, y_probability)


def test_train_logistic_regression_returns_model_and_predictions(
    sample_matchup_data,
):
    results = train_logistic_regression(sample_matchup_data)

    assert results["model_name"] == "Logistic Regression"
    assert results["train_games"] == 40
    assert results["test_games"] == 40

    assert results["metrics"]["accuracy"] >= 0
    assert results["metrics"]["accuracy"] <= 1
    assert results["metrics"]["roc_auc"] >= 0
    assert results["metrics"]["roc_auc"] <= 1

    assert len(results["predictions"]) == 40
    assert "ACTUAL_HOME_WIN" in results["predictions"]
    assert "PREDICTED_HOME_WIN" in results["predictions"]
    assert "HOME_WIN_PROBABILITY" in results["predictions"]

    assert len(results["features"]) == len(FEATURE_COLUMNS)


def test_model_and_baseline_use_same_test_games(sample_matchup_data):
    results = train_logistic_regression(sample_matchup_data)

    assert results["test_games"] == len(results["predictions"])
    assert results["baseline_metrics"]["accuracy"] >= 0
    assert results["baseline_metrics"]["accuracy"] <= 1

def test_compare_classification_models_evaluates_all_models(
    sample_matchup_data,
):
    results = compare_classification_models(sample_matchup_data)

    assert results["train_games"] == 40
    assert results["test_games"] == 40

    assert set(results["models"]) == {
        "Logistic Regression",
        "Random Forest",
        "Gradient Boosting",
    }

    for model_results in results["models"].values():
        assert 0 <= model_results["metrics"]["accuracy"] <= 1
        assert 0 <= model_results["metrics"]["roc_auc"] <= 1
        assert len(model_results["predictions"]) == 40
