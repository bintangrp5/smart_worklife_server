import React, { useEffect, useState } from 'react';

const Health = () => {
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    fetch('/admin/api/health')
      .then(r => r.json())
      .then(data => setHealthData(data))
      .catch(err => console.error(err));
  }, []);

  const healthItems = [
    { k: 'postgresql', label: 'PostgreSQL (Neon)', icon: '🐘' },
    { k: 'backend', label: 'FastAPI Backend', icon: '⚡' },
    { k: 'cloudinary', label: 'Cloudinary CDN', icon: '☁️' }
  ];

  return (
    <div className="page active" id="page-health">
      <div className="page-title">🖥️ System Health &amp; Status</div>
      <div className="page-sub">Status koneksi layanan backend</div>
      <hr className="div" />
      <div className="health-grid">
        {!healthData ? (
          <div className="spin">⏳ Memuat...</div>
        ) : (
          healthItems.map(({ k, label, icon }) => {
            const ok = healthData[k];
            return (
              <div className="health-card" key={k}>
                <div className={`health-dot ${ok ? 'dot-green' : 'dot-red'}`}></div>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>{icon}</div>
                <div className="health-name">{label}</div>
                <div className="health-status">{ok ? '🟢 Terhubung & Normal' : '🔴 Gagal Terhubung'}</div>
              </div>
            );
          })
        )}
      </div>
      <hr className="div" />
      <div className="page-title" style={{ fontSize: '16px', marginBottom: '12px' }}>🔗 Quick Links</div>
      <div className="link-grid">
        <a href="/docs" target="_blank" rel="noreferrer" className="link-card">
          <div className="link-icon">📋</div>
          <div>
            <div className="link-label">Swagger UI</div>
            <div className="link-sub">API Documentation</div>
          </div>
        </a>
        <a href="/health" target="_blank" rel="noreferrer" className="link-card">
          <div className="link-icon">❤️</div>
          <div>
            <div className="link-label">Health Check</div>
            <div className="link-sub">Backend status</div>
          </div>
        </a>
        <a href="/redoc" target="_blank" rel="noreferrer" className="link-card">
          <div className="link-icon">📄</div>
          <div>
            <div className="link-label">ReDoc</div>
            <div className="link-sub">API Reference</div>
          </div>
        </a>
      </div>
    </div>
  );
};

export default Health;
