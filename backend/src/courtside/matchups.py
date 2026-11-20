
"""Utilities for preparing game-level NBA matchup data."""

import pandas as pd

from courtside.features import (
    calculate_prior_win_percentage,
    calculate_rolling_team_performance,
)


def build_matchup_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Convert team-game records into one row per completed game."""

    required_columns = {
        "GAME_ID",
        "GAME_DATE",
        "SEASON",
        "TEAM_ID",
        "TEAM_NAME",
        "MATCHUP",
        "WL",
        "PTS",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    game_df = df.copy()

    if "GAME_STATUS" in game_df.columns:
        game_df = game_df.loc[game_df["GAME_STATUS"] == "COMPLETED"].copy()

    if game_df.empty:
        raise ValueError("No completed games available.")

    if game_df[list(required_columns)].isna().any().any():
        raise ValueError("Required game data contains missing values.")

    if game_df.duplicated(["GAME_ID", "TEAM_ID"]).any():
        raise ValueError("Duplicate game/team records found.")

    if not game_df["WL"].isin(["W", "L"]).all():
        raise ValueError("Unexpected game outcome values.")

    game_df["IS_HOME"] = game_df["MATCHUP"].str.contains(
        " vs. ",
        regex=False,
    )

    game_df["IS_AWAY"] = game_df["MATCHUP"].str.contains(
        " @ ",
        regex=False,
    )

    if not (game_df["IS_HOME"] ^ game_df["IS_AWAY"]).all():
        raise ValueError("Unable to determine home/away team from MATCHUP.")

    games_per_game = game_df.groupby("GAME_ID").agg(
        TEAM_COUNT=("TEAM_ID", "nunique"),
        HOME_COUNT=("IS_HOME", "sum"),
        AWAY_COUNT=("IS_AWAY", "sum"),
        RESULT_COUNT=("WL", "nunique"),
        DATE_COUNT=("GAME_DATE", "nunique"),
        SEASON_COUNT=("SEASON", "nunique"),
    )

    standard_games = (
        games_per_game["HOME_COUNT"].eq(1)
        & games_per_game["AWAY_COUNT"].eq(1)
    )

    neutral_games = (
        games_per_game["HOME_COUNT"].eq(0)
        & games_per_game["AWAY_COUNT"].eq(2)
    )

    valid_games = (
        games_per_game["TEAM_COUNT"].eq(2)
        & (standard_games | neutral_games)
        & games_per_game["RESULT_COUNT"].eq(2)
        & games_per_game["DATE_COUNT"].eq(1)
        & games_per_game["SEASON_COUNT"].eq(1)
    )

    if not valid_games.all():
        raise ValueError("Invalid team-game records found.")

    neutral_game_ids = games_per_game.loc[
        neutral_games
    ].index

    game_df["IS_NEUTRAL"] = game_df["GAME_ID"].isin(neutral_game_ids)

    standard_df = game_df.loc[~game_df["IS_NEUTRAL"]].copy()

    home = standard_df.loc[standard_df["IS_HOME"]].copy()
    away = standard_df.loc[standard_df["IS_AWAY"]].copy()

    home = home.rename(
        columns={
            "TEAM_ID": "HOME_TEAM_ID",
            "TEAM_NAME": "HOME_TEAM",
            "PTS": "HOME_PTS",
            "WL": "HOME_RESULT",
        }
    )

    away = away.rename(
        columns={
            "TEAM_ID": "AWAY_TEAM_ID",
            "TEAM_NAME": "AWAY_TEAM",
            "PTS": "AWAY_PTS",
            "WL": "AWAY_RESULT",
        }
    )

    standard_matchups = home[
        ["GAME_ID", "GAME_DATE", "SEASON", "HOME_TEAM_ID",
        "HOME_TEAM", "HOME_PTS", "HOME_RESULT"]
    ].merge(
        away[
            ["GAME_ID", "AWAY_TEAM_ID", "AWAY_TEAM",
            "AWAY_PTS", "AWAY_RESULT"]
        ],
        on="GAME_ID",
        how="inner",
        validate="one_to_one",
    )

    standard_matchups["IS_NEUTRAL"] = False
    standard_matchups["HOME_WIN"] = (
        standard_matchups["HOME_RESULT"] == "W"
    ).astype(int)

    standard_matchups["WINNER_TEAM_ID"] = standard_matchups.apply(
        lambda row: (
            row["HOME_TEAM_ID"] if row["HOME_WIN"] else row["AWAY_TEAM_ID"]
        ),
        axis=1,
    )

    standard_matchups["WINNER_TEAM"] = standard_matchups.apply(
        lambda row: (
            row["HOME_TEAM"] if row["HOME_WIN"] else row["AWAY_TEAM"]
        ),
        axis=1,
    )

    neutral_df = game_df.loc[game_df["IS_NEUTRAL"]].copy()
    neutral_df = neutral_df.sort_values(["GAME_ID", "TEAM_ID"])
    neutral_df["TEAM_SLOT"] = neutral_df.groupby("GAME_ID").cumcount()

    team_1 = neutral_df[neutral_df["TEAM_SLOT"] == 0].set_index("GAME_ID")
    neutral_df[neutral_df["TEAM_SLOT"] == 1].set_index("GAME_ID")
    neutral_winners = neutral_df[neutral_df["WL"] == "W"].set_index("GAME_ID")

    neutral_matchups = pd.DataFrame(index=team_1.index)

    neutral_matchups["GAME_DATE"] = team_1["GAME_DATE"]
    neutral_matchups["SEASON"] = team_1["SEASON"]
    neutral_matchups["IS_NEUTRAL"] = True

    for column in [
        "HOME_TEAM_ID", "HOME_TEAM", "HOME_PTS", "HOME_RESULT",
        "AWAY_TEAM_ID", "AWAY_TEAM", "AWAY_PTS", "AWAY_RESULT",
    ]:
        neutral_matchups[column] = pd.NA

    neutral_matchups["HOME_WIN"] = pd.NA
    neutral_matchups["WINNER_TEAM_ID"] = neutral_winners["TEAM_ID"]
    neutral_matchups["WINNER_TEAM"] = neutral_winners["TEAM_NAME"]

    neutral_matchups = neutral_matchups.reset_index()

    matchups = pd.concat(
        [standard_matchups, neutral_matchups],
        ignore_index=True,
    )

    return matchups.sort_values(
        ["GAME_DATE", "GAME_ID"]
    ).reset_index(drop=True)


def build_matchup_features(
    team_game_df: pd.DataFrame,
    matchup_df: pd.DataFrame,
    windows: tuple[int, ...] = (5, 10),
) -> pd.DataFrame:
    """Attach pre-game team performance features to each matchup."""

    prior_features = calculate_prior_win_percentage(team_game_df)

    rolling_features = calculate_rolling_team_performance(
        team_game_df,
        windows=windows,
    )

    feature_columns = [
        "GAME_ID",
        "TEAM_ID",
        "PRIOR_GAMES",
        "PRIOR_WINS",
        "PRIOR_WIN_PCT",
    ]

    for window in windows:
        feature_columns.extend(
            [
                f"LAST_{window}_PTS_FOR",
                f"LAST_{window}_PTS_ALLOWED",
                f"LAST_{window}_WIN_PCT",
            ]
        )

    team_features = prior_features[
        ["GAME_ID", "TEAM_ID", "PRIOR_GAMES", "PRIOR_WINS", "PRIOR_WIN_PCT"]
    ].merge(
        rolling_features[
            [
                "GAME_ID",
                "TEAM_ID",
                *[
                    column
                    for column in feature_columns
                    if column.startswith("LAST_")
                ],
            ]
        ],
        on=["GAME_ID", "TEAM_ID"],
        how="inner",
        validate="one_to_one",
    )

    home_features = team_features.rename(
        columns={
            "TEAM_ID": "HOME_TEAM_ID",
            **{
                column: f"HOME_{column}"
                for column in feature_columns
                if column not in {"GAME_ID", "TEAM_ID"}
            },
        }
    )

    away_features = team_features.rename(
        columns={
            "TEAM_ID": "AWAY_TEAM_ID",
            **{
                column: f"AWAY_{column}"
                for column in feature_columns
                if column not in {"GAME_ID", "TEAM_ID"}
            },
        }
    )

    result = matchup_df.copy()

    result["HOME_TEAM_ID"] = pd.to_numeric(
        result["HOME_TEAM_ID"],
        errors="coerce",
    ).astype("Int64")

    result["AWAY_TEAM_ID"] = pd.to_numeric(
        result["AWAY_TEAM_ID"],
        errors="coerce",
    ).astype("Int64")

    home_features["HOME_TEAM_ID"] = (
        home_features["HOME_TEAM_ID"].astype("Int64")
    )

    away_features["AWAY_TEAM_ID"] = (
        away_features["AWAY_TEAM_ID"].astype("Int64")
    )

    result = result.merge(
        home_features,
        on=["GAME_ID", "HOME_TEAM_ID"],
        how="left",
        validate="one_to_one",
    )

    result = result.merge(
        away_features,
        on=["GAME_ID", "AWAY_TEAM_ID"],
        how="left",
        validate="one_to_one",
    )

    return result