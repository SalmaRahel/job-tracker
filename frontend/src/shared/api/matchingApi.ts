import { ApiError, apiFetch } from "./client";

type ApiAnalysis = { id: number; score: number; missing_requirements: string[] };
export type Analysis = { id: number; score: number; missing: string[] };

export const startAnalysis = (jobId: number) => apiFetch<{ message: string }>(`/jobs/${jobId}/analyze`, { method: "POST" });

export async function getAnalysis(jobId: number): Promise<Analysis | null> {
  try {
    const data = await apiFetch<ApiAnalysis>(`/jobs/${jobId}/analysis`);
    return { id: data.id, score: data.score, missing: data.missing_requirements };
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
