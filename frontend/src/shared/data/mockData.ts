export const pipelineSteps = [
  { label: "Saved", count: 12, color: "bg-[#f5b8d2]" },
  { label: "Applied", count: 8, color: "bg-[#ff6b4a]" },
  { label: "Interview", count: 3, color: "bg-[#3559e0]" },
  { label: "Offer", count: 1, color: "bg-[#c8f04b]" },
];

export const landingJobs = [
  {
    company: "Luma",
    role: "Product Designer",
    location: "Remote",
    match: 94,
    mark: "L",
    markClass: "bg-[#3559e0] text-white",
  },
  {
    company: "Northstar",
    role: "UX Research Intern",
    location: "London",
    match: 87,
    mark: "N",
    markClass: "bg-[#ff6b4a] text-white",
  },
];

export const landingFeatures = [
  {
    number: "01",
    title: "See the whole search",
    copy: "Every application, deadline and next step in one calm, visual pipeline.",
    accent: "bg-[#ff6b4a]",
  },
  {
    number: "02",
    title: "Know your match",
    copy: "Paste any role. Get a clear match score and the gaps worth working on.",
    accent: "bg-[#3559e0]",
  },
  {
    number: "03",
    title: "Tailor in a click",
    copy: "Turn your profile into a focused CV shaped around the job you want.",
    accent: "bg-[#c8f04b]",
  },
  {
    number: "04",
    title: "Ask your own data",
    copy: "Ask natural questions and get useful answers about your job search.",
    accent: "bg-[#f5b8d2]",
  },
];

export const floatingQuestions = [
  "Which remote roles did I apply to?",
  "What should I follow up this week?",
  "Where am I getting the most interviews?",
];

export type JobStatus =
  | "Saved"
  | "Applied"
  | "Online Assessment"
  | "Interview"
  | "Final Interview"
  | "Offer"
  | "Rejected"
  | "Withdrawn";

export type Job = {
  id: number;
  company: string;
  position: string;
  location: string;
  status: JobStatus;
  deadline: string;
  deadlineLabel: string;
  mark: string;
  color: string;
  applicationDate: string;
  link: string;
  description: string;
};

export const jobStatuses: JobStatus[] = [
  "Saved",
  "Applied",
  "Online Assessment",
  "Interview",
  "Final Interview",
  "Offer",
  "Rejected",
  "Withdrawn",
];

export type ProfileItem = { id: number; [key: string]: string | number };

export type Profile = {
  personal: {
    fullName: string;
    email: string;
    phone: string;
    city: string;
  };
  skills: string[];
  experience: ProfileItem[];
  education: ProfileItem[];
  projects: ProfileItem[];
  certifications: ProfileItem[];
  links: ProfileItem[];
};

export const exampleQuestions = [
  "Which remote jobs did I apply to?",
  "How many applications per status?",
  "Which deadlines are in the next 10 days?",
  "Which applications are still applied after 2 weeks?",
];
