import { useEffect, useMemo, useState } from "react";
import { Icon } from "../../shared/components/AppShell";
import { jobStatuses, type Job, type JobStatus } from "../../shared/data/mockData";

const statusStyles: Record<JobStatus, string> = {
  Saved: "bg-[#f0eee6] text-[#5d5d55]",
  Applied: "bg-[#dfe5ff] text-[#2441aa]",
  "Online Assessment": "bg-[#fff0c7] text-[#735510]",
  Interview: "bg-[#ffe0d8] text-[#a13922]",
  "Final Interview": "bg-[#eadcf7] text-[#62318a]",
  Offer: "bg-[#dff2a7] text-[#315000]",
  Rejected: "bg-[#f0e4e2] text-[#81534c]",
  Withdrawn: "bg-[#e8e8e3] text-[#5c5c56]",
};

export default function JobsListPage({
  jobs,
  loading,
  error,
  hasMore,
  onSearch,
  onLoadMore,
  onAdd,
  onOpen,
  onEdit,
  onDelete,
}: {
  jobs: Job[];
  loading: boolean;
  error: string;
  hasMore: boolean;
  onSearch: (query: string) => void;
  onLoadMore: () => void;
  onAdd: () => void;
  onOpen: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"All" | JobStatus>("All");
  const [menu, setMenu] = useState<number | null>(null);
  const filtered = useMemo(() => jobs.filter((job) => status === "All" || job.status === status), [jobs, status]);

  useEffect(() => {
    const timer = window.setTimeout(() => onSearch(query.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [query, onSearch]);

  return (
    <section className="px-5 pb-28 pt-10 md:px-8 lg:px-10 lg:pt-14">
      <div className="mx-auto max-w-[1160px]">
        <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div>
            <p className="mb-3 text-xs font-extrabold uppercase tracking-[0.17em] text-[#ff6b4a]">Your opportunity board</p>
            <h1 className="font-display text-5xl font-semibold tracking-[-0.055em] md:text-6xl">Jobs <span className="ml-3 inline-grid h-8 min-w-8 place-items-center rounded-full bg-[#c8f04b] px-2 align-middle font-sans text-xs font-extrabold tracking-normal">{jobs.length}</span></h1>
            <p className="mt-3 text-sm font-medium text-[#707067]">All your applications, deadlines and next moves in one place.</p>
          </div>
          <button className="flex w-fit items-center gap-2 rounded-full bg-[#ff6b4a] px-5 py-3.5 text-sm font-extrabold text-white transition hover:-translate-y-1 hover:shadow-[0_6px_0_#171714]" onClick={onAdd}><Icon name="plus" className="h-4 w-4" />Add a job</button>
        </div>
        <div className="mt-10 flex items-center gap-3 rounded-2xl border border-[#171714]/15 bg-white px-4 focus-within:border-[#3559e0] focus-within:ring-4 focus-within:ring-[#3559e0]/10">
          <Icon name="search" className="h-5 w-5 text-[#77776d]" />
          <input className="h-14 min-w-0 flex-1 bg-transparent text-sm font-semibold outline-none" placeholder="Search by role, company or location..." value={query} onChange={(event) => setQuery(event.target.value)} />
          {query && <button className="text-xs font-bold text-[#77776d]" onClick={() => setQuery("")}>Clear</button>}
        </div>
        {error && <p className="mt-4 text-sm font-bold text-[#c53f2b]">{error}</p>}
        <div className="mt-4 flex gap-2 overflow-x-auto pb-2">
          {(["All", ...jobStatuses] as const).map((item) => <button className={`shrink-0 rounded-full border px-4 py-2 text-xs font-bold ${status === item ? "border-[#171714] bg-[#171714] text-white" : "border-[#171714]/15 bg-white text-[#6e6e65]"}`} key={item} onClick={() => setStatus(item)}>{item}</button>)}
        </div>
        <div className="mt-6 overflow-visible rounded-[26px] border border-[#171714]/15 bg-white shadow-[0_10px_40px_rgba(23,23,20,.04)]">
          <div className="hidden grid-cols-[1.5fr_1fr_1fr_.7fr_auto] gap-4 border-b border-[#171714]/10 bg-[#fffaf0] px-7 py-3 text-[10px] font-extrabold uppercase tracking-[0.14em] text-[#838379] lg:grid"><span>Company & role</span><span>Status</span><span>Location</span><span>Deadline</span><span className="w-9" /></div>
          {loading ? Array.from({ length: 5 }).map((_, index) => <div className="flex animate-pulse items-center gap-4 border-b border-[#171714]/10 p-5" key={index}><span className="h-12 w-12 rounded-2xl bg-[#e9e5da]" /><span className="h-3 w-48 rounded bg-[#e9e5da]" /></div>) : jobs.length === 0 && !query ? (
            <div className="px-6 py-20 text-center"><span className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-[#f5b8d2]"><Icon name="briefcase" /></span><h2 className="mt-6 font-display text-3xl font-semibold">No jobs yet.</h2><p className="mt-2 text-sm font-medium text-[#77776d]">Add your first one and start building momentum.</p><button className="mt-6 rounded-full bg-[#ff6b4a] px-5 py-3 text-sm font-bold text-white" onClick={onAdd}>Add a job</button></div>
          ) : filtered.length === 0 ? (
            <div className="px-6 py-20 text-center"><h2 className="font-display text-3xl font-semibold">No jobs found</h2><p className="mt-2 text-sm text-[#77776d]">Try another search or clear your filters.</p><button className="mt-5 rounded-full bg-[#171714] px-5 py-3 text-sm font-bold text-white" onClick={() => { setQuery(""); setStatus("All"); }}>Clear filters</button></div>
          ) : filtered.map((job) => (
            <article className="group relative grid cursor-pointer grid-cols-[1fr_auto] items-center gap-4 border-b border-[#171714]/10 px-5 py-5 last:border-0 hover:bg-[#fffaf0] lg:grid-cols-[1.5fr_1fr_1fr_.7fr_auto] lg:px-7" key={job.id} onClick={() => onOpen(job.id)}>
              <div className="flex min-w-0 items-center gap-4"><span className={`grid h-12 w-12 shrink-0 place-items-center rounded-2xl font-display text-xl font-semibold ${job.color}`}>{job.mark}</span><div className="min-w-0"><h2 className="truncate text-sm font-extrabold">{job.position}</h2><p className="mt-1 truncate text-xs font-semibold text-[#797970]">{job.company}</p></div></div>
              <span className={`w-fit rounded-full px-3 py-2 text-[10px] font-extrabold ${statusStyles[job.status]}`}>{job.status}</span>
              <p className="col-span-2 pl-16 text-xs font-semibold text-[#6f6f66] lg:col-span-1 lg:pl-0">{job.location}</p>
              <p className="hidden text-xs font-bold lg:block">{job.deadlineLabel}</p>
              <div className="relative" onClick={(event) => event.stopPropagation()}>
                <button aria-label="More actions" className="grid h-9 w-9 place-items-center rounded-full border border-[#171714]/15 hover:bg-[#171714] hover:text-white" onClick={() => setMenu(menu === job.id ? null : job.id)}><Icon name="more" className="h-4 w-4" /></button>
                {menu === job.id && <div className="absolute right-0 top-11 z-20 w-32 rounded-xl border border-[#171714]/10 bg-white p-1.5 shadow-xl"><button className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs font-bold hover:bg-[#f5f1e8]" onClick={() => onEdit(job.id)}><Icon name="edit" className="h-4 w-4" />Edit</button><button className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs font-bold text-[#a13922] hover:bg-[#fff0ec]" onClick={() => { setMenu(null); if (window.confirm(`Delete ${job.position} at ${job.company}?`)) onDelete(job.id); }}><Icon name="trash" className="h-4 w-4" />Delete</button></div>}
              </div>
            </article>
          ))}
        </div>
        {hasMore && !loading && <button className="mx-auto mt-6 block rounded-full bg-[#171714] px-5 py-3 text-sm font-bold text-white" onClick={onLoadMore}>Load more</button>}
      </div>
    </section>
  );
}
