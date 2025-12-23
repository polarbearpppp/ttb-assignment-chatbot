import { useState, type FormEvent } from 'react';
import './App.css';

interface Message {
  role: 'user' | 'ai';
  text: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', text: 'Welcome to TTB Assistant. How can I help you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Math.floor(Math.random() * 10000)}`);
  const options = ["สินเชื่อ", "เปิดบัญชีอย่างไร", "ยอดเงินไม่เข้า", "สแกนจ่ายไม่ได้"];

  const handleSend = async (content: string) => {
    if (!content.trim() || loading) return;

    const updatedMessages: Message[] = [...messages, { role: 'user', text: content }];
    setMessages(updatedMessages);
    setInputValue(''); // Clear input after sending
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: content,
          thread_id: sessionId
        }),
      });

      const data = await response.json();
      setMessages([...updatedMessages, { role: 'ai', text: data.response }]);
    } catch (err) {
      setMessages([...updatedMessages, { role: 'ai', text: "Service temporarily unavailable." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    handleSend(inputValue);
  };

  return (
    <div className="container">
      <div className="chat-card">
        <div className="header">TTB Digital Assistant</div>

        <div className="chat-area">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.text}
            </div>
          ))}
          {loading && (
            <div className="message ai typing-indicator">
              <span></span><span></span><span></span>
            </div>
          )}
        </div>

        {/* Quick Options */}
        <div className="options-grid">
          {options.map(opt => (
            <button key={opt} onClick={() => handleSend(opt)} disabled={loading} className="opt-button">
              {opt}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form className="input-container" onSubmit={handleSubmit}>
          <input 
            type="text" 
            className="chat-input"
            placeholder="Type your question..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="send-button" disabled={loading || !inputValue.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}