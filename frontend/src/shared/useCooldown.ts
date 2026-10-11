import { useEffect, useState } from "react";

export function useCooldown(ms = 45000) {
  const [until, setUntil] = useState(0);
  const [now, setNow] = useState(0);

  useEffect(() => {
    const left = until - Date.now();
    if (left <= 0) return;
    const timer = window.setTimeout(() => setNow(Date.now()), left);
    return () => window.clearTimeout(timer);
  }, [until]);

  const start = () => {
    setNow(Date.now());
    setUntil(Date.now() + ms);
  };
  return { waiting: until > now, start };
}
