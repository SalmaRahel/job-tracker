import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import * as authApi from "../../shared/api/authApi";
import { clearToken, getEmail, getToken, setEmail, setToken, setUnauthorizedHandler } from "../../shared/api/client";

type AuthValue = {
  token: string | null;
  email: string | null;
  isLoggedIn: boolean;
  sessionExpired: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(getToken);
  const [email, setEmailState] = useState<string | null>(getEmail);
  const [sessionExpired, setSessionExpired] = useState(false);

  const logout = () => {
    clearToken();
    setTokenState(null);
    setEmailState(null);
    setSessionExpired(false);
  };

  const save = (email: string, { access_token }: { access_token: string }) => {
    setToken(access_token);
    setSessionExpired(false);
    setEmail(email);
    setTokenState(access_token);
    setEmailState(email);
  };

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setSessionExpired(true);
      setTokenState(null);
      setEmailState(null);
    });
  }, []);

  const value: AuthValue = {
    token,
    email,
    isLoggedIn: token !== null,
    sessionExpired,
    login: async (email, password) => save(email, await authApi.login(email, password)),
    register: async (email, password) => save(email, await authApi.register(email, password)),
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
