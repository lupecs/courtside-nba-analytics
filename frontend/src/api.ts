const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export interface AvailableSeasonsResponse {
  count: number;
  seasons: string[];
}

export interface SeasonSummary {
  SEASON: string;
  TOTAL_GAMES: number;
  TEAM_COUNT: number;
  AVG_GAME_PTS: number;
  AVG_TEAM_PTS: number;
  HIGHEST_SCORING_TEAM: string;
  BEST_TEAM: string;
  BEST_TEAM_WIN_PCT: number;
  BEST_TEAM_POINT_DIFF: number;
}

export interface TeamPerformance {
  TEAM_ID: number;
  TEAM_NAME: string;
  GP: number;
  W: number;
  L: number;
  PTS: number;
  PTS_ALLOWED: number;
  WIN_PCT: number;
  POINT_DIFF: number;
  SEASON: string;
}

export interface SeasonComparison {
  METRIC: string;
  SEASON_A: string;
  VALUE_A: number;
  SEASON_B: string;
  VALUE_B: number;
  DIFFERENCE: number;
  PCT_CHANGE: number | null;
}

export interface EraAdjustedTeamPerformance extends TeamPerformance {
  LEAGUE_AVG_PTS: number;
  PTS_INDEX: number;
  PTS_ABOVE_LEAGUE_AVG: number;
  LEAGUE_AVG_PTS_ALLOWED: number;
  DEF_INDEX: number;
  PTS_PREVENTED_ABOVE_LEAGUE_AVG: number;
  ERA_STRENGTH: number;
}

async function apiGet<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json() as Promise<T>;
}

export function getAvailableSeasons() {
  return apiGet<AvailableSeasonsResponse>("/seasons");
}

export function getSeasonSummaries() {
  return apiGet<SeasonSummary[]>("/seasons/summary");
}

export function getTeamPerformance(season: string) {
  return apiGet<TeamPerformance[]>(`/seasons/${season}/teams`);
}

export function compareSeasons(seasonA: string, seasonB: string) {
  return apiGet<SeasonComparison[]>(
    `/seasons/compare?season_a=${encodeURIComponent(seasonA)}&season_b=${encodeURIComponent(seasonB)}`,
  );
}

export function getEraAdjustedTeamPerformance(season: string) {
  return apiGet<EraAdjustedTeamPerformance[]>(
    `/seasons/${encodeURIComponent(season)}/teams/era-adjusted`,
  );
}

export type PredictiveModelName =
  | "Logistic Regression"
  | "Random Forest"
  | "Gradient Boosting";

export interface ClassificationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  brier_score: number;
  log_loss: number;
  confusion_matrix: number[][];
}

export interface ModelPerformanceResponse {
  train_games: number;
  test_games: number;
  test_start_season: string;
  baseline: ClassificationMetrics;
  models: Record<PredictiveModelName, ClassificationMetrics>;
}

export interface CalibrationBin {
  bin: string;
  games: number;
  mean_predicted_probability: number;
  actual_home_win_rate: number;
}

export interface ModelCalibrationResponse {
  baseline: CalibrationBin[];
  models: Record<PredictiveModelName, CalibrationBin[]>;
}

export interface FeatureImportance {
  feature: string;
  importance_mean: number;
  importance_std: number;
}

export type FeatureImportanceResponse = Record<
  PredictiveModelName,
  FeatureImportance[]
>;

export interface HistoricalPrediction {
  GAME_ID: number;
  GAME_DATE: string;
  SEASON: string;
  HOME_TEAM: string;
  AWAY_TEAM: string;
  HOME_PTS: number;
  AWAY_PTS: number;
  ACTUAL_HOME_WIN: number;
  PREDICTED_HOME_WIN: number;
  HOME_WIN_PROBABILITY: number;
}

export interface HistoricalPredictionsResponse {
  model: PredictiveModelName;
  season: string | null;
  total: number;
  limit: number;
  offset: number;
  predictions: HistoricalPrediction[];
}

export function getModelPerformance() {
  return apiGet<ModelPerformanceResponse>("/models/performance");
}

export function getModelCalibration() {
  return apiGet<ModelCalibrationResponse>("/models/calibration");
}

export function getFeatureImportance() {
  return apiGet<FeatureImportanceResponse>("/models/feature-importance");
}

export function getHistoricalPredictions(
  model: PredictiveModelName = "Logistic Regression",
  season?: string,
  limit = 25,
  offset = 0,
) {
  const params = new URLSearchParams({
    model,
    limit: String(limit),
    offset: String(offset),
  });

  if (season) {
    params.set("season", season);
  }

  return apiGet<HistoricalPredictionsResponse>(
    `/predictions/historical?${params.toString()}`,
  );
}
