import { applicationsByMonth, jobStatuses, type Job } from "../../shared/data/mockData";
import { Icon } from "../../shared/components/AppShell";

export default function DashboardPage({ jobs, onAdd }: { jobs: Job[]; onAdd: () => void }) {
  if (!jobs.length) return <section className="grid min-h-[calc(100vh-72px)] place-items-center px-5 pb-24"><div className="text-center"><span className="mx-auto grid h-20 w-20 place-items-center rounded-full bg-[#f5b8d2]"><Icon name="grid" /></span><h1 className="mt-6 font-display text-4xl font-semibold">Nothing to chart yet.</h1><p className="mt-3 text-sm text-[#77776d]">Add your first job to start seeing your progress.</p><button className="mt-6 rounded-full bg-[#ff6b4a] px-6 py-3.5 text-sm font-bold text-white" onClick={onAdd}>Add a job</button></div></section>;
  const active = jobs.filter((job) => !["Saved", "Rejected", "Withdrawn"].includes(job.status)).length;
  const interviews = jobs.filter((job) => job.status.includes("Interview")).length;
  const metrics = [
    ["Total applications", jobs.length, "bg-[#3559e0] text-white"],
    ["Active", active, "bg-[#ff6b4a] text-white"],
    ["Interviews", interviews, "bg-[#f5b8d2]"],
    ["Offers", jobs.filter((job) => job.status === "Offer").length, "bg-[#c8f04b]"],
    ["Rejections", jobs.filter((job) => job.status === "Rejected").length, "bg-white"],
  ];
  const statusCounts = jobStatuses.map((status) => ({ status, count: jobs.filter((job) => job.status === status).length })).filter((item) => item.count);
  const colors = ["#3559e0", "#ff6b4a", "#f5b8d2", "#c8f04b", "#8563a8", "#ffac88", "#9d9d91"];
  return (
    <section className="px-5 pb-28 pt-10 md:px-8 lg:px-10 lg:pt-14">
      <div className="mx-auto max-w-[1160px]">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p className="text-xs font-extrabold uppercase tracking-[.17em] text-[#ff6b4a]">Your progress at a glance</p><h1 className="mt-3 font-display text-5xl font-semibold tracking-[-.055em] md:text-6xl">Dashboard</h1><p className="mt-3 text-sm font-medium text-[#707067]">A clearer view of where your search is moving.</p></div><button className="flex w-fit items-center gap-2 rounded-full bg-[#171714] px-5 py-3 text-sm font-bold text-white" onClick={onAdd}><Icon name="plus" className="h-4 w-4" />Add job</button></div>
        <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{metrics.map(([label, value, color]) => <article className={`rounded-[24px] border border-[#171714]/10 p-5 ${color}`} key={label}><p className="text-[10px] font-extrabold uppercase tracking-[.13em] opacity-70">{label}</p><p className="mt-7 font-display text-5xl font-semibold">{value}</p></article>)}</div>
        <div className="mt-7 grid gap-7 lg:grid-cols-2">
          <article className="rounded-[28px] border border-[#171714]/10 bg-white p-6 md:p-8"><div><p className="text-xs font-extrabold uppercase tracking-[.15em] text-[#77776d]">Pipeline shape</p><h2 className="mt-2 font-display text-3xl font-semibold">Status distribution</h2></div><div className="mt-8 flex items-center gap-8"><div className="relative h-44 w-44 shrink-0 rounded-full" style={{ background: `conic-gradient(${statusCounts.map((item, index) => `${colors[index]} ${index * (100 / statusCounts.length)}% ${(index + 1) * (100 / statusCounts.length)}%`).join(",")})` }}><div className="absolute inset-9 grid place-items-center rounded-full bg-white text-center"><span><strong className="font-display text-3xl">{jobs.length}</strong><small className="block text-[9px] font-bold uppercase text-[#77776d]">jobs</small></span></div></div><div className="min-w-0 space-y-3">{statusCounts.map((item, index) => <div className="flex items-center gap-2 text-xs font-bold" key={item.status}><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: colors[index] }} /><span className="truncate">{item.status}</span><span className="ml-auto">{item.count}</span></div>)}</div></div></article>
          <article className="rounded-[28px] border border-[#171714]/10 bg-white p-6 md:p-8"><p className="text-xs font-extrabold uppercase tracking-[.15em] text-[#77776d]">Last six months</p><h2 className="mt-2 font-display text-3xl font-semibold">Applications per month</h2><div className="mt-9 flex h-52 items-end gap-3 border-b border-[#171714]/15">{applicationsByMonth.map((item, index) => <div className="flex h-full flex-1 flex-col justify-end text-center" key={item.month}><span className="mb-2 text-xs font-extrabold">{item.count}</span><div className={`mx-auto w-full max-w-12 rounded-t-xl ${index === applicationsByMonth.length - 1 ? "bg-[#ff6b4a]" : "bg-[#3559e0]"}`} style={{ height: `${item.count * 8}%` }} /><span className="py-3 text-[10px] font-bold text-[#77776d]">{item.month}</span></div>)}</div></article>
        </div>
      </div>
    </section>
  );
}
