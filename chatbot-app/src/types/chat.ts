export interface ChatHistoryItem {
  role: "user" | "assistant" | "bot";
  message?: string;
  answer?: string;
  timestamp?: string;
}

export interface UserHistoryItem {
  type: string;
  id: string;
  chat_history: ChatHistoryItem[];
  metadata?: unknown;
  tables?: number;
  images?: number;
  chunks?: number;
  rows?: number;
  columns?: number;
  columns_list?: string[];
  filename?: string[];
}