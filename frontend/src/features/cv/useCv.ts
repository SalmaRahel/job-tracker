import { useState } from "react";
import { getCvUrl, startCv, type CvStyle } from "../../shared/api/cvApi";
import { useJobTask } from "../notifications/useJobTask";

export function useCv(jobId: number) {
  const [openError, setOpenError] = useState("");
  const [style, setStyle] = useState<CvStyle>({ template: "colored", palette: "dark_gray_blue" });
  const task = useJobTask<string>({
    jobId,
    kind: "cv",
    start: () => startCv(jobId, style),
    fetchResult: () => getCvUrl(jobId),
  });

  const open = async () => {
    setOpenError("");
    const tab = window.open("about:blank", "_blank");
    try {
      const url = await getCvUrl(jobId);
      if (!url) throw new Error("CV not found");
      if (tab) {
        tab.opener = null;
        tab.location.href = url;
      }
    } catch (err) {
      tab?.close();
      setOpenError(err instanceof Error ? err.message : "Could not open the CV");
    }
  };

  return {
    ready: task.result !== null,
    phase: task.phase,
    error: task.error || openError,
    waiting: task.waiting,
    generate: task.run,
    style,
    setStyle,
    open,
  };
}
