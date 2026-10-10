import type { Job, Profile } from "../data/mockData";

const wait = (ms = 650) => new Promise((resolve) => window.setTimeout(resolve, ms));

export async function analyzeJob(job: Job, profile: Profile | null) {
  await wait(1100);
  if (!profile || profile.skills.length < 3) throw new Error("profile");
  if (!job.description) throw new Error("description");
  if (job.description.toLowerCase().includes("[fail]")) throw new Error("failed");
  const score = job.id === 4 ? 72 : 86 + (job.id % 9);
  return {
    score,
    missing: score >= 80 ? ["Advanced analytics", "B2B SaaS experience"] : ["SQL", "Cloud deployment", "Automated testing"],
  };
}

export async function generateCv(job: Job, profile: Profile | null) {
  await wait(1200);
  if (!profile || profile.skills.length < 3) throw new Error("profile");
  if (job.company.toLowerCase().includes("[fail]")) throw new Error("failed");
  const content = `%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj\n4 0 obj<</Length 55>>stream\nBT /F1 18 Tf 72 720 Td (${profile.personal.fullName} - ${job.position}) Tj ET\nendstream\nendobj\ntrailer<</Root 1 0 R>>\n%%EOF`;
  return URL.createObjectURL(new Blob([content], { type: "application/pdf" }));
}

export async function askJobSearch(question: string) {
  await wait(800);
  const lower = question.toLowerCase();
  if (lower.includes("salary") || lower.includes("other people")) throw new Error("scope");
  if (lower.includes("delete") || lower.includes("drop")) throw new Error("unsafe");
  if (lower.includes("complex")) throw new Error("timeout");
  if (lower.includes("offline")) throw new Error("network");
  if (lower.includes("remote")) return "You applied to Northstar’s UX Research Intern role. Form & Field is remote too, but it is still saved rather than applied.";
  if (lower.includes("status")) return "You have one application in each stage shown, with interviews currently your strongest active stage.";
  if (lower.includes("deadline")) return "Luma Labs and Northstar have the nearest upcoming deadlines. Luma is due first.";
  if (lower.includes("2 weeks")) return "Morrow’s Junior Product Manager application has remained at Applied for more than two weeks.";
  return "Your strongest momentum is in interview-stage roles. Luma Labs and Northstar are the best applications to focus on next.";
}
