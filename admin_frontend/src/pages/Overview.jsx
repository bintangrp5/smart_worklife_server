import React, { useEffect, useState, useRef } from 'react';
import { BarChart2, Loader, Users, Flame, Calendar, UserPlus, Timer, Wrench, PlayCircle, Globe, CheckSquare, Droplet, Mic, Activity } from 'lucide-react';

const Overview = ({ theme = 'dark' }) => {
  const [stats, setStats] = useState(null);
  const [features, setFeatures] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [ytEndDate, setYtEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [dtEndDate, setDtEndDate] = useState(new Date().toISOString().split('T')[0]);

  const chartNewUsersRef = useRef(null);
  const chartPomodoroRef = useRef(null);
  const chartYoutubeRef = useRef(null);
  const chartDetikRef = useRef(null);
  const chartInstances = useRef({});

  // Theme Variables for Charts
  const textColorPrimary = theme === 'light' ? '#334155' : 'rgba(255,255,255,0.7)';
  const textColorMuted = theme === 'light' ? '#64748B' : 'rgba(255,255,255,0.4)';
  const gridColor = theme === 'light' ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)';

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

          if (window.Chart) {
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
                  responsive: true, maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { ticks: { color: textColorMuted, font: { size: 11 } } },
                    y: { ticks: { color: textColorMuted, font: { size: 11 } }, grid: { color: gridColor } }
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
                    fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#10B981'
                  }]
                },
                options: {
                  responsive: true, maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { ticks: { color: textColorMuted, font: { size: 11 } } },
                    y: { ticks: { color: textColorMuted, font: { size: 11 } }, grid: { color: gridColor } }
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
    return () => { isMounted = false; };
  }, [theme]);

  // YOUTUBE CHART
  useEffect(() => {
    let isMounted = true;
    fetch(`/admin/api/bigdata-youtube?end=${ytEndDate}`)
      .then(res => { if (!res.ok) throw new Error("API not ready"); return res.json(); })
      .then(data => { if (isMounted) renderYoutubeChart(data); })
      .catch(err => {
        console.log("Using YT mock data fallback", err);
        if (isMounted) renderYoutubeChart({
          labels: ['Makanan Bergetah, Makanan Asli vs Makanan Cokelat...','KING ABDI MASAK BEBEK HITAM VIRAL DI DAPUR TANBOY KUN !!','DJ TIKTOK TERBARU 2025 🎵 DJ CINTA SEBERANG 🎵 DJ...','VIRAL..! RUMAH PALSU LAGI VIRAL DI JAWA BARAT','KUMPULAN LAGU HITS SPOTIFY TIKTOK VIRAL 2025 - LAGU...'],
          views: [59297621, 23971239, 13789123, 10002123, 4001923].map(v => v + Math.floor(Math.random()*1000000)),
          likes: [2012391, 5183921, 1002341, 1209341, 800123].map(v => v + Math.floor(Math.random()*100000))
        });
      });
    return () => { isMounted = false; };
  }, [ytEndDate, theme]);

  // DETIK CHART
  useEffect(() => {
    let isMounted = true;
    fetch(`/admin/api/bigdata-detik?end=${dtEndDate}`)
      .then(res => { if (!res.ok) throw new Error("API not ready"); return res.json(); })
      .then(data => { if (isMounted) renderDetikChart(data); })
      .catch(err => {
        console.log("Using Detik mock data fallback", err);
        if (isMounted) renderDetikChart({
          labels: ['Terkini','Pendidikan','Pemerintah','Wisata','Ekonomi'],
          values: [35, 20, 15, 10, 20].map(v => v + Math.floor(Math.random()*10))
        });
      });
    return () => { isMounted = false; };
  }, [dtEndDate, theme]);

  const renderYoutubeChart = (data) => {
    if (!window.Chart || !chartYoutubeRef.current) return;
    if (chartInstances.current.youtube) chartInstances.current.youtube.destroy();
    
    chartInstances.current.youtube = new window.Chart(chartYoutubeRef.current, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          { label: 'Views', data: data.views, borderColor: '#3B82F6', backgroundColor: 'rgba(59,130,246,0.1)', fill: true, tension: 0.4, yAxisID: 'y' },
          { label: 'Likes', data: data.likes, borderColor: '#F59E0B', backgroundColor: 'rgba(245,158,11,0.1)', fill: true, tension: 0.4, yAxisID: 'y1' }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: true, labels: { color: textColorPrimary, font: { size: 11 }, boxWidth: 12 } },
          tooltip: {
            mode: 'index', intersect: false,
            callbacks: {
              title: function(context) {
                const fullTitle = context[0].label;
                if (fullTitle.length <= 40) return fullTitle;
                const words = fullTitle.split(' ');
                const lines = []; let currentLine = '';
                for (let word of words) {
                    if ((currentLine + word).length > 40) { lines.push(currentLine.trim()); currentLine = word + ' '; } 
                    else { currentLine += word + ' '; }
                }
                lines.push(currentLine.trim()); return lines;
              }
            }
          }
        },
        scales: {
          x: { ticks: { color: textColorMuted, font: { size: 10 }, maxRotation: 45, minRotation: 45, callback: function(value) { const label = this.getLabelForValue(value); return label.length > 15 ? label.substring(0, 15) + '...' : label; } } },
          y: { type: 'linear', display: true, position: 'left', ticks: { color: textColorMuted, font: { size: 11 }, callback: (v) => v/1000 + 'k' }, grid: { color: gridColor } },
          y1: { type: 'linear', display: true, position: 'right', ticks: { color: textColorMuted, font: { size: 11 }, callback: (v) => v/1000 + 'k' }, grid: { drawOnChartArea: false } }
        }
      }
    });
  };

  const renderDetikChart = (data) => {
    if (!window.Chart || !chartDetikRef.current) return;
    if (chartInstances.current.detik) chartInstances.current.detik.destroy();
    
    chartInstances.current.detik = new window.Chart(chartDetikRef.current, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.values,
          backgroundColor: ['#4F46E5','#10B981','#3B82F6','#F59E0B','#EF4444','#8B5CF6'],
          borderWidth: theme === 'light' ? 2 : 0,
          borderColor: theme === 'light' ? '#fff' : 'transparent',
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: textColorPrimary, font: { size: 11 }, padding: 15, boxWidth: 12 } }
        },
        cutout: '70%'
      }
    });
  };

  return (
    <div className="page active" id="page-overview">
      <div className="page-title"><BarChart2 style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Overview &amp; Metrik Aplikasi</div>
      <div className="page-sub">Ringkasan performa real-time Smart-WorkLife</div>
      <hr className="div" />

      <div className="kpi-grid">
        {loading ? (
          <div className="spin"><Loader className="animate-spin" style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Memuat data...</div>
        ) : stats?.error ? (
          <p style={{ color: 'var(--red)' }}>{stats.error}</p>
        ) : stats ? (
          <>
            <div className="kpi-card"><div className="kpi-icon"><Users /></div><div className="kpi-label">Total Pengguna Aktif</div><div className="kpi-value">{stats.total_users.toLocaleString()}</div><div className="kpi-delta">+{stats.new_users_week} minggu ini</div></div>
            <div className="kpi-card"><div className="kpi-icon"><Flame /></div><div className="kpi-label">DAU (Hari Ini)</div><div className="kpi-value">{stats.dau.toLocaleString()}</div><div className={`kpi-delta ${stats.dau_delta < 0 ? 'neg' : ''}`}>{stats.dau_delta >= 0 ? '+' : ''}{stats.dau_delta} dari kemarin</div></div>
            <div className="kpi-card"><div className="kpi-icon"><Calendar /></div><div className="kpi-label">MAU (Bulanan)</div><div className="kpi-value">{stats.mau.toLocaleString()}</div><div className="kpi-delta">Bulan ini</div></div>
            <div className="kpi-card"><div className="kpi-icon"><UserPlus /></div><div className="kpi-label">User Baru (7 Hari)</div><div className="kpi-value">{stats.new_users_week.toLocaleString()}</div><div className="kpi-delta">Minggu ini</div></div>
          </>
        ) : null}
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-title"><Calendar style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={20} /> Registrasi User Baru (7 Hari)</div>
          <div className="chart-wrap"><canvas ref={chartNewUsersRef}></canvas></div>
        </div>
        <div className="chart-card">
          <div className="chart-title"><Timer style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={20} /> Tren Sesi Pomodoro Selesai (14 Hari)</div>
          <div className="chart-wrap"><canvas ref={chartPomodoroRef}></canvas></div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <PlayCircle style={{ marginRight: '8px', verticalAlign: 'text-bottom', color: '#EF4444' }} size={20} /> Top 5 Video YouTube
              </div>
              <div style={{ fontSize: '11px', color: textColorMuted, marginTop: '4px', marginLeft: '28px', fontWeight: 'normal' }}>
                Berdasarkan interaksi (jumlah <strong>Views</strong> &amp; <strong>Likes</strong>) tertinggi
              </div>
            </div>
            <input type="date" value={ytEndDate} onChange={e => setYtEndDate(e.target.value)} style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)', outline: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 'normal' }} />
          </div>
          <div className="chart-wrap"><canvas ref={chartYoutubeRef}></canvas></div>
        </div>
        
        <div className="chart-card">
          <div className="chart-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <Globe style={{ marginRight: '8px', verticalAlign: 'text-bottom', color: '#3B82F6' }} size={20} /> Tren Topik Berita (Detik)
              </div>
              <div style={{ fontSize: '11px', color: textColorMuted, marginTop: '4px', marginLeft: '28px', fontWeight: 'normal' }}>
                Berdasarkan <strong>volume publikasi</strong> (jumlah artikel)
              </div>
            </div>
            <input type="date" value={dtEndDate} onChange={e => setDtEndDate(e.target.value)} style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)', outline: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 'normal' }} />
          </div>
          <div className="chart-wrap" style={{ display: 'flex', justifyContent: 'center' }}><canvas ref={chartDetikRef} style={{ maxWidth: '300px' }}></canvas></div>
        </div>
      </div>

      <div className="chart-card" style={{ marginBottom: '24px' }}>
        <div className="chart-title"><Wrench style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={20} /> Penggunaan Fitur Bulan Ini</div>
        <div className="feature-list">
          {loading ? (
            <div className="spin"><Loader className="animate-spin" style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Memuat...</div>
          ) : features ? (
            Object.entries(features).map(([k, v]) => {
              const maxVal = Math.max(...Object.values(features), 1);
              return (
                <div className="feature-item" key={k}>
                  <div className="feature-name">
                    {(() => {
                      if (k.includes('Pomodoro')) return <Timer size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom', color: '#EF4444' }} />;
                      if (k.includes('Todo')) return <CheckSquare size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom', color: '#10B981' }} />;
                      if (k.includes('Health')) return <Droplet size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom', color: '#3B82F6' }} />;
                      if (k.includes('Notulen')) return <Mic size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom', color: '#8B5CF6' }} />;
                      if (k.includes('Stretching')) return <Activity size={16} style={{ marginRight: '6px', verticalAlign: 'text-bottom', color: '#F59E0B' }} />;
                      return null;
                    })()}
                    {k}
                  </div>
                  <div className="feature-bar-wrap"><div className="feature-bar" style={{ width: `${Math.round(v / maxVal * 100)}%` }}></div></div>
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
