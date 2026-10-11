import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "./AuthContext";
import { emailError } from "../../shared/validation";
import {
  floatingQuestions,
  landingFeatures,
  landingJobs,
  pipelineSteps,
} from "../../shared/data/mockData";

type AuthMode = "login" | "register" | null;

function ArrowIcon({ diagonal = false }: { diagonal?: boolean }) {
  return (
    <svg
      aria-hidden="true"
      className="h-4 w-4"
      viewBox="0 0 20 20"
      fill="none"
    >
      <path
        d={diagonal ? "M5 15 15 5m0 0H7m8 0v8" : "M4 10h12m-4-4 4 4-4 4"}
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function SparkIcon() {
  return (
    <svg aria-hidden="true" className="h-5 w-5" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 2c.7 5.5 4.5 9.3 10 10-5.5.7-9.3 4.5-10 10-.7-5.5-4.5-9.3-10-10 5.5-.7 9.3-4.5 10-10Z"
        fill="currentColor"
      />
    </svg>
  );
}

function Logo({ blackDot = false }: { blackDot?: boolean }) {
  return (
    <a className="group flex items-center gap-2.5" href="#top" aria-label="Job Tracker home">
      <span className="relative grid h-9 w-9 place-items-center overflow-hidden rounded-full bg-[#171714] text-[#fffaf0]">
        <span className="font-display text-lg font-semibold">J</span>
        <span
          className={`absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full transition-transform duration-300 group-hover:scale-150 ${
            blackDot ? "bg-black" : "bg-[#ff6b4a]"
          }`}
        />
      </span>
      <span className="text-[15px] font-extrabold tracking-[-0.03em]">Job Tracker</span>
    </a>
  );
}

function AuthDialog({
  mode,
  onClose,
  onModeChange,
  onAuthenticated,
}: {
  mode: Exclude<AuthMode, null>;
  onClose: () => void;
  onModeChange: (mode: Exclude<AuthMode, null>) => void;
  onAuthenticated: () => void;
}) {
  const { login, register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
  }, [mode]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const emailProblem = mode === "register" ? emailError(email) : null;
    if (emailProblem) return setError(emailProblem);
    setLoading(true);
    setError("");
    try {
      await (mode === "login" ? login : register)(email, password);
      onAuthenticated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-[#171714]/30 p-3 backdrop-blur-sm sm:items-center"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        aria-modal="true"
        aria-labelledby="auth-title"
        className="relative w-full max-w-[440px] rounded-[28px] border border-[#171714] bg-[#fffaf0] p-6 shadow-[8px_8px_0_#171714] sm:p-8"
        role="dialog"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button
          aria-label="Close"
          className="absolute right-5 top-5 grid h-9 w-9 place-items-center rounded-full border border-[#171714]/20 text-xl transition hover:rotate-6 hover:bg-white"
          onClick={onClose}
        >
          ×
        </button>
        <div className="mb-7 inline-flex rounded-full border border-[#171714] bg-white p-1 text-sm font-bold">
          <button
            className={`rounded-full px-4 py-2 transition ${mode === "login" ? "bg-[#171714] text-white" : ""}`}
            onClick={() => onModeChange("login")}
          >
            Login
          </button>
          <button
            className={`rounded-full px-4 py-2 transition ${mode === "register" ? "bg-[#171714] text-white" : ""}`}
            onClick={() => onModeChange("register")}
          >
            Register
          </button>
        </div>
          <>
            <p className="mb-2 text-xs font-extrabold uppercase tracking-[0.18em] text-[#ff6b4a]">
              {mode === "login" ? "Welcome back" : "Start your search"}
            </p>
            <h2
              id="auth-title"
              className="font-display text-4xl font-semibold tracking-[-0.04em]"
            >
              {mode === "login" ? "Pick up where you left off." : "Make every application count."}
            </h2>
            <form
              className="mt-7 space-y-4"
              onSubmit={submit}
            >
              <label className="block text-sm font-bold">
                Email
                <input
                  className="mt-2 w-full rounded-2xl border border-[#171714]/20 bg-white px-4 py-3.5 font-medium outline-none transition focus:border-[#3559e0] focus:ring-4 focus:ring-[#3559e0]/10"
                  placeholder="you@example.com"
                  required
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                />
              </label>
              <label className="block text-sm font-bold">
                Password
                <input
                  className="mt-2 w-full rounded-2xl border border-[#171714]/20 bg-white px-4 py-3.5 font-medium outline-none transition focus:border-[#3559e0] focus:ring-4 focus:ring-[#3559e0]/10"
                  placeholder="At least 8 characters"
                  required
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
              </label>
              {error && <p className="text-sm font-bold text-[#c53f2b]">{error}</p>}
              <button
                className="group flex w-full items-center justify-center gap-2 rounded-full bg-[#3559e0] px-5 py-4 font-extrabold text-white transition hover:bg-[#2444c4] disabled:opacity-60"
                disabled={loading}
              >
                {loading ? "Please wait..." : mode === "login" ? "Login to your workspace" : "Create my free account"}
                <span className="transition-transform group-hover:translate-x-1">
                  <ArrowIcon />
                </span>
              </button>
            </form>
          </>

      </section>
    </div>
  );
}

export default function LandingPage({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [authMode, setAuthMode] = useState<AuthMode>(null);
  const [questionIndex, setQuestionIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setQuestionIndex((current) => (current + 1) % floatingQuestions.length);
    }, 2800);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <main id="top" className="overflow-hidden bg-[#fffaf0] text-[#171714]">
      <nav className="relative z-30 mx-auto flex max-w-[1440px] items-center justify-between px-5 py-5 md:px-10 lg:px-16">
        <Logo blackDot />
        <div className="hidden items-center gap-8 text-sm font-bold md:flex">
          <a className="nav-link" href="#features">
            Features
          </a>
          <a className="nav-link" href="#how-it-works">
            How it works
          </a>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="rounded-full px-4 py-2.5 text-sm font-extrabold transition hover:bg-white"
            onClick={() => setAuthMode("login")}
          >
            Login
          </button>
          <button
            className="group flex items-center gap-2 rounded-full bg-[#171714] px-4 py-2.5 text-sm font-extrabold text-white transition hover:-translate-y-0.5 hover:shadow-[0_5px_0_#ff6b4a]"
            onClick={() => setAuthMode("register")}
          >
            Try it free
            <ArrowIcon diagonal />
          </button>
        </div>
      </nav>

      <section className="relative mx-auto min-h-[790px] max-w-[1440px] px-5 pb-24 pt-12 md:px-10 md:pt-20 lg:grid lg:min-h-[850px] lg:grid-cols-[1.05fr_.95fr] lg:items-center lg:px-16 lg:pb-28 lg:pt-8">
        <div className="relative z-20 max-w-[740px]">
          <div className="reveal-up mb-7 inline-flex items-center gap-2 rounded-full border border-[#171714]/15 bg-white px-3 py-2 text-xs font-extrabold uppercase tracking-[0.13em] shadow-[0_3px_0_rgba(23,23,20,.1)]">
            <span className="text-[#ff6b4a]">
              <SparkIcon />
            </span>
            Your job search, finally in motion
          </div>
          <h1 className="reveal-up delay-1 font-display text-[clamp(4.15rem,9vw,8.7rem)] font-semibold leading-[0.78] tracking-[-0.075em]">
            Less chaos.
            <span className="relative mt-2 block w-fit text-[#3559e0]">
              More offers.
              <svg
                aria-hidden="true"
                className="absolute -bottom-5 left-1 w-[96%] text-[#ff6b4a]"
                viewBox="0 0 520 28"
                fill="none"
              >
                <path
                  d="M4 18C128 3 351 4 516 11"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeWidth="8"
                />
              </svg>
            </span>
          </h1>
          <p className="reveal-up delay-2 mt-12 max-w-[570px] text-lg font-medium leading-8 text-[#5f5f55] md:text-xl">
            Track every application, see how well you match, and shape a better CV for
            every role. One smart workspace for your next move.
          </p>
          <div className="reveal-up delay-3 mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              className="group flex items-center justify-center gap-3 rounded-full bg-[#ff6b4a] px-7 py-4 font-extrabold text-white transition hover:-translate-y-1 hover:shadow-[0_7px_0_#171714]"
              onClick={() => setAuthMode("register")}
            >
              Start tracking for free
              <span className="transition-transform group-hover:translate-x-1">
                <ArrowIcon />
              </span>
            </button>
            <a
              className="flex items-center justify-center gap-2 rounded-full border border-[#171714]/20 bg-white px-7 py-4 font-extrabold transition hover:border-[#171714]"
              href="#how-it-works"
            >
              See how it works
              <ArrowIcon diagonal />
            </a>
          </div>
          <div className="reveal-up delay-4 mt-9 flex items-center gap-4 text-xs font-bold text-[#707067]">
            Built for ambitious job seekers,
            <br />
            not spreadsheet enthusiasts.
          </div>
        </div>

        <div className="relative z-10 mt-20 h-[490px] lg:mt-0 lg:h-[650px]">
          <div className="absolute left-1/2 top-1/2 h-[430px] w-[430px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#f5b8d2] md:h-[550px] md:w-[550px]" />
          <div className="float-card absolute left-[2%] top-[-4%] z-20 hidden rotate-[-7deg] rounded-2xl border border-[#171714] bg-[#c8f04b] px-5 py-4 shadow-[5px_5px_0_#171714] sm:block lg:left-[-4%] lg:top-[-1%]">
            <p className="text-[10px] font-extrabold uppercase tracking-[0.16em]">AI match</p>
            <p className="mt-1 font-display text-4xl font-semibold">94%</p>
            <p className="text-xs font-bold">Strong fit</p>
          </div>
          <div className="float-card-delayed absolute bottom-[2%] right-[0%] z-20 max-w-[240px] rotate-[5deg] rounded-2xl border border-[#171714] bg-white p-4 shadow-[5px_5px_0_#171714] md:right-[3%] lg:bottom-[9%]">
            <div className="mb-3 flex items-center gap-2 text-[#3559e0]">
              <SparkIcon />
              <span className="text-[10px] font-extrabold uppercase tracking-[0.16em]">
                Ask your search
              </span>
            </div>
            <p className="min-h-10 text-sm font-bold leading-5" key={questionIndex}>
              “{floatingQuestions[questionIndex]}”
            </p>
          </div>
          <div className="absolute left-1/2 top-1/2 z-10 w-[91%] max-w-[520px] -translate-x-1/2 -translate-y-1/2 rotate-[2deg] rounded-[30px] border border-[#171714] bg-white p-4 shadow-[9px_11px_0_#171714] md:p-6">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-[#77776d]">
                  Today
                </p>
                <h2 className="font-display text-3xl font-semibold tracking-[-0.04em]">
                  Your search
                </h2>
              </div>
              <span className="grid h-10 w-10 place-items-center rounded-full bg-[#171714] text-xs font-bold text-white">
                AM
              </span>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {pipelineSteps.map((step) => (
                <div className={`${step.color} rounded-2xl p-3`} key={step.label}>
                  <p className="font-display text-2xl font-semibold">{step.count}</p>
                  <p className="mt-1 truncate text-[9px] font-extrabold uppercase tracking-[0.08em]">
                    {step.label}
                  </p>
                </div>
              ))}
            </div>
            <div className="mt-6 flex items-center justify-between">
              <h3 className="text-sm font-extrabold">Move these forward</h3>
              <span className="text-[10px] font-bold text-[#77776d]">2 active roles</span>
            </div>
            <div className="mt-3 space-y-2">
              {landingJobs.map((job) => (
                <div
                  className="group flex items-center gap-3 rounded-2xl border border-[#171714]/10 bg-[#fffaf0] p-3 transition hover:-translate-y-0.5 hover:border-[#171714]/30"
                  key={job.company}
                >
                  <span
                    className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl font-display text-lg font-semibold ${job.markClass}`}
                  >
                    {job.mark}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-extrabold">{job.role}</p>
                    <p className="mt-0.5 text-[10px] font-medium text-[#77776d]">
                      {job.company} · {job.location}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-extrabold text-[#3559e0]">{job.match}%</p>
                    <p className="text-[9px] font-bold text-[#77776d]">match</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 rounded-2xl bg-[#171714] p-4 text-white">
              <div className="flex items-center justify-between text-xs font-bold">
                <span>Applications this month</span>
                <span className="text-[#c8f04b]">+32%</span>
              </div>
              <div className="mt-4 flex h-12 items-end gap-2">
                {[34, 48, 31, 66, 54, 88, 72, 100].map((height, index) => (
                  <span
                    className={`flex-1 rounded-t-sm ${index === 7 ? "bg-[#c8f04b]" : "bg-white/25"}`}
                    key={index}
                    style={{ height: `${height}%` }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        className="border-y border-[#171714] bg-[#171714] py-4 text-[#fffaf0]"
        aria-label="Product benefits"
      >
        <div className="marquee flex w-max items-center gap-8 whitespace-nowrap text-sm font-extrabold uppercase tracking-[0.16em]">
          {[0, 1].map((copy) => (
            <div className="flex items-center gap-8" key={copy}>
              <span>Track every move</span>
              <span className="text-[#ff6b4a]">✦</span>
              <span>Match with confidence</span>
              <span className="text-[#c8f04b]">✦</span>
              <span>Tailor every CV</span>
              <span className="text-[#f5b8d2]">✦</span>
              <span>Ask better questions</span>
              <span className="text-[#3559e0]">✦</span>
            </div>
          ))}
        </div>
      </section>

      <section id="features" className="mx-auto max-w-[1440px] px-5 py-24 md:px-10 md:py-32 lg:px-16">
        <div className="grid gap-10 lg:grid-cols-[.7fr_1.3fr] lg:gap-20">
          <div>
            <p className="eyebrow">Everything you need</p>
            <h2 className="mt-5 max-w-md font-display text-5xl font-semibold leading-[0.95] tracking-[-0.055em] md:text-7xl">
              A smarter way to get hired.
            </h2>
            <p className="mt-7 max-w-sm text-base font-medium leading-7 text-[#66665c]">
              Job Tracker keeps the practical parts organized and uses AI only where it
              genuinely helps.
            </p>
          </div>
          <div className="grid gap-px overflow-hidden rounded-[30px] border border-[#171714] bg-[#171714] sm:grid-cols-2">
            {landingFeatures.map((feature) => (
              <article
                className="group relative min-h-[280px] bg-[#fffaf0] p-7 transition-colors hover:bg-white md:p-9"
                key={feature.number}
              >
                <div className="flex items-start justify-between">
                  <span className="text-xs font-extrabold tracking-[0.18em] text-[#77776d]">
                    / {feature.number}
                  </span>
                  <span
                    className={`grid h-11 w-11 place-items-center rounded-full ${feature.accent} transition-transform duration-300 group-hover:rotate-45`}
                  >
                    <ArrowIcon diagonal />
                  </span>
                </div>
                <h3 className="mt-16 font-display text-3xl font-semibold tracking-[-0.035em]">
                  {feature.title}
                </h3>
                <p className="mt-3 max-w-xs text-sm font-medium leading-6 text-[#66665c]">
                  {feature.copy}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="bg-[rgba(64,111,11,0.698)] px-5 py-24 text-white md:px-10 md:py-32 lg:px-16">
        <div className="mx-auto max-w-[1312px]">
          <div className="flex flex-col justify-between gap-8 border-b border-white/30 pb-10 md:flex-row md:items-end">
            <div>
              <p className="text-xs font-extrabold uppercase tracking-[0.2em] text-[#c8f04b]">
                From scattered to strategic
              </p>
              <h2 className="mt-5 max-w-3xl font-display text-5xl font-semibold leading-[0.95] tracking-[-0.055em] md:text-7xl">
                Your next move,
                <br />
                made clearer.
              </h2>
            </div>
            <button
              className="group flex w-fit items-center gap-3 rounded-full bg-[#c8f04b] px-6 py-4 font-extrabold text-[#171714] transition hover:-translate-y-1 hover:shadow-[0_6px_0_#171714]"
              onClick={() => setAuthMode("register")}
            >
              Build your workspace
              <ArrowIcon />
            </button>
          </div>
          <div className="grid gap-8 pt-10 md:grid-cols-3">
            {[
              ["01", "Build your profile", "Add your skills, experience and projects once."],
              ["02", "Save every role", "Keep details, deadlines and progress together."],
              ["03", "Apply with insight", "Check your fit, fill the gaps and tailor your CV."],
            ].map(([number, title, copy]) => (
              <article className="border-l border-white/30 pl-6" key={number}>
                <span className="font-display text-5xl font-semibold text-[#f5b8d2]">{number}</span>
                <h3 className="mt-10 text-xl font-extrabold">{title}</h3>
                <p className="mt-3 max-w-xs text-sm font-medium leading-6 text-white/70">{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <footer className="bg-[#fffaf0] px-5 py-8 md:px-10 lg:px-16">
        <div className="mx-auto flex max-w-[1312px] flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <Logo />
          <p className="text-xs font-bold text-[#77776d]">
            Your search has a lot of moving parts. Now they move together.
          </p>
          <button
            className="w-fit text-sm font-extrabold underline decoration-[#ff6b4a] decoration-2 underline-offset-4"
            onClick={() => setAuthMode("register")}
          >
            Get started
          </button>
        </div>
      </footer>

      {authMode && (
        <AuthDialog
          mode={authMode}
          onClose={() => setAuthMode(null)}
          onModeChange={setAuthMode}
          onAuthenticated={onAuthenticated}
        />
      )}
    </main>
  );
}
