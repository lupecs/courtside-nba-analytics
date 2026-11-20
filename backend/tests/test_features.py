import pandas as pd

from courtside.features import (
    calculate_prior_win_percentage,
    calculate_rolling_team_performance,
)


def test_calculate_prior_win_percentage_uses_only_previous_games():
    df = pd.DataFrame(
        [
            {
                "GAME_ID": "001",
                "GAME_DATE": "2024-10-01",
                "TEAM_ID": 1,
                "WL": "W",
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "002",
                "GAME_DATE": "2024-10-03",
                "TEAM_ID": 1,
                "WL": "L",
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "003",
                "GAME_DATE": "2024-10-05",
                "TEAM_ID": 1,
                "WL": "W",
                "GAME_STATUS": "COMPLETED",
            },
        ]
    )

    result = calculate_prior_win_percentage(df)

    assert result["PRIOR_GAMES"].tolist() == [0, 1, 2]
    assert result["PRIOR_WINS"].tolist() == [0, 1, 1]

    assert pd.isna(result.iloc[0]["PRIOR_WIN_PCT"])
    assert result.iloc[1]["PRIOR_WIN_PCT"] == 1.0
    assert result.iloc[2]["PRIOR_WIN_PCT"] == 0.5


def test_calculate_prior_win_percentage_tracks_teams_independently():
    df = pd.DataFrame(
        [
            {
                "GAME_ID": "001",
                "GAME_DATE": "2024-10-01",
                "TEAM_ID": 1,
                "WL": "W",
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "001",
                "GAME_DATE": "2024-10-01",
                "TEAM_ID": 2,
                "WL": "L",
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "002",
                "GAME_DATE": "2024-10-03",
                "TEAM_ID": 1,
                "WL": "L",
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "002",
                "GAME_DATE": "2024-10-03",
                "TEAM_ID": 2,
                "WL": "W",
                "GAME_STATUS": "COMPLETED",
            },
        ]
    )

    result = calculate_prior_win_percentage(df)

    team_1 = result[result["TEAM_ID"] == 1]
    team_2 = result[result["TEAM_ID"] == 2]

    assert team_1["PRIOR_GAMES"].tolist() == [0, 1]
    assert team_2["PRIOR_GAMES"].tolist() == [0, 1]

    assert team_1.iloc[1]["PRIOR_WIN_PCT"] == 1.0
    assert team_2.iloc[1]["PRIOR_WIN_PCT"] == 0.0


def test_calculate_prior_win_percentage_excludes_unplayed_games():
    df = pd.DataFrame(
        [
            {
                "GAME_ID": "001",
                "GAME_DATE": "2024-10-01",
                "TEAM_ID": 1,
                "WL": "W",
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "002",
                "GAME_DATE": "2024-10-03",
                "TEAM_ID": 1,
                "WL": None,
                "GAME_STATUS": "UNPLAYED",
            },
            {
                "GAME_ID": "003",
                "GAME_DATE": "2024-10-05",
                "TEAM_ID": 1,
                "WL": "L",
                "GAME_STATUS": "COMPLETED",
            },
        ]
    )

    result = calculate_prior_win_percentage(df)

    assert len(result) == 2
    assert result["GAME_ID"].tolist() == ["001", "003"]

    assert result["PRIOR_GAMES"].tolist() == [0, 1]
    assert result["PRIOR_WINS"].tolist() == [0, 1]
    assert result.iloc[1]["PRIOR_WIN_PCT"] == 1.0


def test_calculate_rolling_team_performance_uses_previous_games():
    from courtside.features import calculate_rolling_team_performance

    df = pd.DataFrame(
        [
            {
                "GAME_ID": str(i),
                "GAME_DATE": f"2024-10-{i:02d}",
                "TEAM_ID": 1,
                "WL": "W" if i <= 5 else "L",
                "PTS": i * 10,
                "GAME_STATUS": "COMPLETED",
            }
            for i in range(1, 7)
        ]
    )

    result = calculate_rolling_team_performance(df, windows=(5,))

    assert pd.isna(result.iloc[4]["LAST_5_PTS_FOR"])
    assert pd.isna(result.iloc[4]["LAST_5_WIN_PCT"])

    assert result.iloc[5]["LAST_5_PTS_FOR"] == 30.0
    assert result.iloc[5]["LAST_5_WIN_PCT"] == 1.0

