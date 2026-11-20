import pandas as pd
import pytest

from courtside.ingest import (
    CORE_COLUMNS,
    OPTIONAL_STAT_COLUMNS,
    validate_game_logs,
)


def make_game_log():
    """Create a minimal valid NBA game log."""
    return pd.DataFrame(
        [
            {
                "GAME_ID": "0010000001",
                "TEAM_ID": 1610612747,
                "TEAM_NAME": "Los Angeles Lakers",
                "GAME_DATE": "2024-10-22",
                "MATCHUP": "LAL vs. MIN",
                "WL": "W",
                "PTS": 110,
            }
        ]
    )

def make_unplayed_game_log():
    """Create a two-team game log for a canceled, unplayed game."""
    return pd.DataFrame(
        [
            {
                "GAME_ID": "0021201214",
                "TEAM_ID": 1610612738,
                "TEAM_NAME": "Boston Celtics",
                "GAME_DATE": "2013-04-16",
                "MATCHUP": "BOS vs. IND",
                "WL": pd.NA,
                "PTS": 0,
                "MIN": 0,
            },
            {
                "GAME_ID": "0021201214",
                "TEAM_ID": 1610612754,
                "TEAM_NAME": "Indiana Pacers",
                "GAME_DATE": "2013-04-16",
                "MATCHUP": "IND @ BOS",
                "WL": pd.NA,
                "PTS": 0,
                "MIN": 0,
            },
        ]
    )

def test_validator_preserves_missing_historical_statistics():
    df = make_game_log()

    result = validate_game_logs(df, "1946-47")

    assert len(result) == 1
    assert result.loc[0, "SEASON"] == "1946-47"
    assert result.loc[0, "PTS"] == 110

    # Missing statistics must remain missing, not become zero.
    assert pd.isna(result.loc[0, "FG3M"])
    assert pd.isna(result.loc[0, "AST"])


def test_validator_accepts_complete_modern_statistics():
    df = make_game_log()

    for column in OPTIONAL_STAT_COLUMNS:
        df[column] = 0

    result = validate_game_logs(df, "2024-25")

    assert len(result) == 1
    assert result.loc[0, "SEASON"] == "2024-25"
    assert result.loc[0, "FG3M"] == 0
    assert result.loc[0, "AST"] == 0


def test_validator_rejects_missing_core_columns():
    df = make_game_log().drop(columns=["PTS"])

    with pytest.raises(ValueError, match="PTS"):
        validate_game_logs(df, "2024-25")


def test_validator_rejects_duplicate_game_team_records():
    df = pd.concat(
        [make_game_log(), make_game_log()],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="Duplicate"):
        validate_game_logs(df, "2024-25")


def test_validator_adds_optional_columns_missing_from_source():
    df = make_game_log()

    result = validate_game_logs(df, "1946-47")

    for column in OPTIONAL_STAT_COLUMNS:
        assert column in result.columns


def test_validator_rejects_empty_data():
    df = pd.DataFrame(columns=list(CORE_COLUMNS))

    with pytest.raises(ValueError, match="No game records"):
        validate_game_logs(df, "2024-25")

def test_save_raw_data_creates_csv(tmp_path, monkeypatch):
    from courtside import ingest

    monkeypatch.setattr(ingest, "RAW_DATA_DIR", tmp_path)

    df = make_game_log()
    output_path = ingest.save_raw_data(df, "2024-25")

    assert output_path.exists()
    assert output_path.name == "nba_team_game_logs_2024-25.csv"

    saved_df = pd.read_csv(output_path)
    assert len(saved_df) == 1
    assert saved_df.loc[0, "PTS"] == 110

    assert not output_path.with_suffix(".csv.tmp").exists()


def test_save_raw_data_preserves_existing_file_on_write_failure(
    tmp_path,
    monkeypatch,
):
    from courtside import ingest

    monkeypatch.setattr(ingest, "RAW_DATA_DIR", tmp_path)

    output_path = tmp_path / "nba_team_game_logs_2024-25.csv"
    output_path.write_text("existing data", encoding="utf-8")

    def fail_to_csv(self, *args, **kwargs):
        raise OSError("Simulated disk error")

    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_to_csv)

    with pytest.raises(OSError, match="Simulated disk error"):
        ingest.save_raw_data(make_game_log(), "2024-25")

    assert output_path.read_text(encoding="utf-8") == "existing data"
    assert not output_path.with_suffix(".csv.tmp").exists()

def test_validator_marks_completed_games():
    result = validate_game_logs(make_game_log(), "2024-25")

    assert result["GAME_STATUS"].eq("COMPLETED").all()


def test_validator_accepts_unplayed_game():
    result = validate_game_logs(make_unplayed_game_log(), "2012-13")

    assert len(result) == 2
    assert result["GAME_STATUS"].eq("UNPLAYED").all()
    assert result["WL"].isna().all()


def test_validator_rejects_unexpected_missing_outcome():
    df = make_game_log()
    df.loc[0, "WL"] = pd.NA

    with pytest.raises(ValueError, match="Unexpected game outcome values"):
        validate_game_logs(df, "2024-25")