import { useEffect, useState } from "react";
import LandingPage from "./features/auth/LandingPage";
import DashboardPage from "./features/dashboard/DashboardPage";
import AskPage from "./features/job_search_query/AskPage";
import JobDetailPage from "./features/jobs/JobDetailPage";
import JobFormPage from "./features/jobs/JobFormPage";
import JobsListPage from "./features/jobs/JobsListPage";
import ProfilePage from "./features/profile/ProfilePage";
import { useAuth } from "./features/auth/AuthContext";
import AppShell from "./shared/components/AppShell";
import { jobs as initialJobs, profile as initialProfile, type Job, type Profile } from "./shared/data/mockData";
import type { AppPage } from "./shared/types";

export default function App() {
  const { isLoggedIn, logout } = useAuth();
  const [page, setPage] = useState<AppPage>("dashboard");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [profile, setProfile] = useState<Profile | null>(initialProfile);
  const [selectedId, setSelectedId] = useState<number>(initialJobs[0].id);
  const [loading, setLoading] = useState(true);
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setJobs(initialJobs);
      setLoading(false);
    }, 450);
    return () => window.clearTimeout(timer);
  }, []);

  const navigate = (next: AppPage) => {
    setPage(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (!isLoggedIn || page === "landing") return <LandingPage onAuthenticated={() => navigate("jobs")} />;

  if (expired) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#fffaf0] px-5 text-[#171714]">
        <section className="w-full max-w-md rounded-[30px] border border-[#171714] bg-white p-8 text-center shadow-[8px_8px_0_#171714]">
          <span className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-[#f5b8d2] font-display text-2xl font-semibold">!</span>
          <h1 className="mt-6 font-display text-4xl font-semibold tracking-[-.045em]">Your session expired.</h1>
          <p className="mt-3 text-sm font-medium leading-6 text-[#707067]">For your security, please return to login and start a new session.</p>
          <button className="mt-7 w-full rounded-full bg-[#171714] px-6 py-3.5 text-sm font-extrabold text-white" onClick={() => { setExpired(false); setPage("landing"); }}>Return to login</button>
        </section>
      </main>
    );
  }

  const selectedJob = jobs.find((job) => job.id === selectedId);
  const saveJob = (job: Job) => {
    setJobs((current) => current.some((item) => item.id === job.id) ? current.map((item) => item.id === job.id ? job : item) : [job, ...current]);
    setSelectedId(job.id);
    navigate("job-detail");
  };
  const deleteJob = (id: number) => setJobs((current) => current.filter((job) => job.id !== id));

  let content;
  if (page === "dashboard") content = <DashboardPage jobs={jobs} onAdd={() => navigate("job-create")} />;
  else if (page === "jobs") content = <JobsListPage jobs={jobs} loading={loading} onAdd={() => navigate("job-create")} onOpen={(id) => { setSelectedId(id); navigate("job-detail"); }} onEdit={(id) => { setSelectedId(id); navigate("job-edit"); }} onDelete={deleteJob} />;
  else if (page === "job-create") content = <JobFormPage onCancel={() => navigate("jobs")} onSave={saveJob} />;
  else if (page === "job-edit" && selectedJob) content = <JobFormPage job={selectedJob} onCancel={() => navigate("job-detail")} onSave={saveJob} />;
  else if (page === "job-detail" && selectedJob) content = <JobDetailPage job={selectedJob} profile={profile} onBack={() => navigate("jobs")} onEdit={() => navigate("job-edit")} onProfile={() => navigate("profile")} onStatus={(status) => setJobs((current) => current.map((job) => job.id === selectedId ? { ...job, status } : job))} />;
  else if (page === "ask") content = <AskPage />;
  else if (page === "profile") content = <ProfilePage profile={profile} setProfile={setProfile} />;
  else content = <FriendlyError onBack={() => navigate("jobs")} />;

  return (
    <AppShell page={page} navigate={navigate} onLanding={() => navigate("landing")} onExpire={() => { logout(); setPage("landing"); }}>
      {content}
    </AppShell>
  );
}

function FriendlyError({ onBack }: { onBack: () => void }) {
  return (
    <section className="grid min-h-[calc(100vh-72px)] place-items-center px-5 pb-24">
      <div className="text-center">
        <span className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-[#ffddd4] font-display text-2xl font-semibold">!</span>
        <h1 className="mt-6 font-display text-4xl font-semibold">We lost that page.</h1>
        <p className="mt-3 text-sm font-medium text-[#707067]">The item may have been removed or is temporarily unavailable.</p>
        <button className="mt-6 rounded-full bg-[#171714] px-6 py-3 text-sm font-bold text-white" onClick={onBack}>Back to jobs</button>
      </div>
    </section>
  );
}
