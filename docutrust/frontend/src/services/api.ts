import axios from "axios";
import type { AuthResponse, ChatResponse, Dashboard, DocumentRecord, UserProfile } from "@/types";

export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000
});

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
  const url = new URL(API_BASE_URL);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "/ws/chat";
  url.searchParams.set("token", token);
  return url.toString();
}
