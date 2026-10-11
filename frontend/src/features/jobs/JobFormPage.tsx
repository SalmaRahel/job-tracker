import { useState, type FormEvent } from "react";
import { Icon } from "../../shared/components/AppShell";
import { jobStatuses, type Job, type JobStatus } from "../../shared/types";

const fieldClass = "mt-2 w-full rounded-2xl border border-[#171714]/15 bg-white px-4 py-3.5 text-sm font-semibold outline-none transition focus:border-[#3559e0] focus:ring-4 focus:ring-[#3559e0]/10";

export default function JobFormPage({ job, onCancel, onSave }: { job?: Job; onCancel: () => void; onSave: (job: Job) => void }) {
  const [form, setForm] = useState({ company: job?.company ?? "", position: job?.position ?? "", location: job?.location ?? "", status: job?.status ?? "Saved" as JobStatus, applicationDate: job?.applicationDate ?? "", deadline: job?.deadline ?? "", link: job?.link ?? "", description: job?.description ?? "" });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const update = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));
  const submit = (event: FormEvent) => {
    event.preventDefault();
    const next: Record<string, string> = {};
    if (!form.company.trim()) next.company = "Company is required.";
    if (!form.position.trim()) next.position = "Position is required.";
    if (!form.location.trim()) next.location = "Location is required.";
    if (form.link && !/^https?:\/\//.test(form.link)) next.link = "Use a full URL starting with http:// or https://.";
    if (form.deadline && form.applicationDate && form.deadline < form.applicationDate) next.deadline = "Deadline cannot be before the application date.";
    setErrors(next);
    if (Object.keys(next).length) return;
    onSave({ id: job?.id ?? Date.now(), ...form, mark: form.company.charAt(0).toUpperCase(), color: job?.color ?? "bg-[#f5b8d2] text-[#171714]", deadlineLabel: form.deadline ? new Date(`${form.deadline}T12:00:00`).toLocaleDateString("en-GB", { month: "short", day: "2-digit" }) : "No date" });
  };
  return (
    <section className="px-5 pb-28 pt-8 md:px-8 lg:px-10">
      <div className="mx-auto max-w-[900px]">
        <button className="mb-7 flex items-center gap-2 text-sm font-bold text-[#6f6f66]" onClick={onCancel}><Icon name="back" className="h-4 w-4" />Back to jobs</button>
        <p className="text-xs font-extrabold uppercase tracking-[0.17em] text-[#ff6b4a]">{job ? "Update opportunity" : "New opportunity"}</p>
        <h1 className="mt-3 font-display text-5xl font-semibold tracking-[-0.055em]">{job ? "Edit job" : "Add a job"}</h1>
        <form className="mt-9 rounded-[28px] border border-[#171714]/15 bg-[#fffaf0] p-5 shadow-[7px_7px_0_#171714] md:p-8" onSubmit={submit}>
          <div className="grid gap-5 md:grid-cols-2">
            {[["company", "Company", "e.g. Luma Labs"], ["position", "Position", "e.g. Product Designer"], ["location", "Location", "e.g. London or Remote"]].map(([key, label, placeholder]) => <label className="text-sm font-extrabold" key={key}>{label}<input className={`${fieldClass} ${errors[key] ? "border-[#d64b35]" : ""}`} placeholder={placeholder} value={form[key as keyof typeof form]} onChange={(event) => update(key, event.target.value)} />{errors[key] && <span className="mt-2 block text-xs font-bold text-[#c53f2b]">{errors[key]}</span>}</label>)}
            <label className="text-sm font-extrabold">Status<select className={fieldClass} value={form.status} onChange={(event) => update("status", event.target.value)}>{jobStatuses.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label className="text-sm font-extrabold">Application date<input className={fieldClass} type="date" value={form.applicationDate} onChange={(event) => update("applicationDate", event.target.value)} /></label>
            <label className="text-sm font-extrabold">Deadline<input className={fieldClass} type="date" value={form.deadline} onChange={(event) => update("deadline", event.target.value)} />{errors.deadline && <span className="mt-2 block text-xs font-bold text-[#c53f2b]">{errors.deadline}</span>}</label>
            <label className="text-sm font-extrabold md:col-span-2">Job link<input className={fieldClass} placeholder="https://..." value={form.link} onChange={(event) => update("link", event.target.value)} />{errors.link && <span className="mt-2 block text-xs font-bold text-[#c53f2b]">{errors.link}</span>}</label>
            <label className="text-sm font-extrabold md:col-span-2">Job description<textarea className={`${fieldClass} min-h-52 resize-y leading-6`} placeholder="Paste the full job description here..." value={form.description} onChange={(event) => update("description", event.target.value)} /></label>
          </div>
          <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end"><button className="rounded-full border border-[#171714]/20 bg-white px-6 py-3.5 text-sm font-bold" type="button" onClick={onCancel}>Cancel</button><button className="rounded-full bg-[#3559e0] px-7 py-3.5 text-sm font-extrabold text-white" type="submit">{job ? "Save changes" : "Add job"}</button></div>
        </form>
      </div>
    </section>
  );
}
