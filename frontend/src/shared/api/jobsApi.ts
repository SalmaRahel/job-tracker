import { jobs } from "../data/mockData";

export async function listJobs() {
  await new Promise((resolve) => window.setTimeout(resolve, 350));
  return jobs;
}
