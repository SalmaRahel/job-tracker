import { Icon } from "../../shared/components/AppShell";
import { jobStatuses, type Job, type Profile } from "../../shared/data/mockData";
import MatchAnalysisCard from "../matching/MatchAnalysisCard";
import CvCard from "../cv/CvCard";

export default function JobDetailPage({ job, profile, onBack, onEdit, onStatus, onProfile }: { job: Job; profile: Profile | null; onBack: () => void; onEdit: () => void; onStatus: (status: Job["status"]) => void; onProfile: () => void }) {
  return (
    <section className="px-5 pb-28 pt-8 md:px-8 lg:px-10">
      <div className="mx-auto max-w-[1080px]">
        <button className="mb-7 flex items-center gap-2 text-sm font-bold text-[#6f6f66]" onClick={onBack}><Icon name="back" className="h-4 w-4" />Back to jobs</button>
        <div className="rounded-[30px] bg-[#fffaf0] p-6 md:p-9">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-start">
            <div className="flex gap-5"><span className={`grid h-16 w-16 shrink-0 place-items-center rounded-2xl font-display text-2xl font-semibold ${job.color}`}>{job.mark}</span><div><p className="text-sm font-extrabold text-[#77776d]">{job.company}</p><h1 className="mt-1 font-display text-4xl font-semibold tracking-[-.045em] md:text-5xl">{job.position}</h1></div></div>
            <button className="flex w-fit items-center gap-2 rounded-full border border-[#171714]/20 bg-white px-5 py-3 text-sm font-bold" onClick={onEdit}><Icon name="edit" className="h-4 w-4" />Edit</button>
          </div>
          <div className="mt-8 grid gap-4 border-t border-[#171714]/10 pt-6 sm:grid-cols-2 lg:grid-cols-4">
            <Detail icon="location" label="Location" value={job.location} />
            <Detail icon="calendar" label="Applied" value={job.applicationDate || "Not applied yet"} />
            <Detail icon="calendar" label="Deadline" value={job.deadlineLabel} />
            <label className="text-[10px] font-extrabold uppercase tracking-[.14em] text-[#77776d]">Status<select className="mt-2 w-full rounded-xl border border-[#171714]/15 bg-white px-3 py-2.5 text-xs font-bold text-[#171714]" value={job.status} onChange={(event) => onStatus(event.target.value as Job["status"])}>{jobStatuses.map((status) => <option key={status}>{status}</option>)}</select></label>
          </div>
          {job.link && <a className="mt-6 inline-flex items-center gap-2 text-sm font-extrabold text-[#3559e0] underline underline-offset-4" href={job.link} target="_blank" rel="noreferrer"><Icon name="link" className="h-4 w-4" />Open original job listing</a>}
          <div className="mt-8"><h2 className="text-xs font-extrabold uppercase tracking-[.14em] text-[#77776d]">Job description</h2><p className="mt-3 whitespace-pre-wrap text-sm font-medium leading-7 text-[#56564f]">{job.description || "No description has been added yet."}</p></div>
        </div>
        <div className="mt-7 grid gap-7 lg:grid-cols-2"><MatchAnalysisCard job={job} profile={profile} onProfile={onProfile} /><CvCard job={job} profile={profile} onProfile={onProfile} /></div>
      </div>
    </section>
  );
}

function Detail({ icon, label, value }: { icon: "location" | "calendar"; label: string; value: string }) {
  return <div><span className="flex items-center gap-2 text-[10px] font-extrabold uppercase tracking-[.14em] text-[#77776d]"><Icon name={icon} className="h-4 w-4" />{label}</span><p className="mt-2 text-sm font-bold">{value}</p></div>;
}
