"""Utilities for engineering pre-game NBA prediction features."""

import pandas as pd


def calculate_rolling_team_performance(
    df: pd.DataFrame,
    windows: tuple[int, ...] = (5, 10),
) -> pd.DataFrame:
    """Calculate rolling team performance using previous games only."""
    required_columns = {
        "GAME_ID",
        "GAME_DATE",
        "TEAM_ID",
        "WL",
        "PTS",
        "GAME_STATUS",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if not windows or any(window < 1 for window in windows):
        raise ValueError("Rolling windows must be positive integers.")

    game_df = df.copy()

    game_df = game_df.loc[
        game_df["GAME_STATUS"] == "COMPLETED"
    ].copy()

    game_df["GAME_DATE"] = pd.to_datetime(game_df["GAME_DATE"])

    game_df = game_df.sort_values(
        ["TEAM_ID", "GAME_DATE", "GAME_ID"]
    )

    game_df["WIN"] = (game_df["WL"] == "W").astype(int)

    game_df["PTS_ALLOWED"] = (
    game_df.groupby("GAME_ID")["PTS"].transform("sum")
    - game_df["PTS"]
)

    game_df.groupby("TEAM_ID", sort=False)

    for window in windows:
        for column, feature in [
            ("PTS", "PTS_FOR"),
            ("WIN", "WIN_PCT"),
            ("PTS_ALLOWED", "PTS_ALLOWED"),
        ]:
            rolling_values = (
                game_df.groupby("TEAM_ID", sort=False)[column]
                .transform(
                    lambda values, window=window: (
                        values.shift(1)
                        .rolling(window, min_periods=window)
                        .mean()
                    )
                )
            )

            game_df[f"LAST_{window}_{feature}"] = rolling_values

        date_groups = game_df.groupby(
            ["TEAM_ID", "GAME_DATE"]
        )

        for feature in [
            "PTS_FOR",
            "WIN_PCT",
            "PTS_ALLOWED",
        ]:
            column = f"LAST_{window}_{feature}"

            game_df[column] = date_groups[column].transform("first")

    return game_df

def calculate_prior_win_percentage(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate each team's win percentage before every game."""
    required_columns = {
        "GAME_ID",
        "GAME_DATE",
        "TEAM_ID",
        "WL",
        "GAME_STATUS",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    game_df = df.copy()

    game_df = game_df.loc[
        game_df["GAME_STATUS"] == "COMPLETED"
    ].copy()

    game_df["GAME_DATE"] = pd.to_datetime(game_df["GAME_DATE"])

    game_df = game_df.sort_values(
        ["TEAM_ID", "GAME_DATE", "GAME_ID"]
    )

    game_df["WIN"] = (game_df["WL"] == "W").astype(int)

    team_groups = game_df.groupby("TEAM_ID", sort=False)

    game_df["PRIOR_GAMES"] = (
        team_groups.cumcount()
    )

    game_df["PRIOR_WINS"] = (
        team_groups["WIN"].cumsum() - game_df["WIN"]
    )

    game_df["PRIOR_GAMES"] = (
        game_df.groupby(["TEAM_ID", "GAME_DATE"])["PRIOR_GAMES"]
        .transform("first")
    )

    game_df["PRIOR_WINS"] = (
        game_df.groupby(["TEAM_ID", "GAME_DATE"])["PRIOR_WINS"]
        .transform("first")
    )

    game_df["PRIOR_WIN_PCT"] = (
        game_df["PRIOR_WINS"]
        / game_df["PRIOR_GAMES"].replace(0, pd.NA)
    )

    return game_df