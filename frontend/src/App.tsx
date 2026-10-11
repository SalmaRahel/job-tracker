import { useState } from "react";
import LandingPage from "./features/auth/LandingPage";
import DashboardPage from "./features/dashboard/DashboardPage";
import AskPage from "./features/job_search_query/AskPage";
import JobDetailPage from "./features/jobs/JobDetailPage";
import JobFormPage from "./features/jobs/JobFormPage";
import JobsListPage from "./features/jobs/JobsListPage";
import ProfilePage from "./features/profile/ProfilePage";
import { useAuth } from "./features/auth/AuthContext";
import { useJobs } from "./features/jobs/useJobs";
import { useProfile } from "./features/profile/useProfile";
import AppShell from "./shared/components/AppShell";
import { jobs as mockJobs, type Job } from "./shared/data/mockData";
import type { AppPage } from "./shared/types";

export default function App() {
  const { isLoggedIn, email, logout } = useAuth();
  const [page, setPage] = useState<AppPage>("dashboard");
  const store = useJobs(isLoggedIn);
  const profileStore = useProfile(isLoggedIn, email ?? "");
  const [expired, setExpired] = useState(false);

  const [notice, setNotice] = useState("");

  const attempt = async (action: () => Promise<unknown>) => {
    setNotice("");
    try {
      await action();
      return true;
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Something went wrong");
      return false;
    }
  };

  const navigate = (next: AppPage) => {
    setNotice("");
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

  const selectedJob = store.selected;
  const saveJob = async (job: Job) => {
    if (await attempt(() => store.save(job, page === "job-edit"))) navigate("job-detail");
  };
  const open = (id: number, next: AppPage) => {
    store.select(id);
    navigate(next);
  };

  let content;
  if (page === "dashboard") content = <DashboardPage jobs={mockJobs} onAdd={() => navigate("job-create")} />;
  else if (page === "jobs") content = <JobsListPage jobs={store.jobs} loading={store.loading} error={store.error} hasMore={store.hasMore} onSearch={store.setSearch} onLoadMore={store.loadMore} onAdd={() => navigate("job-create")} onOpen={(id) => open(id, "job-detail")} onEdit={(id) => open(id, "job-edit")} onDelete={(id) => attempt(() => store.remove(id))} />;
  else if (page === "job-create") content = <JobFormPage onCancel={() => navigate("jobs")} onSave={saveJob} />;
  else if ((page === "job-edit" || page === "job-detail") && store.selecting) content = <JobSkeleton />;
  else if (page === "job-edit" && selectedJob) content = <JobFormPage job={selectedJob} onCancel={() => navigate("job-detail")} onSave={saveJob} />;
  else if (page === "job-detail" && selectedJob) content = <JobDetailPage job={selectedJob} profile={profileStore.profile} onBack={() => navigate("jobs")} onEdit={() => navigate("job-edit")} onProfile={() => navigate("profile")} onStatus={(status) => attempt(() => store.setStatus(selectedJob.id, status))} />;
  else if (page === "ask") content = <AskPage />;
  else if (page === "profile") content = <ProfilePage store={profileStore} />;
  else content = <FriendlyError onBack={() => navigate("jobs")} />;

  return (
    <AppShell page={page} navigate={navigate} onLanding={() => navigate("landing")} onExpire={() => { logout(); setPage("landing"); }}>
      {notice && (
        <div className="mx-auto flex max-w-[1160px] items-center justify-between gap-4 px-5 pt-5 md:px-8 lg:px-10">
          <p className="text-sm font-bold text-[#c53f2b]">{notice}</p>
          <button className="shrink-0 text-xs font-bold text-[#77776d]" onClick={() => setNotice("")}>Dismiss</button>
        </div>
      )}
      {content}
    </AppShell>
  );
}

function JobSkeleton() {
  return (
    <section className="px-5 pt-10 md:px-8 lg:px-10">
      <div className="mx-auto max-w-[900px] animate-pulse space-y-4">
        <span className="block h-4 w-32 rounded bg-[#e9e5da]" />
        <span className="block h-12 w-72 rounded bg-[#e9e5da]" />
        <span className="block h-64 rounded-[28px] bg-[#e9e5da]" />
      </div>
    </section>
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
