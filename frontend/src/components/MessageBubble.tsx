import type { ChatMessage } from "../types";
import { SourceCards } from "./SourceCards";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      <div className={`message-bubble ${isUser ? "message-bubble-user" : "message-bubble-assistant"}`}>
        <div className="message-role">{isUser ? "You" : "Krishna's Wisdom"}</div>
        <div className="message-content">
          {message.content}
          {message.isStreaming && <span className="streaming-cursor" aria-hidden="true" />}
        </div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCards sources={message.sources} />
        )}
      </div>
    </div>
  );
}
