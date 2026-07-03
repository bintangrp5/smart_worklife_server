import React, { useState } from 'react';
import Overview from './Overview';
import Users from './Users';
import Ratings from './Ratings';
import Health from './Health';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart2, 
  UsersIcon, 
  Star, 
  Activity, 
  FileText, 
  HeartPulse, 
  FileCode2, 
  LogOut, 
  Menu, 
  X 
} from 'lucide-react';

const Dashboard = () => {
  const [activePage, setActivePage] = useState('overview');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
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
    window.location.href = '/admin/logout';
  };

  const handleNavClick = (page) => {
    setActivePage(page);
    setIsSidebarOpen(false);
  };

  return (
    <>
      <div className="mobile-header">
        <button className="btn-hamburger" onClick={() => setIsSidebarOpen(true)}>
          <Menu size={24} />
        </button>
        <div className="mobile-title">Developer Dashboard</div>
      </div>
      
      {isSidebarOpen && <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)}></div>}

      <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <img src="/static/logo.png" className="brand-icon" alt="Logo" />
          <div className="brand-text">
            <div className="brand-name">Smart-WorkLife</div>
            <div className="brand-sub">Developer Dashboard</div>
          </div>
          <button className="btn-close" onClick={() => setIsSidebarOpen(false)}>
            <X size={24} />
          </button>
        </div>
        <nav>
          <span className="nav-sep">Menu</span>
          <button 
            className={`nav-item ${activePage === 'overview' ? 'active' : ''}`}
            onClick={() => handleNavClick('overview')}
          >
            <BarChart2 size={18} style={{ marginRight: '8px' }} /> Overview &amp; Metrik
          </button>
          <button 
            className={`nav-item ${activePage === 'users' ? 'active' : ''}`}
            onClick={() => handleNavClick('users')}
          >
            <UsersIcon size={18} style={{ marginRight: '8px' }} /> Data Pengguna
          </button>
          <button 
            className={`nav-item ${activePage === 'ratings' ? 'active' : ''}`}
            onClick={() => handleNavClick('ratings')}
          >
            <Star size={18} style={{ marginRight: '8px' }} /> Feedback &amp; Rating
          </button>
          <button 
            className={`nav-item ${activePage === 'health' ? 'active' : ''}`}
            onClick={() => handleNavClick('health')}
          >
            <Activity size={18} style={{ marginRight: '8px' }} /> System Health
          </button>
          
          <span className="nav-sep">Links</span>
          <a className="nav-item" href="/docs" target="_blank" rel="noreferrer">
            <FileText size={18} style={{ marginRight: '8px' }} /> API Docs (Swagger)
          </a>
          <a className="nav-item" href="/health" target="_blank" rel="noreferrer">
            <HeartPulse size={18} style={{ marginRight: '8px' }} /> Health Check
          </a>
          <a className="nav-item" href="/redoc" target="_blank" rel="noreferrer">
            <FileCode2 size={18} style={{ marginRight: '8px' }} /> ReDoc
          </a>
        </nav>
        <div className="sidebar-footer">
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={18} style={{ marginRight: '8px' }} /> Logout
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
