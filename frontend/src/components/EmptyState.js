import React from 'react';
import './EmptyState.css';

const examples = [
  'Summarize the latest meeting notes into action items.',
  'Draft a professional reply to a client asking for an update.',
  'Explain quantum entanglement in simple terms.'
];

function EmptyState({ onChoose }) {
  return (
    <div className="empty-illustration">
      <svg width="160" height="96" viewBox="0 0 160 96" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="160" height="96" rx="12" fill="#0B1220" />
        <path d="M20 28H140V36H20z" fill="#111827" />
        <circle cx="28" cy="44" r="6" fill="#10B981" />
        <rect x="38" y="40" width="84" height="6" rx="3" fill="#111827" />
      </svg>
      <div className="empty-copy">
        <h3>Ready when you are</h3>
        <p>Try one of these prompts — click to insert.</p>
        <div className="examples">
          {examples.map((ex, i) => (
            <button key={i} className="example-btn" onClick={() => onChoose(ex)}>{ex}</button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default EmptyState;
