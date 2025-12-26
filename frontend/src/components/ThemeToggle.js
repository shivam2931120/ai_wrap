import React, { useEffect, useState } from 'react';
import './ThemeToggle.css';

function ThemeToggle() {
  const [theme, setTheme] = useState(() => document.documentElement.getAttribute('data-theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <button
      className={`theme-toggle ${theme === 'dark' ? 'dark' : 'light'}`}
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? '🌙' : '☀️'}
    </button>
  );
}

export default ThemeToggle;
