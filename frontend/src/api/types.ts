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
