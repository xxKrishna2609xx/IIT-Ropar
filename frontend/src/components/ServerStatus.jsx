import React, { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
const POLL_INTERVAL = 5000; // check every 5 seconds

function formatTime(date) {
  let h = date.getHours();
  const m = String(date.getMinutes()).padStart(2, '0');
  const s = String(date.getSeconds()).padStart(2, '0');
  const ampm = h >= 12 ? 'pm' : 'am';
  h = h % 12 || 12;
  return `${String(h).padStart(2, '0')}:${m}:${s} ${ampm}`;
}

function ServerStatus() {
  const [status, setStatus] = useState('checking'); // 'online' | 'offline' | 'checking'
  const [time, setTime] = useState(formatTime(new Date()));
  const pollRef = useRef(null);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`, {
        signal: AbortSignal.timeout(3000), // 3s timeout
      });
      setStatus(res.ok ? 'online' : 'offline');
    } catch {
      setStatus('offline');
    }
  };

  // Poll backend health
  useEffect(() => {
    checkHealth(); // immediate first check
    pollRef.current = setInterval(checkHealth, POLL_INTERVAL);
    return () => clearInterval(pollRef.current);
  }, []);

  // Live clock — ticks every second
  useEffect(() => {
    const clockId = setInterval(() => {
      setTime(formatTime(new Date()));
    }, 1000);
    return () => clearInterval(clockId);
  }, []);

  const statusLabel =
    status === 'online'   ? 'Connected' :
    status === 'offline'  ? 'Server Offline' :
                            'Connecting…';

  return (
    <div className="server-status-bar">
      {/* Online / Offline pill */}
      <div className={`server-status-pill status-${status}`}>
        {status === 'online' ? (
          /* WiFi icon */
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
               strokeLinecap="round" strokeLinejoin="round" className="status-icon">
            <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
            <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
            <circle cx="12" cy="20" r="1" fill="currentColor" stroke="none"/>
          </svg>
        ) : status === 'offline' ? (
          /* Wifi-off icon */
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
               strokeLinecap="round" strokeLinejoin="round" className="status-icon">
            <line x1="1" y1="1" x2="23" y2="23"/>
            <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/>
            <path d="M5 12.55a11 11 0 0 1 5.17-2.39"/>
            <path d="M10.71 5.05A16 16 0 0 1 22.56 9"/>
            <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/>
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
            <circle cx="12" cy="20" r="1" fill="currentColor" stroke="none"/>
          </svg>
        ) : (
          /* Spinner for checking */
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
               strokeLinecap="round" strokeLinejoin="round" className="status-icon spin">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
        )}
        <span className="status-label">{statusLabel}</span>
      </div>

      {/* Live clock pill */}
      <div className="server-clock-pill">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
             strokeLinecap="round" strokeLinejoin="round" className="clock-icon">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span className="clock-label">{time}</span>
      </div>
    </div>
  );
}

export default ServerStatus;
