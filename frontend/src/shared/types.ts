export type AppPage =
  | "dashboard"
  | "jobs"
  | "job-create"
  | "job-edit"
  | "job-detail"
  | "ask"
  | "profile"
  | "landing";

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
