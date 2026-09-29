export type UserProfile = {
  id: string;
  name: string;
  email: string;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: UserProfile;
};

export type DocumentRecord = {
  id: string;
  filename: string;
  upload_time: string;
  chunks_count: number;
  status: "processing" | "ready" | "failed" | string;
};

export type Source = {
  source_id: string;
  filename: string;
  page: number | null;
  snippet: string;
  score: number | null;
};

export type AgentLog = {
  step: string;
  status: "pending" | "running" | "completed" | "warning" | "error";
  message: string;
  timestamp: string;
};

export type ChatResponse = {
  id?: string | null;
  question: string;
  answer: string;
  sources: Source[];
  rewritten_query?: string | null;
  retrieval_score: number;
  web_search_used: boolean;
  logs: AgentLog[];
  timestamp: string;
  favorite?: boolean;
};

export type Dashboard = {
  total_documents: number;
  total_chats: number;
  average_retrieval_score: number;
  web_search_usage_percent: number;
  recent_activity: Array<{
    id: string;
    kind: string;
    title: string;
    timestamp: string;
  }>;
};
