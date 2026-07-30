// Typed fetch helpers and TanStack Query hooks for the accelerator API.
import { useMutation, useQuery } from "@tanstack/react-query";
import type {
  Area,
  Config,
  ContextualNote,
  DatasetOverview,
  FacilitySeries,
  GradeResponse,
  KnowledgeCheck,
  Lesson,
  TrainResponse,
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
