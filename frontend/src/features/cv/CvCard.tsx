import { useState } from "react";
import { generateCv } from "../../shared/api/mockApi";
import { Icon } from "../../shared/components/AppShell";
import type { Job, Profile } from "../../shared/data/mockData";

export default function CvCard({ job, profile, onProfile }: { job: Job; profile: Profile | null; onProfile: () => void }) {
  const [state, setState] = useState<"idle" | "loading" | "failed" | "profile" | "cooldown" | "done">("idle");
  const [cooldown, setCooldown] = useState(false);
  const generate = async () => {
    if (cooldown) return setState("cooldown");
    if (!profile || profile.skills.length < 3) return setState("profile");
    setState("loading");
    try {
      const url = await generateCv(job, profile);
      window.open(url, "_blank", "noopener,noreferrer");
      setState("done");
      setCooldown(true);
      window.setTimeout(() => {
        setCooldown(false);
        setState((current) => current === "cooldown" ? "done" : current);
      }, 2200);
    } catch {
      setState("failed");
    }
  };
  return (
    <article className="rounded-[28px] border border-[#171714] bg-[#c8f04b] p-6 shadow-[6px_6px_0_#171714] md:p-8">
      <div className="flex items-start justify-between"><div><span className="text-xs font-extrabold uppercase tracking-[.16em]">Tailored CV</span><h2 className="mt-2 font-display text-3xl font-semibold">Make this role yours.</h2></div><span className="grid h-11 w-11 place-items-center rounded-full bg-white"><Icon name="download" /></span></div>
      <p className="mt-5 text-sm font-medium leading-6">Create a focused PDF using your profile and the language of this role.</p>
      {state === "loading" && <div className="mt-6 space-y-2 animate-pulse"><div className="h-3 w-full rounded bg-black/10" /><div className="h-3 w-2/3 rounded bg-black/10" /><p className="pt-2 text-xs font-bold">Writing and formatting your CV…</p></div>}
      {state === "failed" && <Message title="CV generation failed" copy="We could not create the PDF this time." action="Retry" onAction={generate} />}
      {state === "profile" && <Message title="Build your profile first" copy="Add at least 3 skills before generating a tailored CV." action="Go to Profile" onAction={onProfile} />}
      {state === "cooldown" && <Message title="Please wait a moment" copy="A CV was just requested. Try again shortly." />}
      {state === "done" && <Message title="Your CV opened in a new tab" copy="Review the PDF before sending your application." />}
      <button className="mt-7 w-full rounded-full bg-[#171714] px-5 py-3.5 text-sm font-extrabold text-white disabled:opacity-50" disabled={state === "loading" || cooldown} onClick={generate}>{state === "loading" ? "Generating…" : cooldown ? "Please wait a moment" : "Generate CV"}</button>
    </article>
  );
}

function Message({ title, copy, action, onAction }: { title: string; copy: string; action?: string; onAction?: () => void }) {
  return <div className="mt-6 rounded-2xl bg-white/60 p-4"><p className="text-sm font-extrabold">{title}</p><p className="mt-1 text-xs font-medium">{copy}</p>{action && <button className="mt-3 text-xs font-extrabold underline" onClick={onAction}>{action}</button>}</div>;
}
