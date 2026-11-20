"""Download and validate historical NBA team game logs."""

from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

CORE_COLUMNS = {
    "GAME_ID",
    "TEAM_ID",
    "TEAM_NAME",
    "GAME_DATE",
    "MATCHUP",
    "WL",
    "PTS",
}

OPTIONAL_STAT_COLUMNS = {
    "MIN",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PLUS_MINUS",
}


def validate_game_logs(
    df: pd.DataFrame,
    season: str,
) -> pd.DataFrame:
    """Validate game logs while preserving unavailable historical statistics."""

    if df.empty:
        raise ValueError(f"No game records returned for {season}.")

    missing = CORE_COLUMNS.difference(df.columns)

    if missing:
        raise ValueError(f"Missing essential columns for {season}: {sorted(missing)}")

    df = df.copy()

    for column in OPTIONAL_STAT_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    df["GAME_DATE"] = pd.to_datetime(
        df["GAME_DATE"],
        errors="raise",
    )

    df["SEASON"] = season

    if not df["SEASON"].eq(season).all():
        raise ValueError(f"Unexpected season values found for {season}.")

    if df["GAME_ID"].isna().any():
        raise ValueError("Null game IDs found.")

    if df["TEAM_ID"].isna().any():
        raise ValueError("Null team IDs found.")

    if df["PTS"].isna().any():
        raise ValueError("Missing point totals found.")

    if df.duplicated(["GAME_ID", "TEAM_ID"]).any():
        raise ValueError("Duplicate game/team records found.")

    df["GAME_STATUS"] = "COMPLETED"

    for game_id, game_rows in df.groupby("GAME_ID", sort=False):
        if game_rows["WL"].isin(["W", "L"]).all():
            continue

        is_unplayed = (
            len(game_rows) == 2
            and game_rows["TEAM_ID"].nunique() == 2
            and game_rows["GAME_DATE"].nunique() == 1
            and game_rows["WL"].isna().all()
            and pd.to_numeric(
                game_rows["PTS"], errors="coerce"
            ).eq(0).all()
            and pd.to_numeric(
                game_rows["MIN"], errors="coerce"
            ).eq(0).all()
        )

        if not is_unplayed:
            raise ValueError("Unexpected game outcome values.")

        df.loc[game_rows.index, "GAME_STATUS"] = "UNPLAYED"

    return df.sort_values(["GAME_DATE", "GAME_ID", "TEAM_ID"]).reset_index(drop=True)


def fetch_season(season: str = "2024-25") -> pd.DataFrame:
    """Fetch one NBA regular season of team-level game logs."""

    response = leaguegamelog.LeagueGameLog(
        counter=0,
        direction="ASC",
        league_id="00",
        player_or_team_abbreviation="T",
        season=season,
        season_type_all_star="Regular Season",
        sorter="DATE",
        timeout=60,
    )

    df = response.get_data_frames()[0]

    return validate_game_logs(df, season)


def save_raw_data(df: pd.DataFrame, season: str) -> Path:
    """Save validated source data safely without feature transformations."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / f"nba_team_game_logs_{season}.csv"
    temp_path = output_path.with_suffix(".csv.tmp")

    try:
        df.to_csv(temp_path, index=False)
        temp_path.replace(output_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return output_path


def main() -> None:
    season = "2024-25"

    print(f"Fetching NBA {season} regular-season data...")

    df = fetch_season(season)
    output_path = save_raw_data(df, season)

    print("\nData successfully downloaded!")
    print(f"Records: {len(df):,}")
    print(f"Games: {df['GAME_ID'].nunique():,}")
    print(f"Teams: {df['TEAM_ID'].nunique():,}")
    print(f"Date range: {df['GAME_DATE'].min()} to {df['GAME_DATE'].max()}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
