import React, { useEffect, useState } from 'react';
import { Star, Loader } from 'lucide-react';

const Ratings = () => {
  const [ratings, setRatings] = useState(null);

  useEffect(() => {
    fetch('/admin/api/ratings')
      .then(r => r.json())
      .then(data => setRatings(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="page active" id="page-ratings">
      <div className="page-title"><Star style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Feedback &amp; Rating Pengguna</div>
      <div className="page-sub">Kepuasan pengguna per fitur</div>
      <hr className="div" />
      <div id="ratings-content" style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '24px' }}>
        {!ratings ? (
          <div className="spin"><Loader className="animate-spin" style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={16} /> Memuat...</div>
        ) : !Array.isArray(ratings) || ratings.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--muted)', padding: '32px' }}>
            <div style={{ marginBottom: '12px' }}><Star size={40} color="var(--muted)" /></div>
            <div style={{ fontSize: '15px', fontWeight: 600, marginBottom: '8px' }}>Belum ada rating</div>
            <div style={{ fontSize: '13px' }}>Data rating akan muncul setelah pengguna memberi ulasan dari aplikasi Flutter</div>
          </div>
        ) : (
          ratings.map((r, i) => {
            const stars = Array.from({ length: Math.round(r.avg_rating) }, (_, idx) => (
              <Star key={idx} size={14} fill="var(--yellow)" color="var(--yellow)" style={{ marginRight: '2px', verticalAlign: 'middle' }} />
            ));
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600 }}>{r.feature}</div>
                  <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{r.total} ulasan</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '4px' }}>{stars}</div>
                  <div style={{ fontSize: '13px', color: 'var(--yellow)', fontWeight: 600 }}>{r.avg_rating}/5.0</div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Ratings;
