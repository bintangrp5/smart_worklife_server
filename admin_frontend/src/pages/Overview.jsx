import React, { useEffect, useState, useRef } from 'react';

const Overview = () => {
  const [stats, setStats] = useState(null);
  const [features, setFeatures] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartNewUsersRef = useRef(null);
  const chartPomodoroRef = useRef(null);
  const chartInstances = useRef({});

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        const [statsData, nuData, pmData, ftData] = await Promise.all([
          fetch('/admin/api/stats').then(r => r.json()),
          fetch('/admin/api/chart/new-users').then(r => r.json()),
          fetch('/admin/api/chart/pomodoro').then(r => r.json()),
          fetch('/admin/api/features').then(r => r.json())
        ]);

        if (isMounted) {
          setStats(statsData);
          setFeatures(ftData);

          // Initialize Chart.js
          if (window.Chart) {
            // Destroy previous instances if they exist
            if (chartInstances.current.newUsers) chartInstances.current.newUsers.destroy();
            if (chartInstances.current.pomodoro) chartInstances.current.pomodoro.destroy();

            if (chartNewUsersRef.current) {
              chartInstances.current.newUsers = new window.Chart(chartNewUsersRef.current, {
                type: 'bar',
                data: {
                  labels: nuData.labels,
                  datasets: [{
                    data: nuData.values,
                    backgroundColor: 'rgba(79,70,229,.6)',
                    borderColor: '#4F46E5',
                    borderWidth: 1,
                    borderRadius: 6
                  }]
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { ticks: { color: 'rgba(255,255,255,.4)', font: { size: 11 } } },
                    y: { ticks: { color: 'rgba(255,255,255,.4)', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,.05)' } }
                  }
                }
              });
            }

            if (chartPomodoroRef.current) {
              chartInstances.current.pomodoro = new window.Chart(chartPomodoroRef.current, {
                type: 'line',
                data: {
                  labels: pmData.labels,
                  datasets: [{
                    data: pmData.values,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16,185,129,.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#10B981'
                  }]
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { ticks: { color: 'rgba(255,255,255,.4)', font: { size: 11 } } },
                    y: { ticks: { color: 'rgba(255,255,255,.4)', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,.05)' } }
                  }
                }
              });
            }
          }
          setLoading(false);
        }
      } catch (error) {
        console.error("Error fetching overview data", error);
        if (isMounted) setLoading(false);
      }
    };

    fetchData();

    return () => {
      isMounted = false;
      if (chartInstances.current.newUsers) chartInstances.current.newUsers.destroy();
      if (chartInstances.current.pomodoro) chartInstances.current.pomodoro.destroy();
    };
  }, []);

  return (
    <div className="page active" id="page-overview">
      <div className="page-title">📊 Overview &amp; Metrik Aplikasi</div>
      <div className="page-sub">Ringkasan performa real-time Smart-WorkLife</div>
      <hr className="div" />

      <div className="kpi-grid">
        {loading ? (
          <div className="spin">⏳ Memuat data...</div>
        ) : stats?.error ? (
          <p style={{ color: 'var(--red)' }}>{stats.error}</p>
        ) : stats ? (
          <>
            <div className="kpi-card">
              <div className="kpi-icon">👥</div>
              <div className="kpi-label">Total Pengguna Aktif</div>
              <div className="kpi-value">{stats.total_users.toLocaleString()}</div>
              <div className="kpi-delta">+{stats.new_users_week} minggu ini</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">🔥</div>
              <div className="kpi-label">DAU (Hari Ini)</div>
              <div className="kpi-value">{stats.dau.toLocaleString()}</div>
              <div className={`kpi-delta ${stats.dau_delta < 0 ? 'neg' : ''}`}>
                {stats.dau_delta >= 0 ? '+' : ''}{stats.dau_delta} dari kemarin
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">📅</div>
              <div className="kpi-label">MAU (Bulanan)</div>
              <div className="kpi-value">{stats.mau.toLocaleString()}</div>
              <div className="kpi-delta">Bulan ini</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon">🆕</div>
              <div className="kpi-label">User Baru (7 Hari)</div>
              <div className="kpi-value">{stats.new_users_week.toLocaleString()}</div>
              <div className="kpi-delta">Minggu ini</div>
            </div>
          </>
        ) : null}
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-title">📅 Registrasi User Baru (7 Hari)</div>
          <div className="chart-wrap">
            <canvas ref={chartNewUsersRef}></canvas>
          </div>
        </div>
        <div className="chart-card">
          <div className="chart-title">🍅 Tren Sesi Pomodoro Selesai (14 Hari)</div>
          <div className="chart-wrap">
            <canvas ref={chartPomodoroRef}></canvas>
          </div>
        </div>
      </div>

      <div className="chart-card" style={{ marginBottom: '24px' }}>
        <div className="chart-title">🛠️ Penggunaan Fitur Bulan Ini</div>
        <div className="feature-list">
          {loading ? (
            <div className="spin">⏳ Memuat...</div>
          ) : features ? (
            Object.entries(features).map(([k, v]) => {
              const maxVal = Math.max(...Object.values(features), 1);
              return (
                <div className="feature-item" key={k}>
                  <div className="feature-name">{k}</div>
                  <div className="feature-bar-wrap">
                    <div className="feature-bar" style={{ width: `${Math.round(v / maxVal * 100)}%` }}></div>
                  </div>
                  <div className="feature-val">{v}</div>
                </div>
              );
            })
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default Overview;
