import { createContext, useContext, useEffect, useMemo, useRef, type ReactNode } from "react";
import { connectNotifications, type NotificationHandlers } from "../../shared/api/notifications";
import { useAuth } from "../auth/AuthContext";

type Subscribe = (handlers: NotificationHandlers) => () => void;

const NotificationsContext = createContext<Subscribe | null>(null);

export function NotificationsProvider({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const listeners = useRef(new Set<NotificationHandlers>());

  useEffect(() => {
    if (!token) return;
    return connectNotifications(token, {
      onEvent: (event) => listeners.current.forEach((listener) => listener.onEvent(event)),
      onConnected: () => listeners.current.forEach((listener) => listener.onConnected()),
    });
  }, [token]);

  const subscribe = useMemo<Subscribe>(
    () => (handlers) => {
      listeners.current.add(handlers);
      return () => {
        listeners.current.delete(handlers);
      };
    },
    [],
  );

  return <NotificationsContext.Provider value={subscribe}>{children}</NotificationsContext.Provider>;
}

export function useNotifications(handlers: NotificationHandlers) {
  const subscribe = useContext(NotificationsContext);
  const latest = useRef(handlers);
  latest.current = handlers;

  useEffect(() => {
    if (!subscribe) return;
    return subscribe({
      onEvent: (event) => latest.current.onEvent(event),
      onConnected: () => latest.current.onConnected(),
    });
  }, [subscribe]);
}
