import React from 'react';

const ChatMessage = ({ message, isUser }) => {
  return (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
      <div className="message-content">{message}</div>
    </div>
  );
};

export default ChatMessage;