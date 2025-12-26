import React from 'react';
import './ModelSelector.css';

function ModelSelector({ models, selected, onChange }) {
  return (
    <div className="model-selector">
      <label htmlFor="model-select" className="selector-label">Model</label>
      <select
        id="model-select"
        className="selector-dropdown"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Select AI model"
      >
        {models.map((model) => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ModelSelector;
