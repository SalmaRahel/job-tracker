import { getAnalysis, startAnalysis, type Analysis } from "../../shared/api/matchingApi";
import { useJobTask } from "../notifications/useJobTask";

export function useMatching(jobId: number) {
  return useJobTask<Analysis>({
    jobId,
    kind: "analysis",
    start: () => startAnalysis(jobId),
    fetchResult: () => getAnalysis(jobId),
    isFresh: (current, previous) => previous === null || current.id !== previous.id,
  });
}
