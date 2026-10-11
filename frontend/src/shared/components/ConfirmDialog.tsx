import { useEffect } from "react";

export default function ConfirmDialog({ title, text, confirmLabel = "Delete", onCancel, onConfirm }: { title: string; text: string; confirmLabel?: string; onCancel: () => void; onConfirm: () => void }) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="fixed inset-0 z-50 grid place-items-end bg-[#171714]/25 p-3 backdrop-blur-sm sm:place-items-center" onMouseDown={onCancel}>
      <section aria-modal="true" aria-labelledby="confirm-title" className="w-full max-w-md rounded-[28px] border border-[#171714] bg-[#fffaf0] p-6 shadow-[7px_7px_0_#171714]" role="dialog" onMouseDown={(event) => event.stopPropagation()}>
        <h2 className="font-display text-3xl font-semibold" id="confirm-title">{title}</h2>
        <p className="mt-3 text-sm font-medium leading-6 text-[#707067]">{text}</p>
        <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button className="rounded-full border border-[#171714]/20 bg-white px-6 py-3.5 text-sm font-bold" onClick={onCancel}>Cancel</button>
          <button className="rounded-full bg-[#c53f2b] px-7 py-3.5 text-sm font-extrabold text-white" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </section>
    </div>
  );
}
