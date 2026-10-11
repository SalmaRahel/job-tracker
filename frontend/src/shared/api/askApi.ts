import { ApiError, apiFetch } from "./client";

export async function askQuestion(question: string) {
  const data = await apiFetch<{ answer: string; row_count: number }>("/job-search/ask", {
    method: "POST",
    body: { question },
  });
  return data.answer;
}

export function askErrorMessage(err: unknown) {
  if (err instanceof ApiError) {
    if (err.status === 400) return err.message;
    if (err.status === 429) return "Too many questions. Please wait a moment and try again.";
    if (err.status === 502) return "The AI service had a problem. Please try again.";
    if (err.status === 504) return "That took too long. Try a simpler question.";
  }
  return "Something went wrong. Please try again.";
}
