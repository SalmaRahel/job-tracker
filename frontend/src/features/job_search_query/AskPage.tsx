import { useState, type FormEvent } from "react";
import { askJobSearch } from "../../shared/api/mockApi";
import { Icon } from "../../shared/components/AppShell";
import { exampleQuestions } from "../../shared/data/mockData";

type HistoryItem = { question: string; answer: string };

const errors: Record<string, string> = {
  scope: "I can only answer questions about your own job applications.",
  unsafe: "I could not turn that into a safe query. Try rephrasing.",
  timeout: "That question took too long. Try something simpler.",
  network: "I could not reach the assistant. Please try again.",
  cooldown: "Please wait a moment before asking another question.",
};

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(false);
  const submit = async (event?: FormEvent, selected?: string) => {
    event?.preventDefault();
    const value = (selected ?? question).trim();
    if (!value || loading) return;
    if (cooldown) return setError(errors.cooldown);
    setQuestion(value);
    setError("");
    setAnswer("");
    setLoading(true);
    try {
      const response = await askJobSearch(value);
      setAnswer(response);
      setHistory((items) => [{ question: value, answer: response }, ...items].slice(0, 4));
      setQuestion("");
      setCooldown(true);
      window.setTimeout(() => setCooldown(false), 1800);
    } catch (reason) {
      const code = reason instanceof Error ? reason.message : "network";
      setError(errors[code] ?? errors.network);
    } finally {
      setLoading(false);
    }
  };
  return (
    <section className="px-5 pb-28 pt-10 md:px-8 lg:px-10 lg:pt-14">
      <div className="mx-auto max-w-[960px]">
        <p className="text-xs font-extrabold uppercase tracking-[.17em] text-[#ff6b4a]">Your applications know the answer</p>
        <h1 className="mt-3 max-w-3xl font-display text-5xl font-semibold leading-[.95] tracking-[-.055em] md:text-6xl">Ask your job search.</h1>
        <p className="mt-4 max-w-xl text-sm font-medium leading-6 text-[#707067]">Use plain English to find patterns, deadlines and next steps across your own applications.</p>
        <form className="mt-10 rounded-[28px] border border-[#171714] bg-white p-4 shadow-[7px_7px_0_#171714] md:p-6" onSubmit={(event) => submit(event)}>
          <textarea className="min-h-32 w-full resize-none bg-transparent p-2 text-lg font-semibold leading-7 outline-none placeholder:text-[#aaa9a0]" maxLength={500} placeholder="What would you like to know?" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <div className="mt-3 flex items-center justify-between border-t border-[#171714]/10 pt-4"><span className="text-xs font-bold text-[#8a8a80]">{question.length} / 500</span><button className="flex items-center gap-2 rounded-full bg-[#3559e0] px-5 py-3 text-sm font-extrabold text-white disabled:opacity-40" disabled={!question.trim() || loading}>{loading ? "Thinking…" : "Ask"}<Icon name="arrow" className="h-4 w-4" /></button></div>
        </form>
        <div className="mt-6 flex flex-wrap gap-2">{exampleQuestions.map((item) => <button className="rounded-full border border-[#171714]/15 bg-[#fffaf0] px-4 py-2.5 text-left text-xs font-bold transition hover:border-[#171714] hover:bg-white" key={item} onClick={() => submit(undefined, item)}>{item}</button>)}</div>
        {loading && <div className="mt-8 animate-pulse rounded-[24px] bg-white p-6"><div className="h-3 w-2/3 rounded bg-[#e9e5da]" /><div className="mt-3 h-3 w-5/6 rounded bg-[#e9e5da]" /></div>}
        {error && <div className="mt-8 rounded-[24px] border border-[#e6a192] bg-[#fff0ec] p-6"><p className="text-sm font-extrabold text-[#9f3925]">{error}</p></div>}
        {answer && !loading && <article className="mt-8 rounded-[26px] bg-[#c8f04b] p-6 md:p-8"><p className="text-base font-bold leading-7">{answer}</p></article>}
        {history.length > 0 && <div className="mt-12"><h2 className="font-display text-3xl font-semibold">This session</h2><div className="mt-5 space-y-3">{history.map((item, index) => <details className="rounded-2xl border border-[#171714]/10 bg-white p-5" key={`${item.question}-${index}`}><summary className="cursor-pointer text-sm font-extrabold">{item.question}</summary><p className="mt-4 border-t border-[#171714]/10 pt-4 text-sm font-medium leading-6 text-[#65655d]">{item.answer}</p></details>)}</div></div>}
      </div>
    </section>
  );
}
