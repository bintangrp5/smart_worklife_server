import React, { useState } from 'react';
import Overview from './Overview';
import Users from './Users';
import Ratings from './Ratings';
import Health from './Health';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [activePage, setActivePage] = useState('overview');
  const navigate = useNavigate();

  const renderPage = () => {
    switch (activePage) {
      case 'overview': return <Overview />;
      case 'users': return <Users />;
      case 'ratings': return <Ratings />;
      case 'health': return <Health />;
      default: return <Overview />;
    }
  };

  const handleLogout = () => {
    // Basic redirect for logout, or call API if needed
    window.location.href = '/admin/logout';
  };

  return (
    <>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/static/logo.png" className="brand-icon" alt="Logo" />
          <div className="brand-name">Smart-WorkLife</div>
          <div className="brand-sub">Developer Dashboard</div>
        </div>
        <nav>
          <span className="nav-sep">Menu</span>
          <button 
            className={`nav-item ${activePage === 'overview' ? 'active' : ''}`}
            onClick={() => setActivePage('overview')}
          >
            📊 Overview &amp; Metrik
          </button>
          <button 
            className={`nav-item ${activePage === 'users' ? 'active' : ''}`}
            onClick={() => setActivePage('users')}
          >
            👥 Data Pengguna
          </button>
          <button 
            className={`nav-item ${activePage === 'ratings' ? 'active' : ''}`}
            onClick={() => setActivePage('ratings')}
          >
            ⭐ Feedback &amp; Rating
          </button>
          <button 
            className={`nav-item ${activePage === 'health' ? 'active' : ''}`}
            onClick={() => setActivePage('health')}
          >
            🖥️ System Health
          </button>
          
          <span className="nav-sep">Links</span>
          <a className="nav-item" href="/docs" target="_blank" rel="noreferrer">📋 API Docs (Swagger)</a>
          <a className="nav-item" href="/health" target="_blank" rel="noreferrer">❤️ Health Check</a>
          <a className="nav-item" href="/redoc" target="_blank" rel="noreferrer">📄 ReDoc</a>
        </nav>
        <div className="sidebar-footer">
          <button className="btn-logout" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </aside>

      <main className="main">
        {renderPage()}
      </main>
    </>
  );
};

export default Dashboard;
