import { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import {
  getAvailableSeasons,
  getModelPerformance,
  getModelCalibration,
  getFeatureImportance,
  getHistoricalPredictions,
  type PredictiveModelName,
  type ModelPerformanceResponse,
  type ModelCalibrationResponse,
  type FeatureImportanceResponse,
  type HistoricalPredictionsResponse,
} from "../api";
import "./PredictiveAnalytics.css";

const modelNames: PredictiveModelName[] = [
  "Logistic Regression",
  "Random Forest",
  "Gradient Boosting",
];

const metricOptions = [
  { label: "Accuracy", value: "accuracy", format: "percent", higher: true },
  { label: "Precision", value: "precision", format: "percent", higher: true },
  { label: "Recall", value: "recall", format: "percent", higher: true },
  { label: "F1 Score", value: "f1", format: "percent", higher: true },
  { label: "ROC-AUC", value: "roc_auc", format: "decimal", higher: true },
  { label: "Brier Score", value: "brier_score", format: "decimal", higher: false },
  { label: "Log Loss", value: "log_loss", format: "decimal", higher: false },
] as const;

type MetricKey = (typeof metricOptions)[number]["value"];

function formatMetric(value: number, format: "percent" | "decimal") {
  return format === "percent"
    ? `${(value * 100).toFixed(1)}%`
    : value.toFixed(3);
}

function PredictiveAnalytics() {
  const [performance, setPerformance] =
    useState<ModelPerformanceResponse | null>(null);
  const [calibration, setCalibration] =
    useState<ModelCalibrationResponse | null>(null);
  const [importance, setImportance] =
    useState<FeatureImportanceResponse | null>(null);
  const [seasons, setSeasons] = useState<string[]>([]);
  const [overviewLoading, setOverviewLoading] = useState(true);
  const [overviewError, setOverviewError] = useState<string | null>(null);

  const [selectedMetric, setSelectedMetric] =
    useState<MetricKey>("roc_auc");
  const [importanceModel, setImportanceModel] =
    useState<PredictiveModelName>("Random Forest");

  const [predictionModel, setPredictionModel] =
    useState<PredictiveModelName>("Logistic Regression");
  const [predictionSeason, setPredictionSeason] = useState("");
  const [predictionPage, setPredictionPage] = useState(0);
  const [predictions, setPredictions] =
    useState<HistoricalPredictionsResponse | null>(null);
  const [predictionsLoading, setPredictionsLoading] = useState(true);
  const [predictionsError, setPredictionsError] = useState<string | null>(null);

  const pageSize = 25;

  useEffect(() => {
    let cancelled = false;

    async function loadAnalytics() {
      try {
        setOverviewLoading(true);
        setOverviewError(null);

        const [modelResults, calibrationResults, featureResults, seasonResults] =
          await Promise.all([
            getModelPerformance(),
            getModelCalibration(),
            getFeatureImportance(),
            getAvailableSeasons(),
          ]);

        if (!cancelled) {
          setPerformance(modelResults);
          setCalibration(calibrationResults);
          setImportance(featureResults);
          setSeasons(seasonResults.seasons);
        }
      } catch (error) {
        if (!cancelled) {
          setOverviewError(
            error instanceof Error
              ? error.message
              : "Unable to load predictive analytics.",
          );
        }
      } finally {
        if (!cancelled) {
          setOverviewLoading(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadPredictions() {
      try {
        setPredictionsLoading(true);
        setPredictionsError(null);

        const result = await getHistoricalPredictions(
          predictionModel,
          predictionSeason || undefined,
          pageSize,
          predictionPage * pageSize,
        );

        if (!cancelled) {
          setPredictions(result);
        }
      } catch (error) {
        if (!cancelled) {
          setPredictionsError(
            error instanceof Error
              ? error.message
              : "Unable to load historical predictions.",
          );
        }
      } finally {
        if (!cancelled) {
          setPredictionsLoading(false);
        }
      }
    }

    loadPredictions();

    return () => {
      cancelled = true;
    };
  }, [predictionModel, predictionSeason, predictionPage]);

  const selectedMetricInfo = metricOptions.find(
    (metric) => metric.value === selectedMetric,
  )!;

  const selectedFeatureImportance = importance?.[importanceModel] ?? [];

  const sortedImportance = [...selectedFeatureImportance]
    .sort((a, b) => b.importance_mean - a.importance_mean)
    .slice(0, 14)
    .reverse();

  const calibrationTraces = modelNames.map((model) => {
    const bins = calibration?.models[model] ?? [];

    return {
      x: bins.map((bin) => bin.mean_predicted_probability),
      y: bins.map((bin) => bin.actual_home_win_rate),
      text: bins.map((bin) => `${bin.games.toLocaleString()} games`),
      type: "scatter" as const,
      mode: "lines+markers" as const,
      name: model,
      line: { width: 2.5 },
      marker: { size: 8 },
      hovertemplate:
        "Predicted: %{x:.1%}<br>Actual: %{y:.1%}<br>%{text}<extra>%{fullData.name}</extra>",
    };
  });

  return (
    <div className="predictive-page">
      {overviewError && (
        <div className="predictive-error" role="alert">
          Unable to load model analytics: {overviewError}
        </div>
      )}

      <section className="predictive-intro">
        <div>
          <p className="eyebrow">MACHINE LEARNING</p>
          <h2>Can we predict the outcome?</h2>
          <p>
            Evaluate three classification models trained on historical NBA
            games. Explore predictive performance, probability calibration,
            feature importance, and individual game predictions.
          </p>
        </div>
        <div className="predictive-intro-mark">ML</div>
      </section>

      <section className="predictive-stat-grid">
        <div className="stat-card">
          <span className="stat-label">TRAINING GAMES</span>
          <strong>
            {overviewLoading
              ? "—"
              : performance?.train_games.toLocaleString("en-US") ?? "—"}
          </strong>
          <small>Games used to fit the models</small>
        </div>
        <div className="stat-card">
          <span className="stat-label">TEST GAMES</span>
          <strong>
            {overviewLoading
              ? "—"
              : performance?.test_games.toLocaleString("en-US") ?? "—"}
          </strong>
          <small>Games used for evaluation</small>
        </div>
        <div className="stat-card">
          <span className="stat-label">TEST PERIOD START</span>
          <strong className="predictive-season-value">
            {overviewLoading ? "—" : performance?.test_start_season ?? "—"}
          </strong>
          <small>Beginning of the evaluation period</small>
        </div>
      </section>

      <section className="panel predictive-panel">
        <div className="panel-heading performance-heading">
          <div>
            <p className="eyebrow">MODEL EVALUATION</p>
            <h2>Compare Model Performance</h2>
            <p className="predictive-description">
              Select a metric to compare the three models on the same test set.
            </p>
          </div>
          <div className="season-select-control">
            <label htmlFor="predictive-metric">METRIC</label>
            <select
              id="predictive-metric"
              value={selectedMetric}
              onChange={(event) =>
                setSelectedMetric(event.target.value as MetricKey)
              }
            >
              {metricOptions.map((metric) => (
                <option key={metric.value} value={metric.value}>
                  {metric.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {overviewLoading ? (
          <div className="empty-state">Loading model performance...</div>
        ) : performance ? (
          <>
            <div className="model-metric-grid">
              {modelNames.map((model) => {
                const score = performance.models[model][selectedMetric];
                return (
                  <div className="model-metric-card" key={model}>
                    <span>{model}</span>
                    <strong>
                      {formatMetric(score, selectedMetricInfo.format)}
                    </strong>
                    <small>
                      {selectedMetricInfo.higher
                        ? "Higher is better"
                        : "Lower is better"}
                    </small>
                  </div>
                );
              })}
            </div>

            <Plot
              data={[
                {
                  type: "bar",
                  x: modelNames,
                  y: modelNames.map(
                    (model) => performance.models[model][selectedMetric],
                  ),
                  marker: { color: "#f0a45b" },
                  text: modelNames.map((model) =>
                    formatMetric(
                      performance.models[model][selectedMetric],
                      selectedMetricInfo.format,
                    ),
                  ),
                  textposition: "outside",
                  cliponaxis: false,
                  hovertemplate: "%{x}<br>%{y:.4f}<extra></extra>",
                },
              ]}
              layout={{
                autosize: true,
                height: 330,
                margin: { l: 55, r: 25, t: 30, b: 65 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { color: "#dce3ed", family: "DM Sans, sans-serif" },
                xaxis: { gridcolor: "rgba(255,255,255,0.06)" },
                yaxis: {
                  title: { text: selectedMetricInfo.label },
                  gridcolor: "rgba(255,255,255,0.08)",
                  rangemode: "tozero",
                },
                showlegend: false,
              }}
              config={{ responsive: true, displayModeBar: false }}
              useResizeHandler
              style={{ width: "100%", height: "330px" }}
            />

            <div className="predictive-note">
              <strong>How to read this:</strong> Accuracy, precision, recall,
              F1, and ROC-AUC are better when higher. Brier score and log loss
              measure probability error, so lower is better. The baseline
              predicts a home win for every game.
            </div>
          </>
        ) : (
          <div className="empty-state">No model performance data available.</div>
        )}
      </section>

      <section className="panel predictive-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">PROBABILITY QUALITY</p>
            <h2>Model Calibration</h2>
            <p className="predictive-description">
              Compare predicted home-win probabilities with the actual home-win
              rate for games in each probability range.
            </p>
          </div>
        </div>

        {overviewLoading ? (
          <div className="empty-state">Loading calibration data...</div>
        ) : calibration ? (
          <>
            <Plot
              data={[
                {
                  type: "scatter",
                  mode: "lines",
                  x: [0, 1],
                  y: [0, 1],
                  name: "Perfect calibration",
                  line: { color: "#aebbd0", dash: "dash", width: 1.5 },
                  hoverinfo: "skip",
                },
                ...calibrationTraces,
              ]}
              layout={{
                autosize: true,
                height: 390,
                margin: { l: 65, r: 25, t: 25, b: 65 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { color: "#dce3ed", family: "DM Sans, sans-serif" },
                xaxis: {
                  title: { text: "Mean predicted home-win probability" },
                  range: [0, 1],
                  tickformat: ".0%",
                  gridcolor: "rgba(255,255,255,0.08)",
                },
                yaxis: {
                  title: { text: "Actual home-win rate" },
                  range: [0, 1],
                  tickformat: ".0%",
                  gridcolor: "rgba(255,255,255,0.08)",
                },
                legend: { orientation: "h", y: -0.25 },
              }}
              config={{ responsive: true, displayModeBar: false }}
              useResizeHandler
              style={{ width: "100%", height: "390px" }}
            />
            <div className="predictive-note">
              A well-calibrated model should fall near the dashed diagonal. For
              example, games assigned a 70% home-win probability should result
              in home wins about 70% of the time across many games.
            </div>
          </>
        ) : (
          <div className="empty-state">No calibration data available.</div>
        )}
      </section>

      <section className="panel predictive-panel">
        <div className="panel-heading performance-heading">
          <div>
            <p className="eyebrow">MODEL INTERPRETABILITY</p>
            <h2>Feature Importance</h2>
            <p className="predictive-description">
              Which pregame statistics contributed most to each model's
              predictive performance?
            </p>
          </div>
          <div className="season-select-control">
            <label htmlFor="importance-model">MODEL</label>
            <select
              id="importance-model"
              value={importanceModel}
              onChange={(event) =>
                setImportanceModel(event.target.value as PredictiveModelName)
              }
            >
              {modelNames.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        </div>

        {overviewLoading ? (
          <div className="empty-state">Loading feature importance...</div>
        ) : sortedImportance.length > 0 ? (
          <>
            <Plot
              data={[
                {
                  type: "bar",
                  orientation: "h",
                  x: sortedImportance.map((item) => item.importance_mean),
                  y: sortedImportance.map((item) => item.feature),
                  error_x: {
                    type: "data",
                    array: sortedImportance.map((item) => item.importance_std),
                    visible: true,
                    color: "#aebbd0",
                  },
                  marker: { color: "#f0a45b" },
                  hovertemplate:
                    "%{y}<br>Mean decrease in ROC-AUC: %{x:.4f}<extra></extra>",
                },
              ]}
              layout={{
                autosize: true,
                height: 470,
                margin: { l: 220, r: 35, t: 20, b: 55 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { color: "#dce3ed", family: "DM Sans, sans-serif" },
                xaxis: {
                  title: { text: "Mean decrease in ROC-AUC" },
                  gridcolor: "rgba(255,255,255,0.08)",
                },
                yaxis: { automargin: true, fixedrange: true },
                showlegend: false,
              }}
              config={{ responsive: true, displayModeBar: false }}
              useResizeHandler
              style={{ width: "100%", height: "470px" }}
            />
            <div className="predictive-note">
              Importance is measured using permutation importance: the mean
              decrease in ROC-AUC when a feature is shuffled. It indicates
              predictive usefulness, not causation or the direction of a
              feature's effect. Error bars show variation across repeats.
            </div>
          </>
        ) : (
          <div className="empty-state">No feature importance data available.</div>
        )}
      </section>

      <section className="panel predictive-panel">
        <div className="panel-heading performance-heading">
          <div>
            <p className="eyebrow">GAME-LEVEL RESULTS</p>
            <h2>Historical Predictions</h2>
            <p className="predictive-description">
              Review individual model predictions alongside actual game
              outcomes.
            </p>
          </div>

          <div className="prediction-filters">
            <div className="season-select-control">
              <label htmlFor="prediction-model">MODEL</label>
              <select
                id="prediction-model"
                value={predictionModel}
                onChange={(event) => {
                  setPredictionModel(event.target.value as PredictiveModelName);
                  setPredictionPage(0);
                }}
              >
                {modelNames.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
            <div className="season-select-control">
              <label htmlFor="prediction-season">SEASON</label>
              <select
                id="prediction-season"
                value={predictionSeason}
                onChange={(event) => {
                  setPredictionSeason(event.target.value);
                  setPredictionPage(0);
                }}
              >
                <option value="">All seasons</option>
                {seasons.map((season) => (
                  <option key={season} value={season}>
                    {season}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {predictionsLoading ? (
          <div className="empty-state">Loading historical predictions...</div>
        ) : predictionsError ? (
          <div className="empty-state" role="alert">
            {predictionsError}
          </div>
        ) : predictions && predictions.predictions.length > 0 ? (
          <>
            <div className="prediction-table-wrap">
              <table className="data-table prediction-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Matchup</th>
                    <th>Final</th>
                    <th>Predicted</th>
                    <th>Home Win Probability</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.predictions.map((game) => (
                    <tr key={game.GAME_ID}>
                      <td>{game.GAME_DATE}</td>
                      <td>
                        <span className="prediction-matchup">
                          {game.AWAY_TEAM} @ {game.HOME_TEAM}
                        </span>
                      </td>
                      <td>
                        {game.AWAY_PTS.toFixed(0)}–{game.HOME_PTS.toFixed(0)}
                      </td>
                      <td>
                        {game.PREDICTED_HOME_WIN === 1
                          ? "Home win"
                          : "Away win"}
                      </td>
                      <td>
                        {(game.HOME_WIN_PROBABILITY * 100).toFixed(1)}%
                      </td>
                      <td>
                        <span
                          className={`prediction-result ${
                            game.PREDICTED_HOME_WIN === game.ACTUAL_HOME_WIN
                              ? "correct"
                              : "incorrect"
                          }`}
                        >
                          {game.PREDICTED_HOME_WIN === game.ACTUAL_HOME_WIN
                            ? "Correct"
                            : "Incorrect"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="prediction-pagination">
              <span>
                Showing {predictions.offset + 1}–
                {Math.min(
                  predictions.offset + predictions.predictions.length,
                  predictions.total,
                )}{" "}
                of {predictions.total.toLocaleString("en-US")} games
              </span>
              <div>
                <button
                  className="secondary-button"
                  disabled={predictionPage === 0}
                  onClick={() => setPredictionPage((page) => page - 1)}
                >
                  Previous
                </button>
                <button
                  className="secondary-button"
                  disabled={
                    predictions.offset + predictions.predictions.length >=
                    predictions.total
                  }
                  onClick={() => setPredictionPage((page) => page + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state">
            No historical predictions are available for this selection.
          </div>
        )}
      </section>

      <p className="predictive-footnote">
        Model evaluation is based on a historical test period beginning in{" "}
        {performance?.test_start_season ?? "the reported test season"}. These
        results describe performance on that evaluation period and should not
        be interpreted as a guarantee of future outcomes.
      </p>
    </div>
  );
}

export default PredictiveAnalytics;
