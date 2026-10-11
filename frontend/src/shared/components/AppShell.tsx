import { useState, type ReactNode } from "react";
import { useAuth } from "../../features/auth/AuthContext";
import type { AppPage } from "../types";

export type IconName =
  | "search"
  | "plus"
  | "grid"
  | "briefcase"
  | "spark"
  | "user"
  | "arrow"
  | "sliders"
  | "more"
  | "edit"
  | "trash"
  | "back"
  | "check"
  | "link"
  | "calendar"
  | "location"
  | "download";

export function Icon({ name, className = "h-5 w-5" }: { name: IconName; className?: string }) {
  const paths: Record<IconName, ReactNode> = {
    search: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m15.5 15.5 4 4" /></>,
    plus: <path d="M12 5v14M5 12h14" />,
    grid: <><rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" /><rect x="4" y="14" width="6" height="6" rx="1" /><rect x="14" y="14" width="6" height="6" rx="1" /></>,
    briefcase: <><path d="M9 7V5.7c0-.9.7-1.7 1.7-1.7h2.6c1 0 1.7.8 1.7 1.7V7" /><rect x="3" y="7" width="18" height="13" rx="2.5" /><path d="M3 12.5c5.5 2 12.5 2 18 0M10 13h4" /></>,
    spark: <path d="M12 3c.6 5 4 8.4 9 9-5 .6-8.4 4-9 9-.6-5-4-8.4-9-9 5-.6 8.4-4 9-9Z" />,
    user: <><circle cx="12" cy="8" r="3.5" /><path d="M5 20c.7-4 3-6 7-6s6.3 2 7 6" /></>,
    arrow: <path d="M5 12h14m-5-5 5 5-5 5" />,
    sliders: <><path d="M4 7h16M4 17h16" /><circle cx="9" cy="7" r="2" fill="white" /><circle cx="15" cy="17" r="2" fill="white" /></>,
    more: <><circle cx="5" cy="12" r="1" fill="currentColor" /><circle cx="12" cy="12" r="1" fill="currentColor" /><circle cx="19" cy="12" r="1" fill="currentColor" /></>,
    edit: <><path d="m4 16-.7 4 4-.7L18.5 8.1l-3.3-3.3L4 16Z" /><path d="m13.7 6.3 3.3 3.3" /></>,
    trash: <><path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13" /><path d="M10 11v5M14 11v5" /></>,
    back: <path d="m15 5-7 7 7 7" />,
    check: <path d="m5 12 4 4L19 6" />,
    link: <><path d="m10 14 4-4" /><path d="M8.5 17.5 6 20a4 4 0 0 1-6-6l3-3a4 4 0 0 1 5.5 0M15.5 6.5 18 4a4 4 0 0 1 6 6l-3 3a4 4 0 0 1-5.5 0" /></>,
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M8 3v4M16 3v4M3 10h18" /></>,
    location: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
    download: <><path d="M12 3v12m-4-4 4 4 4-4" /><path d="M5 20h14" /></>,
  };
  return <svg aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">{paths[name]}</svg>;
}

const navItems: Array<{ page: AppPage; label: string; icon: IconName }> = [
  { page: "dashboard", label: "Dashboard", icon: "grid" },
  { page: "jobs", label: "Jobs", icon: "briefcase" },
  { page: "ask", label: "Ask your search", icon: "spark" },
  { page: "profile", label: "Profile", icon: "user" },
];

const initialsOf = (email: string) => {
  const name = email.split("@")[0].replace(/[^a-zA-Z0-9]+/g, " ").trim().split(" ");
  const letters = name.length > 1 ? name[0][0] + name[1][0] : name[0].slice(0, 2);
  return letters.toUpperCase();
};

export default function AppShell({
  page,
  navigate,
  onLanding,
  onExpire,
  children,
}: {
  page: AppPage;
  navigate: (page: AppPage) => void;
  onLanding: () => void;
  onExpire: () => void;
  children: ReactNode;
}) {
  const [accountOpen, setAccountOpen] = useState(false);
  const email = useAuth().email ?? "";
  const active = page.startsWith("job-") ? "jobs" : page;
  return (
    <main className="min-h-screen bg-[#f5f1e8] text-[#171714]">
      <header className="sticky top-0 z-40 border-b border-[#171714]/10 bg-[#fffaf0]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-[72px] max-w-[1500px] items-center justify-between px-5 lg:px-8">
          <button className="group flex items-center gap-2.5" onClick={onLanding}>
            <span className="relative grid h-9 w-9 place-items-center overflow-hidden rounded-full bg-[#171714] text-[#fffaf0]">
              <span className="font-display text-lg font-semibold">J</span>
              <span className="absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full bg-black" />
            </span>
            <span className="text-[15px] font-extrabold tracking-[-0.03em]">Job Tracker</span>
          </button>
          <div className="relative flex items-center gap-2">
            <button className="hidden h-10 items-center gap-2 rounded-full px-4 text-sm font-bold transition hover:bg-white sm:flex" onClick={() => navigate("ask")}>
              <span className="text-[#3559e0]"><Icon name="spark" className="h-4 w-4" /></span>
              Ask AI
            </button>
            <button className="grid h-10 w-10 place-items-center rounded-full bg-[#171714] text-xs font-extrabold text-white" onClick={() => setAccountOpen((open) => !open)}>{initialsOf(email) || "?"}</button>
            {accountOpen && (
              <div className="absolute right-0 top-12 w-56 rounded-2xl border border-[#171714]/10 bg-white p-2 shadow-[0_15px_45px_rgba(23,23,20,.15)]">
                <div className="border-b border-[#171714]/10 px-3 py-3">
                  <p className="truncate text-xs font-extrabold">{email}</p>
                </div>
                <button className="mt-1 w-full rounded-xl px-3 py-2.5 text-left text-xs font-bold text-[#a13922] hover:bg-[#fff0ec]" onClick={onExpire}>Sign out</button>
              </div>
            )}
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-[1500px]">
        <aside className="sticky top-[72px] hidden h-[calc(100vh-72px)] w-[230px] shrink-0 flex-col justify-between border-r border-[#171714]/10 bg-[#fffaf0] p-5 lg:flex">
          <nav className="space-y-1.5">
            {navItems.map((item) => (
              <button className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-bold transition ${active === item.page ? "bg-[#171714] text-white" : "text-[#6c6c63] hover:bg-[#f5f1e8] hover:text-[#171714]"}`} key={item.page} onClick={() => navigate(item.page)}>
                <Icon name={item.icon} />{item.label}
              </button>
            ))}
          </nav>
        </aside>
        <div className="min-w-0 flex-1">{children}</div>
      </div>
      <nav className="fixed bottom-3 left-3 right-3 z-40 flex justify-around rounded-2xl border border-[#171714]/10 bg-white/95 p-2 shadow-[0_12px_35px_rgba(23,23,20,.15)] backdrop-blur lg:hidden">
        {navItems.map((item) => (
          <button className={`flex min-w-14 flex-col items-center gap-1 rounded-xl px-2 py-2 text-[9px] font-extrabold ${active === item.page ? "bg-[#171714] text-white" : "text-[#77776d]"}`} key={item.page} onClick={() => navigate(item.page)}>
            <Icon name={item.icon} className="h-4 w-4" />{item.label.replace(" your search", "")}
          </button>
        ))}
      </nav>
    </main>
  );
}
