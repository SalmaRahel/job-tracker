import { useState, type FormEvent } from "react";
import { Icon } from "../../shared/components/AppShell";
import ConfirmDialog from "../../shared/components/ConfirmDialog";
import type { Section } from "../../shared/api/profileApi";
import type { Profile, ProfileItem } from "../../shared/types";
import type { ProfileStore } from "./useProfile";
import { emailError, isValidPhone } from "../../shared/validation";

const messageOf = (err: unknown) => (err instanceof Error ? err.message : "Something went wrong");

const schemas: Record<Section, Array<[string, string, string]>> = {
  experience: [["title", "Title", "Product Designer"], ["company", "Company", "Company name"], ["duration", "Duration", "Jun 2024 – Present"], ["description", "Description", "What did you do?"]],
  education: [["school", "School", "University"], ["degree", "Degree", "BSc"], ["field", "Field", "Product Design"], ["year", "Year", "2025"]],
  projects: [["name", "Project name", "Campus Compass"], ["description", "Description", "What did you build?"], ["techStack", "Tech stack", "Figma, React"], ["link", "Link (optional)", "https://..."]],
  certifications: [["name", "Certification", "UX Design Professional"], ["issuer", "Issuer", "Google"], ["year", "Year", "2024"]],
  links: [["label", "Label", "Portfolio"], ["url", "URL", "https://..."]],
};

const sectionMeta: Record<Section, { title: string; empty: string }> = {
  experience: { title: "Experience", empty: "No experience added yet." },
  education: { title: "Education", empty: "No education added yet." },
  projects: { title: "Projects", empty: "No projects added yet." },
  certifications: { title: "Certifications", empty: "No certifications added yet." },
  links: { title: "Links", empty: "No links added yet." },
};

