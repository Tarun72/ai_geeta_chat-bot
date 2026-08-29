import { ChatWindow } from "./components/ChatWindow";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-content">
          <p className="app-eyebrow">Bhagavad Gita RAG Chatbot</p>
          <h1 className="app-title">Ask Krishna&apos;s Wisdom</h1>
          <p className="app-subtitle">
            Answers grounded in verses from Bhagavad-gita As It Is, with chapter and verse citations.
          </p>
        </div>
      </header>
      <main className="app-main">
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;
