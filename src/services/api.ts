import axios from "axios";
import type { AuthResponse, ChatResponse, Dashboard, DocumentRecord, UserProfile } from "@/types";

function resolveBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === "string" && envUrl.trim() !== "") {
    return envUrl.trim();
  }

  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    // Local development connects directly to local FastAPI server
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return "http://localhost:8000";
    }
    // On Vercel or any cloud-deployed domain, use relative /api
    return "/api";
  }

  return "http://localhost:8000";
}

export const API_BASE_URL = resolveBaseUrl();

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    "Bypass-Tunnel-Reminder": "true"
  }
});

// Automatic Network Error Recovery Interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const isNetworkError =
      error.message === "Network Error" ||
      error.code === "ERR_NETWORK" ||
      error.code === "ECONNABORTED" ||
      !error.response;

    const originalRequest = error.config;

    // If an external backend or mixed-content call fails on Vercel, auto-fallback to internal /api
    if (
      isNetworkError &&
      originalRequest &&
      !originalRequest._retryWithInternalApi &&
      typeof window !== "undefined" &&
      window.location.hostname !== "localhost" &&
      window.location.hostname !== "127.0.0.1" &&
      originalRequest.baseURL !== "/api"
    ) {
      originalRequest._retryWithInternalApi = true;
      originalRequest.baseURL = "/api";
      return api(originalRequest);
    }

    return Promise.reject(error);
  }
);

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export async function register(payload: { name: string; email: string; password: string }) {
  const { data } = await api.post<AuthResponse>("/register", payload);
  return data;
}

export async function login(payload: { email: string; password: string }) {
  const { data } = await api.post<AuthResponse>("/login", payload);
  return data;
}

export async function getProfile() {
  const { data } = await api.get<UserProfile>("/profile");
  return data;
}

export async function uploadDocuments(files: FileList | File[]) {
  const form = new FormData();
  Array.from(files).forEach((file) => form.append("files", file));
  const { data } = await api.post<{ documents: DocumentRecord[] }>("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data.documents;
}

export async function listDocuments() {
  const { data } = await api.get<DocumentRecord[]>("/documents");
  return data;
}

export async function deleteDocument(id: string) {
  await api.delete(`/document/${id}`);
}

export async function askChat(question: string, topK = 6) {
  const { data } = await api.post<ChatResponse>("/chat", { question, top_k: topK });
  return data;
}

export async function getHistory() {
  const { data } = await api.get<ChatResponse[]>("/history");
  return data;
}

export async function getDashboard() {
  const { data } = await api.get<Dashboard>("/dashboard");
  return data;
}

export async function exportChatPdf(chatId: string) {
  const { data } = await api.get<Blob>(`/history/${chatId}/export`, { responseType: "blob" });
  return data;
}

export async function setChatFavorite(chatId: string, favorite: boolean) {
  await api.patch(`/history/${chatId}/favorite`, { favorite });
}

export function chatSocketUrl(token: string) {
  try {
    const base = API_BASE_URL.startsWith("http") ? API_BASE_URL : window.location.origin;
    const url = new URL(base);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    url.pathname = "/ws/chat";
    url.searchParams.set("token", token);
    return url.toString();
  } catch {
    return "";
  }
}
