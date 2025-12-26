import React from 'react';
import './TokenSlider.css';

function TokenSlider({ value, onChange }) {
  const level = value <= 512 ? 'low' : value <= 1024 ? 'medium' : value <= 2048 ? 'high' : 'max';

  return (
    <div className="token-slider">
      <div className="slider-top">
        <label htmlFor="token-slider" className="slider-label">Max Tokens</label>
        <div className={`token-badge token-${level}`} title={`Preset: ${level}`}>
          {value}
        </div>
      </div>
      <input
        id="token-slider"
        type="range"
        min="128"
        max="4096"
        step="128"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`slider-input slider-${level}`}
        aria-label="Max tokens"
      />
      <div className="slider-legend">
        <span>Short</span>
        <span>Balanced</span>
        <span>Long</span>
        <span>Max</span>
      </div>
    </div>
  );
}

export default TokenSlider;
