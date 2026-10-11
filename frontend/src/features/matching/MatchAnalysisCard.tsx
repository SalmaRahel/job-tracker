import { useState } from "react";
import { Icon } from "../../shared/components/AppShell";
import type { Job, Profile } from "../../shared/data/mockData";
import { useMatching } from "./useMatching";

export default function MatchAnalysisCard({ job, profile, onProfile }: { job: Job; profile: Profile | null; onProfile: () => void }) {
  const { result, phase, error, waiting, run } = useMatching(job.id);
  const [blocked, setBlocked] = useState<"profile" | "description" | null>(null);
  const loading = phase === "loading";
  const start = () => {
    if (loading || waiting) return;
    if (!job.description) return setBlocked("description");
    if (!profile || profile.skills.length < 3) return setBlocked("profile");
    setBlocked(null);
    run();
  };
  const score = result?.score ?? 0;
  const label = score >= 80 ? "Strong" : score >= 50 ? "Moderate" : "Weak";
  return (
    <article className="rounded-[28px] border border-[#171714] bg-white p-6 shadow-[6px_6px_0_#171714] md:p-8">
      <div className="flex items-start justify-between gap-5"><div><span className="text-xs font-extrabold uppercase tracking-[0.16em] text-[#3559e0]">AI match analysis</span><h2 className="mt-2 font-display text-3xl font-semibold">How well do you fit?</h2></div><span className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-[#f5b8d2]"><Icon name="spark" /></span></div>
      {loading ? <div className="mt-8 animate-pulse"><div className="h-24 rounded-2xl bg-[#eeeae1]" /><div className="mt-4 h-3 w-3/4 rounded bg-[#eeeae1]" /><p className="mt-4 text-sm font-bold text-[#77776d]">Reading the role and comparing your profile…</p></div> :
      blocked === "profile" ? <StateBox title="Build your profile first" copy="Add at least 3 skills to unlock match analysis." action="Go to Profile" onAction={onProfile} /> :
      blocked === "description" ? <StateBox title="Add a job description to analyze" copy="Edit this job and paste the description so AI has something to compare." /> :
      phase === "failed" ? <StateBox title="Analysis failed" copy="Something interrupted the analysis. Your job details are safe." action="Retry" onAction={start} /> :
      result ? <div className="mt-7"><div className="flex items-center gap-5 rounded-2xl bg-[#fffaf0] p-5"><span className={`grid h-24 w-24 place-items-center rounded-full border-[9px] ${score >= 80 ? "border-[#c8f04b]" : score >= 50 ? "border-[#ffc85c]" : "border-[#ff8066]"}`}><span className="font-display text-3xl font-semibold">{score}</span></span><div><p className="text-xs font-extrabold uppercase tracking-[.15em] text-[#77776d]">Your match</p><p className="mt-1 font-display text-3xl font-semibold">{label}</p></div></div><h3 className="mt-6 text-sm font-extrabold">Missing requirements</h3><ul className="mt-3 space-y-2">{result.missing.length === 0 ? <li className="text-sm font-medium text-[#77776d]">Nothing missing. Great fit.</li> : result.missing.map((item) => <li className="flex items-center gap-3 text-sm font-medium" key={item}><span className="h-2 w-2 rounded-full bg-[#ff6b4a]" />{item}</li>)}</ul></div> :
      <p className="mt-6 text-sm font-medium leading-6 text-[#707067]">Compare this role with your skills and experience, then see the gaps worth addressing.</p>}
      {error && <p className="mt-5 text-xs font-bold text-[#c53f2b]">{error}</p>}
      {waiting && !error && result && <p className="mt-5 text-center text-xs font-bold text-[#77776d]">Please wait a moment before re-analyzing.</p>}
      <button className="mt-7 w-full rounded-full bg-[#3559e0] px-5 py-3.5 text-sm font-extrabold text-white disabled:cursor-not-allowed disabled:opacity-50" disabled={loading || waiting} onClick={start}>{loading ? "Analyzing…" : waiting ? "Please wait a moment" : result ? "Re-analyze" : "Analyze"}</button>
    </article>
  );
}

function StateBox({ title, copy, action, onAction }: { title: string; copy: string; action?: string; onAction?: () => void }) {
  return <div className="mt-7 rounded-2xl bg-[#fff3e9] p-5"><h3 className="text-sm font-extrabold">{title}</h3><p className="mt-2 text-xs font-medium leading-5 text-[#77776d]">{copy}</p>{action && <button className="mt-4 text-xs font-extrabold text-[#3559e0] underline underline-offset-4" onClick={onAction}>{action}</button>}</div>;
}
