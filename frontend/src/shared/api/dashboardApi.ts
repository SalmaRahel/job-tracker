import { apiFetch } from "./client";
import { jobStatuses, type JobStatus } from "../types";

type ApiStats = {
  total: number;
  by_status: Record<string, number>;
  monthly: { month: string; count: number }[];
};

export type Dashboard = {
  total: number;
  active: number;
  interviews: number;
  offers: number;
  rejections: number;
  statusCounts: { status: JobStatus; count: number }[];
  months: { month: string; count: number }[];
};

const INACTIVE: JobStatus[] = ["Offer", "Rejected", "Withdrawn"];
const INTERVIEW: JobStatus[] = ["Interview", "Final Interview"];

const monthName = (value: string) => {
  const [year, month] = value.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString("en-GB", { month: "short" });
};

export function toDashboard(stats: ApiStats): Dashboard {
  const count = (status: JobStatus) => stats.by_status[status] ?? 0;
  const sum = (statuses: JobStatus[]) => statuses.reduce((total, status) => total + count(status), 0);
  return {
    total: stats.total,
    active: sum(jobStatuses.filter((status) => !INACTIVE.includes(status))),
    interviews: sum(INTERVIEW),
    offers: count("Offer"),
    rejections: count("Rejected"),
    statusCounts: jobStatuses.map((status) => ({ status, count: count(status) })).filter((item) => item.count > 0),
    months: stats.monthly.map((item) => ({ month: monthName(item.month), count: item.count })),
  };
}

export const getDashboard = async () => toDashboard(await apiFetch<ApiStats>("/jobs/stats"));
