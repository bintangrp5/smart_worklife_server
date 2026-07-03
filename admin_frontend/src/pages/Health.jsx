import React, { useEffect, useState } from 'react';
import { Database, Zap, Cloud, Activity, Loader, CheckCircle, XCircle, Link, FileText, HeartPulse, FileCode2 } from 'lucide-react';

const Health = () => {
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    fetch('/admin/api/health')
      .then(r => r.json())
      .then(data => setHealthData(data))
      .catch(err => console.error(err));
  }, []);

  const healthItems = [
    { k: 'postgresql', label: 'PostgreSQL (Neon)', icon: <Database size={24} /> },
    { k: 'backend', label: 'FastAPI Backend', icon: <Zap size={24} /> },
    { k: 'cloudinary', label: 'Cloudinary CDN', icon: <Cloud size={24} /> }
  ];

  return (
    <div className="page active" id="page-health">
      <div className="page-title"><Activity style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> System Health &amp; Status</div>
      <div className="page-sub">Status koneksi layanan backend</div>
      <hr className="div" />
      <div className="health-grid">
        {!healthData ? (
          <div className="spin"><Loader className="animate-spin" style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={16} /> Memuat...</div>
        ) : (
          healthItems.map(({ k, label, icon }) => {
            const ok = healthData[k];
            return (
              <div className="health-card" key={k}>
                <div className={`health-dot ${ok ? 'dot-green' : 'dot-red'}`}></div>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>{icon}</div>
                <div className="health-name">{label}</div>
                <div className="health-status">{ok ? <><CheckCircle size={14} color="var(--green)" style={{ marginRight: '4px', verticalAlign: 'text-bottom' }} /> Terhubung &amp; Normal</> : <><XCircle size={14} color="var(--red)" style={{ marginRight: '4px', verticalAlign: 'text-bottom' }} /> Gagal Terhubung</>}</div>
              </div>
            );
          })
        )}
      </div>
      <hr className="div" />
      <div className="page-title" style={{ fontSize: '16px', marginBottom: '12px' }}><Link style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={16} /> Quick Links</div>
      <div className="link-grid">
        <a href="/docs" target="_blank" rel="noreferrer" className="link-card">
          <div className="link-icon"><FileText /></div>
          <div>
            <div className="link-label">Swagger UI</div>
            <div className="link-sub">API Documentation</div>
          </div>
        </a>
        <a href="/health" target="_blank" rel="noreferrer" className="link-card">
          <div className="link-icon"><HeartPulse /></div>
          <div>
            <div className="link-label">Health Check</div>
            <div className="link-sub">Backend status</div>
          </div>
        </a>
        <a href="/redoc" target="_blank" rel="noreferrer" className="link-card">
          <div className="link-icon"><FileCode2 /></div>
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
