import { ApiError, apiFetch } from "./client";

export type CvTemplate = "plain" | "colored";
export type CvPalette = "dark_gray_blue" | "frosted_mint" | "light_gray";
export type CvStyle = { template: CvTemplate; palette: CvPalette };

export const startCv = (jobId: number, style: CvStyle) =>
  apiFetch<{ job_id: number; status: string }>(`/jobs/${jobId}/generate-cv`, { method: "POST", body: style });

export async function getCvUrl(jobId: number): Promise<string | null> {
  try {
    return (await apiFetch<{ url: string }>(`/jobs/${jobId}/download-cv`)).url;
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
