import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Login.module.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  const doLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(false);
    
    const fd = new FormData();
    fd.append('email', email);
    fd.append('password', password);
    
    try {
      const r = await fetch('/admin/login', { method: 'POST', body: fd });
      if (r.ok) {
        // Success
        setTimeout(() => navigate('/admin/dashboard'), 500);
      } else {
        setError(true);
        setLoading(false);
      }
    } catch {
      setError(true);
      setLoading(false);
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={`${styles.blob} ${styles.b1}`}></div>
      <div className={`${styles.blob} ${styles.b2}`}></div>
      <div className={`${styles.blob} ${styles.b3}`}></div>
      
      <div className={styles.wrap}>
        <div className={styles.card}>
          <div className={styles.logo}>
            <img src="/static/logo.png" className={styles.logoIcon} alt="Smart-WorkLife Logo" />
            <h1>Smart-WorkLife</h1>
            <p>Developer Operations Center</p>
            <div className={styles.badge}>🔐 ADMIN ONLY</div>
          </div>
          <h2 className={styles.title}>Selamat Datang</h2>
          <p className={styles.sub}>Login dengan kredensial developer Anda</p>
          
          <div className={`${styles.err} ${error ? styles.visible : ''}`}>
            ❌ Email atau password salah.
          </div>
          
          <form onSubmit={doLogin}>
            <div className={styles.formGroup}>
              <label>📧 Email Developer</label>
              <input 
                type="email" 
                placeholder="admin@smartworklife.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required 
              />
            </div>
            <div className={styles.formGroup}>
              <label>🔑 Password</label>
              <input 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required 
              />
            </div>
            <button type="submit" className={`${styles.btn} ${loading ? styles.loading : ''}`}>
              {loading ? 'Memverifikasi...' : (error ? 'Masuk ke Dashboard →' : (loading && !error ? '✓ Berhasil!' : 'Masuk ke Dashboard →'))}
            </button>
          </form>
          
          <div className={styles.divider}><hr/><span>atau</span><hr/></div>
          <a href="/docs" className={styles.link}>📋 Lihat API Documentation (Swagger)</a>
        </div>
      </div>
    </div>
  );
};

export default Login;