export default function ProfilePage({ store }: { store: ProfileStore }) {
  const { profile } = store;
  const [modal, setModal] = useState<{ section: Section; item?: ProfileItem } | null>(null);
  const [skill, setSkill] = useState("");
  const [skillError, setSkillError] = useState("");
  const [editingPersonal, setEditingPersonal] = useState(false);
  const [pageError, setPageError] = useState("");
  const [pendingRemove, setPendingRemove] = useState<{ section: Section; id: number } | null>(null);
  const run = async (action: () => Promise<unknown>) => {
    setPageError("");
    try {
      await action();
    } catch (err) {
      setPageError(messageOf(err));
    }
  };
  if (store.loading) return <section className="px-5 pt-10 md:px-8 lg:px-10"><div className="mx-auto max-w-[1050px] animate-pulse space-y-4"><span className="block h-12 w-56 rounded bg-[#e9e5da]" /><span className="block h-40 rounded-[28px] bg-[#e9e5da]" /><span className="block h-48 rounded-[28px] bg-[#e9e5da]" /></div></section>;
  if (store.error && !profile) return <section className="grid min-h-[calc(100vh-72px)] place-items-center px-5 pb-24"><div className="text-center"><p className="text-sm font-bold text-[#c53f2b]">{store.error}</p><button className="mt-5 rounded-full bg-[#171714] px-6 py-3 text-sm font-bold text-white" onClick={store.reload}>Try again</button></div></section>;
  if (!profile) return <section className="grid min-h-[calc(100vh-72px)] place-items-center px-5 pb-24"><div className="max-w-md text-center"><span className="mx-auto grid h-20 w-20 place-items-center rounded-full bg-[#c8f04b]"><Icon name="user" /></span><h1 className="mt-6 font-display text-5xl font-semibold tracking-[-.05em]">Create my profile</h1><p className="mt-4 text-sm font-medium leading-6 text-[#707067]">Add your story once, then use it for match analysis and tailored CVs.</p><button className="mt-7 rounded-full bg-[#3559e0] px-6 py-3.5 text-sm font-extrabold text-white" onClick={store.startDraft}>Create my profile</button></div></section>;
  const updateSection = async (section: Section, item: ProfileItem) => {
    await store.saveItem(section, item);
    setModal(null);
  };
  const addSkill = async () => {
    const value = skill.trim();
    if (!value) return;
    try {
      await store.addSkill(value);
      setSkill("");
      setSkillError("");
    } catch (err) {
      setSkillError(messageOf(err));
    }
  };
  const progress = Math.min(profile.skills.length, 3);
  return (
    <section className="px-5 pb-28 pt-10 md:px-8 lg:px-10 lg:pt-14">
      <div className="mx-auto max-w-[1050px]">
        <div className="flex items-end justify-between gap-5"><div><p className="text-xs font-extrabold uppercase tracking-[.17em] text-[#ff6b4a]">The story behind your applications</p><h1 className="mt-3 font-display text-5xl font-semibold tracking-[-.055em] md:text-6xl">Profile</h1></div></div>{pageError && <p className="mt-4 text-xs font-bold text-[#c53f2b]">{pageError}</p>}
        <article className="mt-9 rounded-[28px] bg-[#3559e0] p-6 text-white md:p-8">
          {editingPersonal ? <PersonalForm personal={profile.personal} onCancel={() => setEditingPersonal(false)} onSave={(personal) => run(async () => { await store.savePersonal(personal); setEditingPersonal(false); })} /> : <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center"><div className="flex items-center gap-5"><span className="grid h-16 w-16 place-items-center rounded-full bg-[#f5b8d2] font-display text-2xl font-semibold text-[#171714]">{profile.personal.fullName ? profile.personal.fullName.split(" ").map((word) => word[0]).join("") : (profile.personal.email[0] ?? "?").toUpperCase()}</span><div><h2 className="font-display text-3xl font-semibold">{profile.personal.fullName || "Your name"}</h2><p className="mt-2 text-sm font-medium text-white/70">{[profile.personal.email, profile.personal.phone, profile.personal.city].filter(Boolean).join(" · ") || "Add your contact details"}</p></div></div><button className="flex w-fit items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-bold text-[#171714]" onClick={() => setEditingPersonal(true)}><Icon name="edit" className="h-4 w-4" />Edit details</button></div>}
        </article>
        <article className="mt-7 rounded-[28px] border border-[#171714]/10 bg-white p-6 md:p-8">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><h2 className="font-display text-3xl font-semibold">Skills</h2><p className="mt-2 text-xs font-bold text-[#77776d]">{profile.skills.length >= 3 ? "AI features unlocked" : `${3 - profile.skills.length} more needed for AI features`}</p></div><div className="flex gap-2">{[0, 1, 2].map((item) => <span className={`h-2.5 w-12 rounded-full ${item < progress ? "bg-[#c8f04b]" : "bg-[#e7e4dc]"}`} key={item} />)}</div></div>
          <div className="mt-6 flex flex-wrap gap-2">{profile.skills.map((item) => <span className="flex items-center gap-2 rounded-full bg-[#f5f1e8] px-4 py-2 text-xs font-bold" key={item}>{item}<button aria-label={`Remove ${item}`} className="text-base leading-none text-[#77776d]" onClick={() => run(() => store.removeSkill(item))}>×</button></span>)}</div>
          <div className="mt-5 flex max-w-md gap-2"><input className="min-w-0 flex-1 rounded-xl border border-[#171714]/15 px-4 py-3 text-sm font-semibold outline-none focus:border-[#3559e0]" placeholder="Add a skill" value={skill} onChange={(event) => { setSkill(event.target.value); setSkillError(""); }} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); addSkill(); } }} /><button className="rounded-xl bg-[#171714] px-4 text-sm font-bold text-white" onClick={addSkill}>Add</button></div>{skillError && <p className="mt-2 text-xs font-bold text-[#c53f2b]">{skillError}</p>}
        </article>
        <div className="mt-7 space-y-5">{(Object.keys(sectionMeta) as Section[]).map((section) => <ProfileSection items={profile[section] as ProfileItem[]} key={section} meta={sectionMeta[section]} onAdd={() => setModal({ section })} onEdit={(item) => setModal({ section, item })} onRemove={(id) => setPendingRemove({ section, id })} />)}</div>
      </div>
      {pendingRemove && <ConfirmDialog title="Remove this item?" text="It will be removed from your profile." confirmLabel="Remove" onCancel={() => setPendingRemove(null)} onConfirm={() => { run(() => store.removeItem(pendingRemove.section, pendingRemove.id)); setPendingRemove(null); }} />}
      {modal && <ItemModal section={modal.section} item={modal.item} onClose={() => setModal(null)} onSave={(item) => updateSection(modal.section, item)} />}
    </section>
  );
}

function ProfileSection({ items, meta, onAdd, onEdit, onRemove }: { items: ProfileItem[]; meta: { title: string; empty: string }; onAdd: () => void; onEdit: (item: ProfileItem) => void; onRemove: (id: number) => void }) {
  return <article className="rounded-[28px] border border-[#171714]/10 bg-[#fffaf0] p-6 md:p-8"><div className="flex items-center justify-between"><h2 className="font-display text-3xl font-semibold">{meta.title}</h2><button className="flex items-center gap-2 rounded-full border border-[#171714]/15 bg-white px-4 py-2.5 text-xs font-bold" onClick={onAdd}><Icon name="plus" className="h-4 w-4" />Add</button></div>{items.length ? <div className="mt-6 space-y-3">{items.map((item) => <div className="flex items-start justify-between gap-4 rounded-2xl bg-white p-5" key={item.id}><div><h3 className="text-sm font-extrabold">{item.title || item.name || item.school || item.label}</h3><p className="mt-1 text-xs font-bold text-[#77776d]">{item.company || item.degree || item.issuer || item.techStack || item.url}</p><p className="mt-2 text-xs font-medium leading-5 text-[#65655d]">{item.duration || item.description || item.field || item.year}</p></div><div className="flex gap-1"><button className="grid h-8 w-8 place-items-center rounded-full hover:bg-[#f5f1e8]" onClick={() => onEdit(item)}><Icon name="edit" className="h-4 w-4" /></button><button className="grid h-8 w-8 place-items-center rounded-full text-[#a13922] hover:bg-[#fff0ec]" onClick={() => onRemove(item.id)}><Icon name="trash" className="h-4 w-4" /></button></div></div>)}</div> : <p className="mt-6 rounded-2xl border border-dashed border-[#171714]/20 p-6 text-center text-sm font-medium text-[#77776d]">{meta.empty}</p>}</article>;
}

