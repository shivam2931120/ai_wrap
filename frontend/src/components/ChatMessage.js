import React from 'react';
import './ChatMessage.css';
import ReactMarkdown from 'react-markdown';

function ChatMessage({ message }) {
  const { role, content, timestamp, latency, tokens, debug, isError, errorTitle, errorCode } = message;

  return (
    <div className={`message ${role === 'user' ? 'message-user' : 'message-assistant'} ${isError ? 'message-error' : ''}`}>
      <div className="message-header">
        <span className="message-role">
          {role === 'user' ? 'You' : 'Assistant'}
        </span>
        <span className="message-time">{timestamp}</span>
      </div>
      <div className="message-content">
        {isError && errorTitle && (
          <div className="error-title">
            <strong>{errorTitle}</strong>
            {errorCode && <span className="error-code">{errorCode}</span>}
          </div>
        )}
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
      {!isError && latency && (
        <div className="message-metadata">
          <span>⏱ {Math.round(latency)}ms</span>
          {tokens && <span>• ~{tokens} tokens</span>}
        </div>
      )}
      {debug && (
        <details className="debug-info">
          <summary>Debug Info</summary>
          <pre>{JSON.stringify(debug, null, 2)}</pre>
        </details>
      )}
    </div>
  );
}

export default ChatMessage;
