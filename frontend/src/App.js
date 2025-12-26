import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import ChatMessage from './components/ChatMessage';
import ModelSelector from './components/ModelSelector';
import TokenSlider from './components/TokenSlider';
import SegmentedControl from './components/SegmentedControl';
import EmptyState from './components/EmptyState';
import ThemeToggle from './components/ThemeToggle';
import api from './services/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('meta-llama/llama-3.1-8b-instruct:free');
  const [maxTokens, setMaxTokens] = useState(1024);
  const [showDebug, setShowDebug] = useState(false);
  const [models, setModels] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch available models on mount
    api.getModels()
      .then(data => {
        setModels(data.models);
        if (data.models.length > 0) {
          setSelectedModel(data.models[0]);
        }
      })
      .catch(err => console.error('Failed to fetch models:', err));
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const data = await api.generate(inputValue, selectedModel, maxTokens, showDebug);
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        latency: data.latency_ms,
        tokens: data.tokens,
        debug: data.debug
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: error.message || 'An unexpected error occurred. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isError: true,
        errorTitle: error.title,
        errorCode: error.code
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([]);
  };

  const setTokenPreset = (value) => {
    setMaxTokens(value);
  };

  const insertExample = (text) => {
    setInputValue(text);
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <div className="header-left">
              <h1 className="title">EchoAI</h1>
              <p className="subtitle">Confident, focused AI chat</p>
            </div>
            <div className="header-right">
              <ThemeToggle />
            </div>
          </div>
        </header>

        <div className="controls">
          <div className="controls-wrapper">
            <div className="controls-row">
              <ModelSelector 
                models={models}
                selected={selectedModel}
                onChange={setSelectedModel}
              />
              <TokenSlider 
                value={maxTokens}
                onChange={setMaxTokens}
              />
            </div>

            <div className="controls-row">
              <SegmentedControl
                options={[
                  { label: 'Short', value: 512 },
                  { label: 'Balanced', value: 1024 },
                  { label: 'Long', value: 2048 },
                  { label: 'Max', value: 4096 }
                ]}
                selected={maxTokens}
                onChange={(v) => setTokenPreset(v)}
              />

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={showDebug}
                  onChange={(e) => setShowDebug(e.target.checked)}
                />
                <span>Show Debug Info</span>
              </label>
            </div>
          </div>
        </div>

        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <EmptyState onChoose={insertExample} />
            )}
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {loading && (
              <div className="loading-message">
                <div className="loading-spinner"></div>
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="input-container">
          <div className="input-container-wrapper">
            <div className="input-wrapper">
              <textarea
                className="input-field"
                placeholder="Ask anything... (Shift + Enter for new line)"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={2}
                disabled={loading}
              />
              <button 
                className="send-btn"
                onClick={handleSend}
                disabled={loading || !inputValue.trim()}
              >
                {loading ? '...' : '→'}
              </button>
            </div>
            <div className="input-footer">
              <button 
                className="clear-btn"
                onClick={handleClear}
                disabled={messages.length === 0}
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
