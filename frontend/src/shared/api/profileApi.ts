import { ApiError, apiFetch } from "./client";
import type { Profile, ProfileItem } from "../types";

export type Section = "experience" | "education" | "projects" | "certifications" | "links";
export type Skill = { id: number; name: string };

type ApiItem = Record<string, string | null>;
type ApiProfile = {
  full_name: string;
  email: string;
  phone: string | null;
  city: string | null;
} & Partial<Record<`${Section}_json`, ApiItem[] | null>>;

let nextId = 1;

const fromApiItem = (section: Section, raw: ApiItem): ProfileItem => {
  const { stack, ...rest } = raw;
  const item = section === "projects" ? { ...rest, techStack: stack } : rest;
  const values = Object.fromEntries(Object.entries(item).map(([key, value]) => [key, value ?? ""]));
  return { id: nextId++, ...values };
};

const toApiItem = (section: Section, item: ProfileItem) => {
  const { id, techStack, ...rest } = item;
  return section === "projects" ? { ...rest, stack: techStack || null, link: rest.link || null } : rest;
};

const toProfile = (api: ApiProfile): Profile => {
  const list = (section: Section) => (api[`${section}_json`] ?? []).map((raw) => fromApiItem(section, raw));
  return {
    personal: { fullName: api.full_name, email: api.email, phone: api.phone ?? "", city: api.city ?? "" },
    skills: [],
    experience: list("experience"),
    education: list("education"),
    projects: list("projects"),
    certifications: list("certifications"),
    links: list("links"),
  };
};

const personalBody = (personal: Profile["personal"]) => ({
  full_name: personal.fullName,
  email: personal.email,
  phone: personal.phone || null,
  city: personal.city || null,
});

const listBody = (section: Section, items: ProfileItem[]) => ({
  [`${section}_json`]: items.map((item) => toApiItem(section, item)),
});

export async function loadProfile() {
  try {
    const profile = toProfile(await apiFetch<ApiProfile>("/profile/"));
    const skills = await apiFetch<Skill[]>("/profile/skills");
    return { profile, skills };
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return { profile: null, skills: [] as Skill[] };
    throw err;
  }
}

export const createProfile = async (personal: Profile["personal"], section: Section, items: ProfileItem[]) =>
  toProfile(await apiFetch<ApiProfile>("/profile/", { method: "POST", body: { ...personalBody(personal), ...listBody(section, items) } }));

export const updatePersonal = async (personal: Profile["personal"]) =>
  toProfile(await apiFetch<ApiProfile>("/profile/", { method: "PUT", body: personalBody(personal) }));

export const updateSection = async (section: Section, items: ProfileItem[]) =>
  toProfile(await apiFetch<ApiProfile>("/profile/", { method: "PUT", body: listBody(section, items) }));

export const createSkill = (name: string) => apiFetch<Skill>("/profile/skills", { method: "POST", body: { name } });

export const deleteSkill = (id: number) => apiFetch<null>(`/profile/skills/${id}`, { method: "DELETE" });
