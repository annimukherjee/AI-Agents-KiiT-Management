import React, { useState } from 'react';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Sends message to the backend and retrieves AI response
  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add the user's message to the chat
    const userMessage = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call your Python backend here
      const response = await fetch('http://localhost:8000/placement/bot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      // data should be something like: { response: "AI reply text" }

      // Add the AI's response to the chat
      const aiMessage = { text: data.response, sender: 'ai' };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      // Optionally show an error message in the chat
      const errorMsg = { text: 'Oops! Something went wrong.', sender: 'ai' };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Allow sending on Enter key press
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={styles.chatContainer}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={{ margin: 0 }}>My Chatbot</h2>
      </div>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              ...styles.message,
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.sender === 'user' ? '#DCF8C6' : '#F1F0F0',
            }}
          >
            {msg.text}
          </div>
        ))}
        {isLoading && (
          <div
            style={{
              ...styles.message,
              alignSelf: 'flex-start',
              backgroundColor: '#F1F0F0',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <div className="loader" style={{ ...styles.loader, marginRight: 8 }} />
            <span>The AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Input + Send Button */}
      <div style={styles.inputContainer}>
        <textarea
          style={styles.textarea}
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          style={styles.sendButton}
          onClick={sendMessage}
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
}

/* Inline styles for simplicity. You can also move these into a .css file. */
const styles = {
  chatContainer: {
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '600px',
    height: '80vh',
    margin: '40px auto',
    border: '1px solid #ccc',
    borderRadius: '8px',
    overflow: 'hidden',
    fontFamily: 'sans-serif',
  },
  header: {
    backgroundColor: '#4CAF50',
    color: '#fff',
    padding: '16px',
    textAlign: 'center',
  },
  messagesContainer: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    padding: '16px',
    overflowY: 'auto',
    backgroundColor: '#FAFAFA',
  },
  message: {
    maxWidth: '60%',
    marginBottom: '8px',
    padding: '8px 12px',
    borderRadius: '16px',
    lineHeight: '1.4',
    fontSize: '14px',
    whiteSpace: 'pre-wrap',
  },
  inputContainer: {
    display: 'flex',
    borderTop: '1px solid #ccc',
  },
  textarea: {
    flex: 1,
    resize: 'none',
    border: 'none',
    outline: 'none',
    padding: '12px',
    fontSize: '14px',
  },
  sendButton: {
    backgroundColor: '#4CAF50',
    color: '#fff',
    border: 'none',
    padding: '0 20px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  loader: {
    width: '14px',
    height: '14px',
    border: '2px solid #ccc',
    borderTop: '2px solid #2196F3',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
};

/* If you want the spinner to work inline, add this global CSS somewhere:
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
*/

export default Chatbot;
