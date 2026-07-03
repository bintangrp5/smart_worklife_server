import React, { useEffect, useState } from 'react';
import { UsersIcon, Loader, CheckCircle2, Clock } from 'lucide-react';

const Users = () => {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/admin/api/users')
      .then(r => r.json())
      .then(data => {
        if (!Array.isArray(data)) {
          setError(data.error || 'Unknown error');
        } else {
          setUsers(data);
        }
      })
      .catch(err => setError(err.toString()));
  }, []);

  return (
    <div className="page active" id="page-users">
      <div className="page-title"><UsersIcon style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Data Pengguna Terdaftar</div>
      <div className="page-sub">15 pengguna terbaru yang mendaftar</div>
      <hr className="div" />
      <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '20px' }}>
        <div className="table-wrap">
          <table id="user-table">
            <thead>
              <tr>
                <th>Nama</th>
                <th>Email</th>
                <th>Gender</th>
                <th>Industri</th>
                <th>Bergabung</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {!users && !error ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', color: 'var(--muted)', padding: '30px' }}>
                    <Loader className="animate-spin" style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} size={16} /> Memuat...
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan="6" style={{ color: 'var(--red)' }}>Error: {error}</td>
                </tr>
              ) : (
                users.map((u, i) => (
                  <tr key={i}>
                    <td>{u.full_name}</td>
                    <td style={{ color: 'var(--muted)' }}>{u.email}</td>
                    <td>{u.gender}</td>
                    <td>{u.industry}</td>
                    <td style={{ color: 'var(--muted)' }}>{u.joined}</td>
                    <td>
                      <span className={u.is_verified ? 'badge-ok' : 'badge-no'}>
                        {u.is_verified ? <><CheckCircle2 size={14} style={{ marginRight: '4px', verticalAlign: 'text-bottom' }} /> Terverifikasi</> : <><Clock size={14} style={{ marginRight: '4px', verticalAlign: 'text-bottom' }} /> Belum</>}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Users;
