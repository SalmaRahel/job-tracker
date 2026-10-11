import { apiFetch } from "./client";
import type { Job, JobStatus } from "../types";

type ApiJob = {
  id: number;
  company_name: string;
  position: string;
  location: string;
  application_date: string | null;
  deadline: string | null;
  job_link: string | null;
  job_description: string | null;
  status: JobStatus;
};

type ApiPage = {
  items: ApiJob[];
  has_more: boolean;
  next_cursor: { id: number; created_at: string } | null;
};

export type Cursor = ApiPage["next_cursor"];

const colors = [
  "bg-[#3559e0] text-white",
  "bg-[#ff6b4a] text-white",
  "bg-[#c8f04b] text-[#171714]",
  "bg-[#f5b8d2] text-[#171714]",
  "bg-[#171714] text-white",
  "bg-[#ff9f80] text-[#171714]",
  "bg-[#8da1ed] text-[#171714]",
];

const dateLabel = (date: string | null) =>
  date ? new Date(`${date}T12:00:00`).toLocaleDateString("en-GB", { month: "short", day: "2-digit" }) : "No date";

const toJob = (job: ApiJob): Job => ({
  id: job.id,
  company: job.company_name,
  position: job.position,
  location: job.location,
  status: job.status,
  deadline: job.deadline ?? "",
  deadlineLabel: dateLabel(job.deadline),
  mark: job.company_name.charAt(0).toUpperCase(),
  color: colors[job.id % colors.length],
  applicationDate: job.application_date ?? "",
  link: job.job_link ?? "",
  description: job.job_description ?? "",
});

const toBody = (job: Job) => ({
  company_name: job.company,
  position: job.position,
  location: job.location,
  status: job.status,
  application_date: job.applicationDate || null,
  deadline: job.deadline || null,
  job_link: job.link || null,
  job_description: job.description || null,
});

export async function listJobs(search: string, cursor: Cursor = null) {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (cursor) {
    params.set("last_seen_created_at", cursor.created_at);
    params.set("last_seen_id", String(cursor.id));
  }
  const page = await apiFetch<ApiPage>(`/jobs/?${params}`);
  return { jobs: page.items.map(toJob), hasMore: page.has_more, cursor: page.next_cursor };
}

export const getJob = async (id: number) => toJob(await apiFetch<ApiJob>(`/jobs/${id}`));

export const createJob = async (job: Job) =>
  toJob(await apiFetch<ApiJob>("/jobs/", { method: "POST", body: toBody(job) }));

export const updateJob = async (job: Job) =>
  toJob(await apiFetch<ApiJob>(`/jobs/${job.id}`, { method: "PUT", body: toBody(job) }));

export const changeStatus = async (id: number, status: JobStatus) =>
  toJob(await apiFetch<ApiJob>(`/jobs/${id}`, { method: "PUT", body: { status } }));

export const deleteJob = (id: number) => apiFetch<null>(`/jobs/${id}`, { method: "DELETE" });
