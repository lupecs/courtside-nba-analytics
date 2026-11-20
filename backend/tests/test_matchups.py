
import pandas as pd
import pytest

from courtside.matchups import build_matchup_dataset, build_matchup_features


def make_game_logs():
    """Create two team-game records for one completed game."""
    return pd.DataFrame(
        [
            {
                "GAME_ID": "001",
                "GAME_DATE": "2024-10-22",
                "SEASON": "2024-25",
                "TEAM_ID": 1,
                "TEAM_NAME": "Los Angeles Lakers",
                "MATCHUP": "LAL vs. MIN",
                "WL": "W",
                "PTS": 110,
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "001",
                "GAME_DATE": "2024-10-22",
                "SEASON": "2024-25",
                "TEAM_ID": 2,
                "TEAM_NAME": "Minnesota Timberwolves",
                "MATCHUP": "MIN @ LAL",
                "WL": "L",
                "PTS": 103,
                "GAME_STATUS": "COMPLETED",
            },
        ]
    )


def test_build_matchup_dataset_creates_one_row_per_game():
    result = build_matchup_dataset(make_game_logs())

    assert len(result) == 1
    assert result.iloc[0]["GAME_ID"] == "001"
    assert result.iloc[0]["HOME_TEAM"] == "Los Angeles Lakers"
    assert result.iloc[0]["AWAY_TEAM"] == "Minnesota Timberwolves"


def test_build_matchup_dataset_identifies_scores_and_winner():
    result = build_matchup_dataset(make_game_logs())

    matchup = result.iloc[0]

    assert matchup["HOME_PTS"] == 110
    assert matchup["AWAY_PTS"] == 103
    assert matchup["HOME_WIN"] == 1
    assert matchup["WINNER_TEAM"] == "Los Angeles Lakers"
    assert matchup["WINNER_TEAM_ID"] == 1


def test_build_matchup_dataset_excludes_unplayed_games():
    df = make_game_logs()

    unplayed = make_game_logs()
    unplayed["GAME_ID"] = "002"
    unplayed["GAME_STATUS"] = "UNPLAYED"
    unplayed["WL"] = pd.NA
    unplayed["PTS"] = 0

    df = pd.concat([df, unplayed], ignore_index=True)

    result = build_matchup_dataset(df)

    assert len(result) == 1
    assert result.iloc[0]["GAME_ID"] == "001"


def test_build_matchup_dataset_rejects_missing_columns():
    df = make_game_logs().drop(columns=["MATCHUP"])

    with pytest.raises(ValueError, match="Missing required columns"):
        build_matchup_dataset(df)


def test_build_matchup_dataset_rejects_duplicate_records():
    df = make_game_logs()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate game/team records"):
        build_matchup_dataset(df)


def test_build_matchup_dataset_rejects_missing_outcomes():
    df = make_game_logs()
    df.loc[0, "WL"] = pd.NA

    with pytest.raises(ValueError, match="missing values"):
        build_matchup_dataset(df)


def test_build_matchup_dataset_rejects_invalid_team_counts():
    df = make_game_logs().iloc[[0]].copy()

    with pytest.raises(ValueError, match="Invalid team-game records"):
        build_matchup_dataset(df)

def test_build_matchup_features_attaches_home_and_away_features():
    team_games = pd.DataFrame(
        {
            "GAME_ID": ["001", "001", "002", "002"],
            "GAME_DATE": [
                "2020-01-01",
                "2020-01-01",
                "2020-01-02",
                "2020-01-02",
            ],
            "TEAM_ID": [1, 2, 1, 2],
            "WL": ["W", "L", "L", "W"],
            "PTS": [100, 90, 95, 105],
            "GAME_STATUS": ["COMPLETED"] * 4,
        }
    )

    matchups = pd.DataFrame(
        {
            "GAME_ID": ["001", "002"],
            "HOME_TEAM_ID": [1, 2],
            "AWAY_TEAM_ID": [2, 1],
            "IS_NEUTRAL": [False, False],
        }
    )

    result = build_matchup_features(
        team_games,
        matchups,
        windows=(1,),
    )

    assert len(result) == 2

    first_game = result.loc[result["GAME_ID"] == "001"].iloc[0]
    second_game = result.loc[result["GAME_ID"] == "002"].iloc[0]

    assert pd.isna(first_game["HOME_PRIOR_WIN_PCT"])
    assert pd.isna(first_game["AWAY_PRIOR_WIN_PCT"])

    assert second_game["HOME_PRIOR_WIN_PCT"] == 0
    assert second_game["AWAY_PRIOR_WIN_PCT"] == 1

    assert second_game["HOME_LAST_1_PTS_FOR"] == 90
    assert second_game["AWAY_LAST_1_PTS_FOR"] == 100

def test_build_matchup_features_preserves_neutral_games():
    team_games = pd.DataFrame(
        {
            "GAME_ID": ["001", "001", "002", "002"],
            "GAME_DATE": [
                "2020-01-01",
                "2020-01-01",
                "2020-01-02",
                "2020-01-02",
            ],
            "TEAM_ID": [1, 2, 1, 2],
            "WL": ["W", "L", "L", "W"],
            "PTS": [100, 90, 95, 105],
            "GAME_STATUS": ["COMPLETED"] * 4,
        }
    )

    matchups = pd.DataFrame(
        {
            "GAME_ID": ["002"],
            "HOME_TEAM_ID": [pd.NA],
            "AWAY_TEAM_ID": [pd.NA],
            "IS_NEUTRAL": [True],
        }
    )

    result = build_matchup_features(
        team_games,
        matchups,
        windows=(1,),
    )

    assert len(result) == 1
    assert result.iloc[0]["IS_NEUTRAL"]

    assert pd.isna(result.iloc[0]["HOME_PRIOR_WIN_PCT"])
    assert pd.isna(result.iloc[0]["AWAY_PRIOR_WIN_PCT"])