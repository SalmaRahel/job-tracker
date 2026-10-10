import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import * as authApi from "../../shared/api/authApi";
import { clearToken, getToken, setToken, setUnauthorizedHandler } from "../../shared/api/client";

type AuthValue = {
  token: string | null;
  isLoggedIn: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(getToken);

  const logout = () => {
    clearToken();
    setTokenState(null);
  };

  const save = ({ access_token }: { access_token: string }) => {
    setToken(access_token);
    setTokenState(access_token);
  };

  useEffect(() => {
    setUnauthorizedHandler(() => setTokenState(null));
  }, []);

  const value: AuthValue = {
    token,
    isLoggedIn: token !== null,
    login: async (email, password) => save(await authApi.login(email, password)),
    register: async (email, password) => save(await authApi.register(email, password)),
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
