import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/admin/login" replace />} />
        <Route path="/admin/login" element={<Login />} />
        <Route path="/admin/dashboard" element={<Dashboard />} />
        {/* fallback */}
        <Route path="*" element={<Navigate to="/admin/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
