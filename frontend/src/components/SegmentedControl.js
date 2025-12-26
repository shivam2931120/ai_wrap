import React from 'react';
import './SegmentedControl.css';

function SegmentedControl({ options = [], selected, onChange }) {
  return (
    <div className="segmented-control" role="tablist" aria-label="Token presets">
      {options.map((opt) => (
        <button
          key={opt.value}
          role="tab"
          aria-selected={selected === opt.value}
          className={`seg-btn ${selected === opt.value ? 'seg-selected' : ''}`}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default SegmentedControl;
