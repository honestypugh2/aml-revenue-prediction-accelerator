// Types mirroring the FastAPI backend response models.

export type EnvName = "dev" | "test" | "prod";

export type Area =
  | "overview"
  | "data"
  | "training"
  | "evaluation"
  | "predictions"
  | "governance"
  | "fabric"
  | "security";

export interface Config {
  environment: string;
  facilities: number;
  months: number;
  snapshot_days: number[];
  demo_cutoff_day: number;
  candidates: string[];
  primary_metric: string;
  azure_ml_configured: boolean;
  fabric_configured: boolean;
}

export interface DatasetOverview {
  environment: string;
  rows: number;
  facilities: string[];
  months: string[];
  snapshot_days: number[];
  target_mean: number;
  target_min: number;
  target_max: number;
}

export interface FacilityPoint {
  accounting_month: string;
  actual_month_end_net_revenue: number;
}

export interface FacilitySeries {
  facility_id: string;
  points: FacilityPoint[];
}

export interface ModelMetrics {
  model: string;
  wape: number;
  bias: number;
  mae: number;
  rmse: number;
  mape: number;
  smape: number;
  r2: number;
  is_champion: boolean;
}

export interface GroupMetrics {
  group: string;
  n: number;
  wape: number;
  bias: number;
  mae: number;
  rmse: number;
  mape: number;
  smape: number;
  r2: number;
}

export interface TrainResponse {
  environment: string;
  metric: string;
  champion: string;
  challenger: string | null;
  challenger_promotable: boolean;
  ranking: ModelMetrics[];
  by_facility: GroupMetrics[];
  by_snapshot_day: GroupMetrics[];
}

export interface Lesson {
  key: string;
  title: string;
  summary: string;
  body: string;
  references: string[];
}

export interface ContextualNote {
  area: Area;
  title: string;
  detail: string;
  lesson_key: string | null;
  tip: string | null;
}

export interface KnowledgeCheck {
  key: string;
  question: string;
  options: string[];
}

export interface GradeResponse {
  key: string;
  correct: boolean;
  correct_index: number;
  explanation: string;
}

export interface WalkthroughStep {
  key: string;
  number: number;
  phase: string;
  title: string;
  goal: string;
  concept: string;
  what_we_do: string;
  interpret: string;
  action: string;
  lesson_key: string | null;
}

export interface MetricTarget {
  checkpoint: string;
  primary_metric: string;
  target: string;
  must_beat: string;
}

export interface SuccessCriterion {
  category: string;
  name: string;
  target: string;
}

export interface SuccessCriteria {
  headline: string;
  metric_targets: MetricTarget[];
  criteria: SuccessCriterion[];
}

export type Rag = "green" | "amber" | "red";

export interface ReadinessDimension {
  key: string;
  dimension: string;
  description: string;
  default_rating: Rag;
  is_gate: boolean;
  guidance: string;
}

export interface SplitPreview {
  environment: string;
  train_months: string[];
  validation_months: string[];
  test_months: string[];
  train_rows: number;
  validation_rows: number;
  test_rows: number;
}

export interface TargetPreviewItem {
  facility_id: string;
  accounting_month: string;
  snapshot_day: number;
  gross_charges: number;
  net_revenue: number;
  gross_to_net_ratio: number;
}

export interface TargetPreview {
  environment: string;
  items: TargetPreviewItem[];
  average_gross_to_net_ratio: number;
}

export interface LeakageInfo {
  forbidden_columns: string[];
  rules: string[];
}

export interface FeaturePreview {
  environment: string;
  raw_columns: string[];
  engineered_features: string[];
  n_raw: number;
  n_engineered: number;
  example: Record<string, number>;
}

export interface ImportanceItem {
  feature: string;
  importance: number;
}

export interface ExplainResponse {
  environment: string;
  model: string;
  items: ImportanceItem[];
}

export interface PredictionRow {
  facility_id: string;
  accounting_month: string;
  snapshot_date: string;
  snapshot_day: number;
  predicted_month_end_net_revenue: number;
  actual_month_end_net_revenue: number | null;
  abs_pct_error: number | null;
  prediction_lower: number | null;
  prediction_upper: number | null;
}

export interface PredictPreview {
  environment: string;
  model_name: string;
  model_version: string;
  run_id: string;
  cutoff_day: number;
  scored_at: string;
  has_intervals: boolean;
  wape: number;
  rows: PredictionRow[];
}

export interface CleaningColumn {
  column: string;
  missing_count: number;
  missing_pct: number;
  strategy: string;
}

export interface CleaningPreview {
  environment: string;
  rows: number;
  columns_with_missing: CleaningColumn[];
  outlier_note: string;
}

export interface CorrelationItem {
  feature: string;
  corr_with_target: number;
}

export interface SkewItem {
  feature: string;
  skewness: number;
}

export interface EdaPreview {
  environment: string;
  target: string;
  correlations: CorrelationItem[];
  skewness: SkewItem[];
}

export interface OptimizeTrial {
  setting: string;
  wape: number;
  is_best: boolean;
}

export interface OptimizePreview {
  environment: string;
  model: string;
  hyperparameter: string;
  trials: OptimizeTrial[];
  best_setting: string;
}
