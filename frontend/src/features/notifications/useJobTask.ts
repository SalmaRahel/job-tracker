import { useEffect, useRef, useState } from "react";
import { ApiError } from "../../shared/api/client";
import type { JobEvent } from "../../shared/api/notifications";
import { useCooldown } from "../../shared/useCooldown";
import { useNotifications } from "./useNotifications";

const TIMEOUT_MS = 120000;

type Options<T> = {
  jobId: number;
  kind: JobEvent["kind"];
  start: () => Promise<unknown>;
  fetchResult: () => Promise<T | null>;
  isFresh?: (current: T, previous: T | null) => boolean;
};

export function useJobTask<T>({ jobId, kind, start, fetchResult, isFresh = (_, previous) => previous === null }: Options<T>) {
  const [result, setResult] = useState<T | null>(null);
  const [phase, setPhase] = useState<"idle" | "loading" | "failed">("idle");
  const [error, setError] = useState("");
  const cooldown = useCooldown();
  const phaseRef = useRef(phase);
  const previous = useRef<T | null>(null);
  const timer = useRef<number | undefined>(undefined);
  const alive = useRef(true);

  const finish = (next: "idle" | "loading" | "failed") => {
    window.clearTimeout(timer.current);
    phaseRef.current = next;
    setPhase(next);
  };

  const refresh = async (requireFresh: boolean) => {
    try {
      const current = await fetchResult();
      if (!alive.current || current === null) return false;
      const waiting = phaseRef.current === "loading";
      if (waiting && requireFresh && !isFresh(current, previous.current)) return false;
      setResult(current);
      if (waiting) finish("idle");
      return true;
    } catch {
      return false;
    }
  };

  useEffect(() => {
    alive.current = true;
    refresh(true);
    return () => {
      alive.current = false;
      window.clearTimeout(timer.current);
    };
  }, [jobId]);

  useNotifications({
    onConnected: () => void refresh(true),
    onEvent: (event) => {
      if (event.kind !== kind || event.jobId !== jobId) return;
      if (event.status === "ready") void refresh(false);
      else if (phaseRef.current === "loading") finish("failed");
    },
  });

  const run = async () => {
    previous.current = result;
    setError("");
    finish("loading");
    try {
      await start();
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        cooldown.start();
        setError(err.message);
        return finish("idle");
      }
      return finish("failed");
    }
    cooldown.start();
    timer.current = window.setTimeout(async () => {
      const found = await refresh(true);
      if (!found && alive.current && phaseRef.current === "loading") finish("failed");
    }, TIMEOUT_MS);
  };

  return { result, phase, error, waiting: cooldown.waiting, run };
}
