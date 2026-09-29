import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { getProfile, login, register, setAuthToken } from "@/services/api";
import type { UserProfile } from "@/types";

type AuthContextValue = {
  token: string | null;
  user: UserProfile | null;
  isBooting: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const STORAGE_KEY = "docutrust.token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isBooting, setIsBooting] = useState(true);

  useEffect(() => {
    setAuthToken(token);
    if (!token) {
      setUser(null);
      setIsBooting(false);
      return;
    }

    getProfile()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(STORAGE_KEY);
        setToken(null);
        setAuthToken(null);
      })
      .finally(() => setIsBooting(false));
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isBooting,
      signIn: async (email, password) => {
        const response = await login({ email, password });
        localStorage.setItem(STORAGE_KEY, response.access_token);
        setAuthToken(response.access_token);
        setToken(response.access_token);
        setUser(response.user);
      },
      signUp: async (name, email, password) => {
        const response = await register({ name, email, password });
        localStorage.setItem(STORAGE_KEY, response.access_token);
        setAuthToken(response.access_token);
        setToken(response.access_token);
        setUser(response.user);
      },
      signOut: () => {
        localStorage.removeItem(STORAGE_KEY);
        setAuthToken(null);
        setToken(null);
        setUser(null);
      }
    }),
    [isBooting, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
