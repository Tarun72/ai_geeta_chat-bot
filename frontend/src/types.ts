export interface Source {
  id: string;
  score: number;
  chapter: number | null;
  verse_number: number | null;
  preview: string;
}

export interface ChatRequest {
  question: string;
  top_k?: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  isStreaming?: boolean;
}

export type StreamEvent =
  | { type: "sources"; sources: Source[] }
  | { type: "token"; token: string }
  | { type: "done" }
  | { type: "error"; message: string };