function ItemModal({ section, item, onClose, onSave }: { section: Section; item?: ProfileItem; onClose: () => void; onSave: (item: ProfileItem) => Promise<void> }) {
  const [form, setForm] = useState<Record<string, string>>(() => Object.fromEntries(schemas[section].map(([key]) => [key, String(item?.[key] ?? "")])));
  const [error, setError] = useState("");
  const submit = async (event: FormEvent) => { event.preventDefault(); if (!form[schemas[section][0][0]].trim()) return setError("Complete the first field to save this item."); if ((section === "links" || (section === "projects" && form.link)) && !/^https?:\/\//.test(form.url || form.link)) return setError("Use a complete URL starting with http:// or https://."); try { await onSave({ id: item?.id ?? Date.now(), ...form }); } catch (err) { setError(messageOf(err)); } };
  return <div className="fixed inset-0 z-50 grid place-items-end bg-[#171714]/25 p-3 backdrop-blur-sm sm:place-items-center" onMouseDown={onClose}><form className="w-full max-w-lg rounded-[28px] border border-[#171714] bg-[#fffaf0] p-6 shadow-[7px_7px_0_#171714]" onMouseDown={(event) => event.stopPropagation()} onSubmit={submit}><h2 className="font-display text-3xl font-semibold">{item ? "Edit" : "Add"} {sectionMeta[section].title.toLowerCase()}</h2><div className="mt-6 space-y-4">{schemas[section].map(([key, label, placeholder]) => <label className="block text-xs font-extrabold" key={key}>{label}{key === "description" ? <textarea className="mt-2 min-h-24 w-full rounded-xl border border-[#171714]/15 bg-white px-4 py-3 text-sm font-semibold outline-none" placeholder={placeholder} value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} /> : <input className="mt-2 w-full rounded-xl border border-[#171714]/15 bg-white px-4 py-3 text-sm font-semibold outline-none" placeholder={placeholder} value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} />}</label>)}</div>{error && <p className="mt-4 text-xs font-bold text-[#c53f2b]">{error}</p>}<div className="mt-6 flex justify-end gap-2"><button className="rounded-full px-5 py-3 text-sm font-bold" type="button" onClick={onClose}>Cancel</button><button className="rounded-full bg-[#3559e0] px-5 py-3 text-sm font-bold text-white">Save</button></div></form></div>;
}

function PersonalForm({ personal, onCancel, onSave }: { personal: Profile["personal"]; onCancel: () => void; onSave: (personal: Profile["personal"]) => void }) {
  const [form, setForm] = useState(personal);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const submit = (event: FormEvent) => {
    event.preventDefault();
    const next: Record<string, string> = {};
    const emailProblem = emailError(form.email);
    if (emailProblem) next.email = emailProblem;
    if (!isValidPhone(form.phone)) next.phone = "Enter a valid phone number";
    setErrors(next);
    if (Object.keys(next).length === 0) onSave({ ...form, email: form.email.trim(), phone: form.phone.trim() });
  };
  return <form onSubmit={submit}><div className="grid gap-4 sm:grid-cols-2">{([["fullName", "Full name"], ["email", "Email"], ["phone", "Phone"], ["city", "City"]] as const).map(([key, label]) => <label className="text-xs font-bold" key={key}>{label}<input className={`mt-2 w-full rounded-xl border bg-white/10 px-4 py-3 text-sm font-semibold text-white outline-none placeholder:text-white/40 ${errors[key] ? "border-[#ffb3a3]" : "border-white/20"}`} value={form[key]} onChange={(event) => { setForm({ ...form, [key]: event.target.value }); setErrors({ ...errors, [key]: "" }); }} />{errors[key] && <span className="mt-2 block text-xs font-bold text-[#ffb3a3]">{errors[key]}</span>}</label>)}</div><div className="mt-5 flex justify-end gap-2"><button className="rounded-full px-4 py-2 text-xs font-bold" type="button" onClick={onCancel}>Cancel</button><button className="rounded-full bg-white px-5 py-2.5 text-xs font-bold text-[#171714]">Save details</button></div></form>;
}
