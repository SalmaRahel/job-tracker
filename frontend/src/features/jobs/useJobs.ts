import { useEffect, useRef, useState } from "react";
import * as jobsApi from "../../shared/api/jobsApi";
import type { Job, JobStatus } from "../../shared/types";

const message = (err: unknown) => (err instanceof Error ? err.message : "Something went wrong");

export function useJobs(enabled: boolean) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState<{ hasMore: boolean; cursor: jobsApi.Cursor }>({ hasMore: false, cursor: null });
  const [selected, setSelected] = useState<Job | null>(null);
  const [selecting, setSelecting] = useState(false);
  const latest = useRef(0);

  useEffect(() => {
    if (!enabled) return setJobs([]);
    let current = true;
    setLoading(true);
    setError("");
    jobsApi
      .listJobs(search)
      .then((result) => {
        if (!current) return;
        setJobs(result.jobs);
        setPage({ hasMore: result.hasMore, cursor: result.cursor });
      })
      .catch((err) => current && setError(message(err)))
      .finally(() => current && setLoading(false));
    return () => {
      current = false;
    };
  }, [enabled, search]);

  const loadMore = async () => {
    try {
      const result = await jobsApi.listJobs(search, page.cursor);
      setJobs((current) => [...current, ...result.jobs]);
      setPage({ hasMore: result.hasMore, cursor: result.cursor });
    } catch (err) {
      setError(message(err));
    }
  };

  const select = async (id: number) => {
    const cached = jobs.find((job) => job.id === id) ?? null;
    const request = ++latest.current;
    setSelected(cached);
    setSelecting(!cached);
    try {
      const job = await jobsApi.getJob(id);
      if (request === latest.current) setSelected(job);
    } catch {
      if (request === latest.current && !cached) setSelected(null);
    } finally {
      if (request === latest.current) setSelecting(false);
    }
  };

  const replace = (job: Job) => {
    setJobs((current) => current.map((item) => (item.id === job.id ? job : item)));
    setSelected(job);
  };

  const save = async (job: Job, editing: boolean) => {
    const saved = editing ? await jobsApi.updateJob(job) : await jobsApi.createJob(job);
    if (editing) replace(saved);
    else setJobs((current) => [saved, ...current]);
    setSelected(saved);
    return saved;
  };

  const remove = async (id: number) => {
    await jobsApi.deleteJob(id);
    setJobs((current) => current.filter((job) => job.id !== id));
  };

  const setStatus = async (id: number, status: JobStatus) => replace(await jobsApi.changeStatus(id, status));

  return { jobs, loading, error, hasMore: page.hasMore, selected, selecting, setSearch, loadMore, select, save, remove, setStatus };
}
