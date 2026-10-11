import { useEffect, useState } from "react";
import { getDashboard, type Dashboard } from "../../shared/api/dashboardApi";

export function useDashboard() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let current = true;
    setLoading(true);
    setError("");
    getDashboard()
      .then((result) => current && setData(result))
      .catch((err) => current && setError(err instanceof Error ? err.message : "Something went wrong"))
      .finally(() => current && setLoading(false));
    return () => {
      current = false;
    };
  }, [attempt]);

  return { data, loading, error, reload: () => setAttempt((count) => count + 1) };
}
