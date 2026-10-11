import { BASE_URL } from "./client";

export type JobEvent = { kind: "analysis" | "cv"; status: "ready" | "failed"; jobId: number };

export type NotificationHandlers = {
  onEvent: (event: JobEvent) => void;
  onConnected: () => void;
};

const PREFIXES: Array<[string, JobEvent["kind"], JobEvent["status"]]> = [
  ["matching score is ready", "analysis", "ready"],
  ["matching failed", "analysis", "failed"],
  ["cv generated", "cv", "ready"],
  ["cv generation failed", "cv", "failed"],
];

export function parseNotification(text: string): JobEvent | null {
  const id = text.match(/job_id: (\d+)/);
  const known = PREFIXES.find(([prefix]) => text.startsWith(prefix));
  if (!id || !known) return null;
  return { kind: known[1], status: known[2], jobId: Number(id[1]) };
}

export function connectNotifications(token: string, handlers: NotificationHandlers) {
  const url = `${BASE_URL.replace(/^http/, "ws")}/ws/notifications`;
  let socket: WebSocket | null = null;
  let timer: number | undefined;
  let attempt = 0;
  let closed = false;

  const connect = () => {
    socket = new WebSocket(url);
    socket.onopen = () => socket?.send(token);
    socket.onmessage = (message) => {
      const text = String(message.data);
      if (text.startsWith("authenticated")) {
        attempt = 0;
        return handlers.onConnected();
      }
      const event = parseNotification(text);
      if (event) handlers.onEvent(event);
    };
    socket.onclose = (event) => {
      if (closed || event.code === 1008) return;
      const delay = Math.min(1000 * 2 ** attempt, 10000);
      attempt += 1;
      timer = window.setTimeout(connect, delay);
    };
  };

  connect();
  return () => {
    closed = true;
    window.clearTimeout(timer);
    socket?.close();
  };
}
