import { useState } from "react";
import { askErrorMessage, askQuestion } from "../../shared/api/askApi";

export type HistoryItem = { question: string; answer: string };

export function useAsk() {
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const ask = async (question: string) => {
    const value = question.trim();
    if (!value || loading) return false;
    setError("");
    setAnswer("");
    setLoading(true);
    try {
      const text = await askQuestion(value);
      setAnswer(text);
      setHistory((items) => [{ question: value, answer: text }, ...items].slice(0, 4));
      return true;
    } catch (err) {
      setError(askErrorMessage(err));
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { answer, error, loading, history, ask };
}