def test_calculate_rolling_team_performance_supports_multiple_windows():
    df = pd.DataFrame(
        [
            {
                "GAME_ID": str(i),
                "GAME_DATE": f"2024-10-{i:02d}",
                "TEAM_ID": 1,
                "WL": "W" if i <= 10 else "L",
                "PTS": i * 10,
                "GAME_STATUS": "COMPLETED",
            }
            for i in range(1, 12)
        ]
    )

    result = calculate_rolling_team_performance(
        df,
        windows=(5, 10),
    )

    # Game 10 has only 9 previous games.
    assert pd.isna(result.iloc[9]["LAST_10_PTS_FOR"])

    # Game 11 has 10 previous games.
    assert result.iloc[10]["LAST_10_PTS_FOR"] == 55.0
    assert result.iloc[10]["LAST_10_WIN_PCT"] == 1.0

    # Its last five games are games 6 through 10.
    assert result.iloc[10]["LAST_5_PTS_FOR"] == 80.0
    assert result.iloc[10]["LAST_5_WIN_PCT"] == 1.0

def test_calculate_rolling_team_performance_calculates_points_allowed():
    df = pd.DataFrame(
        [
            {
                "GAME_ID": str(i),
                "GAME_DATE": f"2024-10-{i:02d}",
                "TEAM_ID": 1,
                "WL": "W",
                "PTS": 100,
                "GAME_STATUS": "COMPLETED",
            }
            for i in range(1, 6)
        ]
        + [
            {
                "GAME_ID": str(i),
                "GAME_DATE": f"2024-10-{i:02d}",
                "TEAM_ID": 2,
                "WL": "L",
                "PTS": 90,
                "GAME_STATUS": "COMPLETED",
            }
            for i in range(1, 6)
        ]
        + [
            {
                "GAME_ID": "6",
                "GAME_DATE": "2024-10-06",
                "TEAM_ID": 1,
                "WL": "W",
                "PTS": 110,
                "GAME_STATUS": "COMPLETED",
            },
            {
                "GAME_ID": "6",
                "GAME_DATE": "2024-10-06",
                "TEAM_ID": 2,
                "WL": "L",
                "PTS": 95,
                "GAME_STATUS": "COMPLETED",
            },
        ]
    )

    result = calculate_rolling_team_performance(df, windows=(5,))

    team_1 = result[result["TEAM_ID"] == 1]
    team_2 = result[result["TEAM_ID"] == 2]

    # Team 1 previously scored 100 and allowed 90 per game.
    assert team_1.iloc[5]["LAST_5_PTS_FOR"] == 100.0
    assert team_1.iloc[5]["LAST_5_PTS_ALLOWED"] == 90.0

    # Team 2 previously scored 90 and allowed 100 per game.
    assert team_2.iloc[5]["LAST_5_PTS_FOR"] == 90.0
    assert team_2.iloc[5]["LAST_5_PTS_ALLOWED"] == 100.0

def test_calculate_rolling_team_performance_excludes_unplayed_games():
    df = pd.DataFrame(
        [
            {
                "GAME_ID": str(i),
                "GAME_DATE": f"2024-10-{i:02d}",
                "TEAM_ID": 1,
                "WL": "W",
                "PTS": 100,
                "GAME_STATUS": "COMPLETED",
            }
            for i in range(1, 6)
        ]
        + [
            {
                "GAME_ID": "6",
                "GAME_DATE": "2024-10-06",
                "TEAM_ID": 1,
                "WL": None,
                "PTS": 0,
                "GAME_STATUS": "UNPLAYED",
            },
            {
                "GAME_ID": "7",
                "GAME_DATE": "2024-10-07",
                "TEAM_ID": 1,
                "WL": "L",
                "PTS": 80,
                "GAME_STATUS": "COMPLETED",
            },
        ]
    )

    result = calculate_rolling_team_performance(df, windows=(5,))

    assert len(result) == 6
    assert "6" not in result["GAME_ID"].tolist()

    last_game = result[result["GAME_ID"] == "7"].iloc[0]

    assert last_game["LAST_5_PTS_FOR"] == 100.0
    assert last_game["LAST_5_WIN_PCT"] == 1.0

def test_doubleheader_games_share_same_pre_game_features():
    df = pd.DataFrame(
        {
            "GAME_ID": ["001", "002", "003", "004"],
            "GAME_DATE": [
                "2020-01-01",
                "2020-01-02",
                "2020-01-02",
                "2020-01-03",
            ],
            "TEAM_ID": [1, 1, 1, 1],
            "WL": ["W", "L", "W", "W"],
            "PTS": [100, 90, 110, 105],
            "GAME_STATUS": ["COMPLETED"] * 4,
        }
    )

    result = calculate_rolling_team_performance(
        df,
        windows=(1,),
    )

    doubleheader = result.loc[
        result["GAME_DATE"] == pd.Timestamp("2020-01-02")
    ]

    assert doubleheader["LAST_1_PTS_FOR"].nunique() == 1
    assert doubleheader["LAST_1_WIN_PCT"].nunique() == 1
    assert doubleheader["LAST_1_PTS_ALLOWED"].nunique() == 1

    assert doubleheader["LAST_1_PTS_FOR"].iloc[0] == 100
    assert doubleheader["LAST_1_WIN_PCT"].iloc[0] == 1