import { useCallback, useRef, useState } from "react";

import { streamChat } from "../api/chat";
import type { ChatMessage, Source } from "../types";

function createId(): string {
  return crypto.randomUUID();
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || isLoading) {
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: trimmed,
    };

    const assistantId = createId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      sources: [],
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    setError(null);

    try {
      for await (const event of streamChat({ question: trimmed }, controller.signal)) {
        if (event.type === "sources") {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, sources: event.sources }
                : message,
            ),
          );
        } else if (event.type === "token") {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + event.token }
                : message,
            ),
          );
        } else if (event.type === "error") {
          setError(event.message);
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content: event.message,
                    isStreaming: false,
                  }
                : message,
            ),
          );
          break;
        } else if (event.type === "done") {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, isStreaming: false }
                : message,
            ),
          );
        }
      }
    } catch (err) {
      if (controller.signal.aborted) {
        return;
      }
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
      setMessages((prev) =>
        prev.map((item) =>
          item.id === assistantId
            ? { ...item, content: message, isStreaming: false }
            : item,
        ),
      );
    } finally {
      setIsLoading(false);
      abortRef.current = null;
    }
  }, [isLoading]);

  const clearError = useCallback(() => setError(null), []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearError,
  };
}

export type { ChatMessage, Source };
