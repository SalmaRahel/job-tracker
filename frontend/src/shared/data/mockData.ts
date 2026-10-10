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
  workplace: "Remote" | "Hybrid" | "On-site";
  status: JobStatus;
  deadline: string;
  deadlineLabel: string;
  mark: string;
  color: string;
  applicationDate: string;
  link: string;
  description: string;
};

export const jobs: Job[] = [
  {
    id: 1,
    company: "Luma Labs",
    position: "Product Designer",
    location: "London, UK",
    workplace: "Hybrid",
    status: "Final Interview",
    deadline: "2025-04-24",
    deadlineLabel: "Apr 24",
    mark: "L",
    color: "bg-[#3559e0] text-white",
    applicationDate: "2025-03-28",
    link: "https://example.com/luma-product-designer",
    description: "Join Luma's product team to design thoughtful tools for creative teams. You will lead discovery, prototype new workflows, run usability tests and collaborate with engineering. We are looking for strong Figma skills, product thinking, research experience and familiarity with design systems.",
  },
  {
    id: 2,
    company: "Northstar",
    position: "UX Research Intern",
    location: "Remote",
    workplace: "Remote",
    status: "Interview",
    deadline: "2025-04-28",
    deadlineLabel: "Apr 28",
    mark: "N",
    color: "bg-[#ff6b4a] text-white",
    applicationDate: "2025-04-02",
    link: "https://example.com/northstar-ux-research",
    description: "Support qualitative research for a remote-first education platform. Plan interviews, synthesize insights and communicate findings. Experience with survey design and statistical analysis is useful.",
  },
  {
    id: 3,
    company: "Morrow",
    position: "Junior Product Manager",
    location: "Manchester, UK",
    workplace: "On-site",
    status: "Applied",
    deadline: "2025-05-03",
    deadlineLabel: "May 03",
    mark: "M",
    color: "bg-[#c8f04b] text-[#171714]",
    applicationDate: "2025-04-06",
    link: "https://example.com/morrow-product-manager",
    description: "Work with design and engineering to shape product priorities, write clear requirements and learn from customers. SQL knowledge and previous SaaS experience are preferred.",
  },
  {
    id: 4,
    company: "Patchwork",
    position: "Graduate Software Engineer",
    location: "Bristol, UK",
    workplace: "Hybrid",
    status: "Online Assessment",
    deadline: "2025-05-08",
    deadlineLabel: "May 08",
    mark: "P",
    color: "bg-[#f5b8d2] text-[#171714]",
    applicationDate: "2025-04-08",
    link: "https://example.com/patchwork-engineer",
    description: "Build accessible web products using React, TypeScript and modern testing practices. Familiarity with Node.js, PostgreSQL and cloud deployment is desirable.",
  },
  {
    id: 5,
    company: "Form & Field",
    position: "Brand Design Intern",
    location: "Remote",
    workplace: "Remote",
    status: "Saved",
    deadline: "2025-05-12",
    deadlineLabel: "May 12",
    mark: "F",
    color: "bg-[#171714] text-white",
    applicationDate: "",
    link: "https://example.com/form-field-intern",
    description: "",
  },
  {
    id: 6,
    company: "Brightside",
    position: "Marketing Associate",
    location: "Leeds, UK",
    workplace: "On-site",
    status: "Offer",
    deadline: "2025-05-16",
    deadlineLabel: "May 16",
    mark: "B",
    color: "bg-[#ff9f80] text-[#171714]",
    applicationDate: "2025-03-19",
    link: "https://example.com/brightside-marketing",
    description: "Help plan integrated campaigns, report on performance and coordinate creative work. Knowledge of HubSpot and paid social is a plus.",
  },
  {
    id: 7,
    company: "Common Ground",
    position: "Community Coordinator",
    location: "Edinburgh, UK",
    workplace: "Hybrid",
    status: "Rejected",
    deadline: "2025-04-18",
    deadlineLabel: "Apr 18",
    mark: "C",
    color: "bg-[#8da1ed] text-[#171714]",
    applicationDate: "2025-03-11",
    link: "https://example.com/common-ground-community",
    description: "Build relationships with community partners, organize events and track programme impact.",
  },
];

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

export type ProfileItem = Record<string, string> & { id: number };

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

export const profile: Profile = {
  personal: {
    fullName: "Alex Morgan",
    email: "alex.morgan@example.com",
    phone: "+44 7700 900 321",
    city: "London, UK",
  },
  skills: ["Figma", "User research", "Prototyping", "Design systems", "TypeScript"],
  experience: [
    {
      id: 1,
      title: "Product Design Intern",
      company: "Studio North",
      duration: "Jun 2024 – Sep 2024",
      description: "Designed and tested onboarding improvements for a collaborative planning tool.",
    },
  ],
  education: [
    {
      id: 1,
      school: "University of Bristol",
      degree: "BSc",
      field: "Digital Product Design",
      year: "2025",
    },
  ],
  projects: [
    {
      id: 1,
      name: "Campus Compass",
      description: "A mobile wayfinding concept tested with 18 students.",
      techStack: "Figma, React, Mapbox",
      link: "https://example.com/campus-compass",
    },
  ],
  certifications: [
    { id: 1, name: "UX Design Professional", issuer: "Google", year: "2024" },
  ],
  links: [
    { id: 1, label: "Portfolio", url: "https://example.com/alex" },
    { id: 2, label: "LinkedIn", url: "https://linkedin.com" },
  ],
};

export const exampleQuestions = [
  "Which remote jobs did I apply to?",
  "How many applications per status?",
  "Which deadlines are in the next 10 days?",
  "Which applications are still applied after 2 weeks?",
];

export const applicationsByMonth = [
  { month: "Nov", count: 3 },
  { month: "Dec", count: 5 },
  { month: "Jan", count: 4 },
  { month: "Feb", count: 7 },
  { month: "Mar", count: 11 },
  { month: "Apr", count: 8 },
];
