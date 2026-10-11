import { ApiError, apiFetch } from "./client";

export const startCv = (jobId: number) =>
  apiFetch<{ job_id: number; status: string }>(`/jobs/${jobId}/generate-cv?palette_name=`, { method: "POST" });

export async function getCvUrl(jobId: number): Promise<string | null> {
  try {
    return (await apiFetch<{ url: string }>(`/jobs/${jobId}/download-cv`)).url;
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
