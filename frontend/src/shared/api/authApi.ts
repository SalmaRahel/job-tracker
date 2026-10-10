import { apiFetch } from "./client";

type TokenResponse = { access_token: string; token_type: string };

export const register = (email: string, password: string) =>
  apiFetch<TokenResponse>("/register", { method: "POST", body: { email, password }, auth: false });

export const login = (email: string, password: string) =>
  apiFetch<TokenResponse>("/login", { method: "POST", body: { email, password }, auth: false });
