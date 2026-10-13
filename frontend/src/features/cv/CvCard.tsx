import { useState } from "react";
import { Icon } from "../../shared/components/AppShell";
import type { Job, Profile } from "../../shared/types";
import type { CvPalette, CvTemplate } from "../../shared/api/cvApi";
import { useCv } from "./useCv";

const TEMPLATES: { id: CvTemplate; title: string; copy: string }[] = [
  { id: "plain", title: "Plain", copy: "Single column, ATS friendly" },
  { id: "colored", title: "Colored", copy: "Sidebar with color" },
];

const PALETTES: { id: CvPalette; label: string; color: string }[] = [
  { id: "dark_gray_blue", label: "Dark gray blue", color: "#3a4750" },
  { id: "frosted_mint", label: "Frosted mint", color: "#c2e9ff" },
  { id: "light_gray", label: "Light gray", color: "#d9d9d9" },
];

export default function CvCard({ job, profile, onProfile }: { job: Job; profile: Profile | null; onProfile: () => void }) {
  const { ready, phase, error, waiting, generate, open, style, setStyle } = useCv(job.id);
  const [needProfile, setNeedProfile] = useState(false);
  const loading = phase === "loading";
  const start = () => {
    if (loading || waiting) return;
    if (!profile || profile.skills.length < 3) return setNeedProfile(true);
    setNeedProfile(false);
    generate();
  };
  return (
    <article className="rounded-[28px] border border-[#171714] bg-[#c8f04b] p-6 shadow-[6px_6px_0_#171714] md:p-8">
      <div className="flex items-start justify-between"><div><span className="text-xs font-extrabold uppercase tracking-[.16em]">Tailored CV</span><h2 className="mt-2 font-display text-3xl font-semibold">Make this role yours.</h2></div><span className="grid h-11 w-11 place-items-center rounded-full bg-white"><Icon name="download" /></span></div>
      <p className="mt-5 text-sm font-medium leading-6">Create a focused PDF using your profile and the language of this role.</p>
      <div className="mt-5 grid grid-cols-2 gap-3">
        {TEMPLATES.map((item) => (
          <button key={item.id} type="button" aria-pressed={style.template === item.id} disabled={loading} onClick={() => setStyle({ ...style, template: item.id })} className={`rounded-2xl border border-[#171714] p-3 text-left disabled:opacity-50 ${style.template === item.id ? "bg-white shadow-[3px_3px_0_#171714]" : "bg-white/40"}`}>
            <span className="block text-sm font-extrabold">{item.title}</span>
            <span className="mt-1 block text-xs font-medium">{item.copy}</span>
          </button>
        ))}
      </div>
      {style.template === "colored" && (
        <div className="mt-4 flex items-center gap-3">
          <span className="text-xs font-extrabold uppercase tracking-[.16em]">Palette</span>
          {PALETTES.map((item) => (
            <button key={item.id} type="button" aria-label={item.label} title={item.label} aria-pressed={style.palette === item.id} disabled={loading} onClick={() => setStyle({ ...style, palette: item.id })} className={`h-8 w-8 rounded-full border border-[#171714] disabled:opacity-50 ${style.palette === item.id ? "ring-2 ring-[#171714] ring-offset-2 ring-offset-[#c8f04b]" : ""}`} style={{ backgroundColor: item.color }} />
          ))}
        </div>
      )}
      {loading && <div className="mt-6 space-y-2 animate-pulse"><div className="h-3 w-full rounded bg-black/10" /><div className="h-3 w-2/3 rounded bg-black/10" /><p className="pt-2 text-xs font-bold">Writing and formatting your CV…</p></div>}
      {!loading && needProfile && <Message title="Build your profile first" copy="Add at least 3 skills before generating a tailored CV." action="Go to Profile" onAction={onProfile} />}
      {!loading && !needProfile && phase === "failed" && <Message title="CV generation failed" copy="We could not create the PDF this time." action="Retry" onAction={start} />}
      {!loading && !needProfile && phase !== "failed" && ready && <Message title="Your CV is ready" copy="Review the PDF before sending your application." action="Open CV" onAction={open} />}
      {error && <p className="mt-4 text-xs font-bold text-[#c53f2b]">{error}</p>}
      <button className="mt-7 w-full rounded-full bg-[#171714] px-5 py-3.5 text-sm font-extrabold text-white disabled:opacity-50" disabled={loading || waiting} onClick={start}>{loading ? "Generating…" : waiting ? "Please wait a moment" : "Generate CV"}</button>
    </article>
  );
}

function Message({ title, copy, action, onAction }: { title: string; copy: string; action?: string; onAction?: () => void }) {
  return <div className="mt-6 rounded-2xl bg-white/60 p-4"><p className="text-sm font-extrabold">{title}</p><p className="mt-1 text-xs font-medium">{copy}</p>{action && <button className="mt-3 text-xs font-extrabold underline" onClick={onAction}>{action}</button>}</div>;
}
