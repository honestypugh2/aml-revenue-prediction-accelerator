// Typed fetch helpers and TanStack Query hooks for the accelerator API.
import { useMutation, useQuery } from "@tanstack/react-query";
import type {
  Area,
  CleaningPreview,
  Config,
  ContextualNote,
  DatasetOverview,
  EdaPreview,
  ExplainResponse,
  FacilitySeries,
  FeaturePreview,
  GradeResponse,
  KnowledgeCheck,
  LeakageInfo,
  Lesson,
  OptimizePreview,
  PredictPreview,
  ReadinessDimension,
  SplitPreview,
  SuccessCriteria,
  TargetPreview,
  TrainResponse,
  WalkthroughStep,
} from "./types";

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    throw new Error(`GET ${url} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

async function postJSON<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`POST ${url} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export function useConfig(env: string) {
  return useQuery({
    queryKey: ["config", env],
    queryFn: () => getJSON<Config>(`/api/config?env=${env}`),
  });
}

export function useDatasetOverview(env: string) {
  return useQuery({
    queryKey: ["overview", env],
    queryFn: () => getJSON<DatasetOverview>(`/api/dataset/overview?env=${env}`),
  });
}

// One or more real synthetic rows (all columns) — used to show authentic field
// values in the flow simulator's payload inspector.
export function useDatasetSample(env: string, limit = 1) {
  return useQuery({
    queryKey: ["dataset-sample", env, limit],
    queryFn: () =>
      getJSON<Record<string, number | string | boolean | null>[]>(
        `/api/dataset/sample?env=${env}&limit=${limit}`,
      ),
  });
}

export function useFacilitySeries(env: string, facilityId: string | undefined) {
  return useQuery({
    queryKey: ["facility-series", env, facilityId],
    enabled: Boolean(facilityId),
    queryFn: () =>
      getJSON<FacilitySeries>(
        `/api/dataset/facility-series?env=${env}&facility_id=${facilityId}`,
      ),
  });
}

export function useContextualNotes(area: Area) {
  return useQuery({
    queryKey: ["notes", area],
    queryFn: () =>
      getJSON<ContextualNote[]>(`/api/education/contextual-notes?area=${area}`),
  });
}

export function useLessons() {
  return useQuery({
    queryKey: ["lessons"],
    queryFn: () => getJSON<Lesson[]>("/api/education/lessons"),
  });
}

export function useKnowledgeChecks() {
  return useQuery({
    queryKey: ["checks"],
    queryFn: () => getJSON<KnowledgeCheck[]>("/api/education/knowledge-checks"),
  });
}

export function useTrain() {
  return useMutation({
    mutationKey: ["train"],
    mutationFn: (env: string) =>
      postJSON<TrainResponse>("/api/train", { environment: env }),
  });
}

export function gradeAnswer(key: string, chosenIndex: number) {
  return postJSON<GradeResponse>(
    `/api/education/knowledge-checks/${key}/grade`,
    { chosen_index: chosenIndex },
  );
}

// ---- Guided walkthrough + pipeline steps ----
export function useWalkthrough() {
  return useQuery({
    queryKey: ["walkthrough"],
    queryFn: () => getJSON<WalkthroughStep[]>("/api/education/walkthrough"),
  });
}

export function useSuccessCriteria() {
  return useQuery({
    queryKey: ["success-criteria"],
    queryFn: () => getJSON<SuccessCriteria>("/api/education/success-criteria"),
  });
}

export function useDataReadiness() {
  return useQuery({
    queryKey: ["data-readiness"],
    queryFn: () => getJSON<ReadinessDimension[]>("/api/education/data-readiness"),
  });
}

export function useLeakage(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["leakage", env],
    enabled,
    queryFn: () => getJSON<LeakageInfo>(`/api/pipeline/leakage?env=${env}`),
  });
}

export function useTargetPreview(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["target", env],
    enabled,
    queryFn: () => getJSON<TargetPreview>(`/api/pipeline/target?env=${env}`),
  });
}

export function useSplitPreview(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["split", env],
    enabled,
    queryFn: () => getJSON<SplitPreview>(`/api/pipeline/split?env=${env}`),
  });
}

export function useFeaturePreview(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["features", env],
    enabled,
    queryFn: () => getJSON<FeaturePreview>(`/api/pipeline/features?env=${env}`),
  });
}

export function useExplain(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["explain", env],
    enabled,
    queryFn: () => getJSON<ExplainResponse>(`/api/pipeline/explain?env=${env}`),
  });
}

export function usePredict(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["predict", env],
    enabled,
    queryFn: () => getJSON<PredictPreview>(`/api/pipeline/predict?env=${env}`),
  });
}

export function useCleaning(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["cleaning", env],
    enabled,
    queryFn: () => getJSON<CleaningPreview>(`/api/pipeline/cleaning?env=${env}`),
  });
}

export function useEda(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["eda", env],
    enabled,
    queryFn: () => getJSON<EdaPreview>(`/api/pipeline/eda?env=${env}`),
  });
}

export function useOptimize(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["optimize", env],
    enabled,
    queryFn: () => getJSON<OptimizePreview>(`/api/pipeline/optimize?env=${env}`),
  });
}

// Training is a POST but idempotent + cached server-side; expose it as a query
// so the train/evaluate/select steps share one result without re-running.
export function useTraining(env: string, enabled: boolean) {
  return useQuery({
    queryKey: ["training", env],
    enabled,
    staleTime: 5 * 60_000,
    queryFn: () => postJSON<TrainResponse>("/api/train", { environment: env }),
  });
}
