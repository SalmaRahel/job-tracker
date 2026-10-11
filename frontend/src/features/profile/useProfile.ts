import { useEffect, useState } from "react";
import * as profileApi from "../../shared/api/profileApi";
import type { Section, Skill } from "../../shared/api/profileApi";
import type { Profile, ProfileItem } from "../../shared/data/mockData";

const CORE: Section[] = ["experience", "education", "projects"];
const NEED_FIRST = "Add an experience, education or project first to create your profile.";
const NEED_NAME = "Add your full name in Edit details first.";

export function useProfile(enabled: boolean, email: string) {
  const [saved, setSaved] = useState<Profile | null>(null);
  const [draft, setDraft] = useState<Profile | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setSaved(null);
      setDraft(null);
      setSkills([]);
      return;
    }
    let current = true;
    setLoading(true);
    setError("");
    profileApi
      .loadProfile()
      .then((result) => {
        if (!current) return;
        setSaved(result.profile);
        setSkills(result.skills);
      })
      .catch((err) => current && setError(err instanceof Error ? err.message : "Something went wrong"))
      .finally(() => current && setLoading(false));
    return () => {
      current = false;
    };
  }, [enabled, attempt]);

  const base = saved ?? draft;
  const profile = base && { ...base, skills: skills.map((skill) => skill.name) };

  const startDraft = () =>
    setDraft({ personal: { fullName: "", email, phone: "", city: "" }, skills: [], experience: [], education: [], projects: [], certifications: [], links: [] });

  const savePersonal = async (personal: Profile["personal"]) => {
    if (saved) setSaved(await profileApi.updatePersonal(personal));
    else setDraft((current) => current && { ...current, personal });
  };

  const saveItem = async (section: Section, item: ProfileItem) => {
    if (!base) return;
    if (!saved) {
      if (!CORE.includes(section)) throw new Error(NEED_FIRST);
      if (!base.personal.fullName.trim()) throw new Error(NEED_NAME);
      return setSaved(await profileApi.createProfile(base.personal, section, [item]));
    }
    const list = saved[section] as ProfileItem[];
    const next = list.some((entry) => entry.id === item.id) ? list.map((entry) => (entry.id === item.id ? item : entry)) : [...list, item];
    setSaved(await profileApi.updateSection(section, next));
  };

  const removeItem = async (section: Section, id: number) => {
    if (!saved) return;
    const next = (saved[section] as ProfileItem[]).filter((item) => item.id !== id);
    setSaved(await profileApi.updateSection(section, next));
  };

  const addSkill = async (name: string) => {
    if (!saved) throw new Error(NEED_FIRST);
    const skill = await profileApi.createSkill(name);
    setSkills((current) => [...current, skill]);
  };

  const removeSkill = async (name: string) => {
    const skill = skills.find((item) => item.name === name);
    if (!skill) return;
    await profileApi.deleteSkill(skill.id);
    setSkills((current) => current.filter((item) => item.id !== skill.id));
  };

  const reload = () => setAttempt((count) => count + 1);

  return { profile, loading, error, reload, startDraft, savePersonal, saveItem, removeItem, addSkill, removeSkill };
}

export type ProfileStore = ReturnType<typeof useProfile>;
