import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";

import { useChat } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";

export function ChatWindow() {
  const { messages, isLoading, error, sendMessage, clearError } = useChat();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const question = input.trim();
    if (!question) {
      return;
    }

    setInput("");
    clearError();
    await sendMessage(question);
    inputRef.current?.focus();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit(event);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p>Ask a question about the Bhagavad Gita.</p>
            <p className="chat-empty-hint">
              For example: &ldquo;What is karma yoga?&rdquo; or &ldquo;How should one act without attachment?&rdquo;
            </p>
          </div>
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="chat-error">{error}</div>}

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the Gita..."
          rows={2}
          disabled={isLoading}
        />
        <button className="chat-send-button" type="submit" disabled={isLoading || !input.trim()}>
          {isLoading ? "Thinking..." : "Ask"}
        </button>
      </form>
    </div>
  );
}
