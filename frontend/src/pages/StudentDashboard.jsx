import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Stethoscope, CalendarRange, MapPin, Clock, Hospital, User, Settings, Camera, ShieldCheck, X } from 'lucide-react';
import api from '../api';

export default function StudentDashboard() {
  const [assignments, setAssignments] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profile, setProfile] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [forcePasswordChange, setForcePasswordChange] = useState(false);
  
  // Settings Form State
  const [passwordData, setPasswordData] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [isUpdating, setIsUpdating] = useState(false);
  
  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    try {
      const my_user_id = localStorage.getItem('user_id');
      const [asRes, stRes, attRes] = await Promise.all([
        api.get('/assignments/'),
        api.get('/students/'),
        api.get('/attendance/')
      ]);
      
      const myStudent = stRes.data.find(s => s.user_id.toString() === my_user_id);
      if (myStudent) {
         setAssignments(asRes.data.filter(a => a.student_id === myStudent.id));
      }
      setAttendance(attRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    fetchProfile();
    
    // Check if password change is forced
    if (localStorage.getItem('must_change_password') === 'true') {
      setForcePasswordChange(true);
      setShowSettings(true);
    }
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/profile/me');
      setProfile(res.data);
    } catch (err) {
      console.error("Failed to fetch profile", err);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const showMessage = (type, msg) => {
    if (type === 'error') { setError(msg); setSuccess(''); }
    else { setSuccess(msg); setError(''); }
    setTimeout(() => { setError(''); setSuccess(''); }, 5000);
  }

  const handleClockInOut = async (assignmentId, type) => {
    const now = new Date();
    const dateVal = now.toISOString().split('T')[0];
    const timeVal = now.toTimeString().split(' ')[0]; // HH:MM:SS
    
    try {
      await api.post(`/attendance/clock-${type}?assignment_id=${assignmentId}&date_val=${dateVal}&time_${type}=${timeVal}`);
      showMessage('success', `Successfully clocked ${type}!`);
      fetchDashboardData();
    } catch (err) {
      showMessage('error', `Failed to clock ${type}. Check if rotation is currently active.`);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      showMessage('error', 'New passwords do not match');
      return;
    }
    
    setIsUpdating(true);
    try {
      await api.put('/profile/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      showMessage('success', 'Password updated successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      localStorage.setItem('must_change_password', 'false');
      setForcePasswordChange(false);
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to update password');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleProfilePictureUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Convert to Base64
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64String = reader.result;
      try {
        await api.put('/profile/settings', { profile_picture: base64String });
        fetchProfile();
        showMessage('success', 'Profile picture updated!');
      } catch (err) {
        showMessage('error', 'Failed to upload picture');
      }
    };
    reader.readAsDataURL(file);
  };

  // Helper to visually check today's status
  const getTodayRecord = (assignmentId) => {
    const today = new Date().toISOString().split('T')[0];
    return attendance.find(a => a.assignment_id === assignmentId && a.date === today);
  }

  return (
    <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '2.25rem', color: 'var(--text-dark)' }}>
          <div style={{ background: 'var(--primary-gradient)', padding: '10px', borderRadius: '16px', display: 'flex', boxShadow: '0 8px 24px rgba(255, 182, 193, 0.4)' }}>
            <CalendarRange size={28} color="white" />
          </div>
          My Rotations
        </h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => setShowSettings(true)} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px', border: '1.5px solid #FFEBEE', color: 'var(--text-dark)', padding: '10px 20px' }}>
            <Settings size={18} /> Settings
          </button>
          <button onClick={handleLogout} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px', border: '1.5px solid #FFEBEE', color: '#D32F2F', padding: '10px 20px' }}>
            <LogOut size={18} /> Sign Out
          </button>
        </div>
      </header>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="card">
        <h2 style={{ marginBottom: '24px' }}>Active Assignments</h2>
        {assignments.length === 0 ? (
          <p style={{ color: 'var(--text-light)', textAlign: 'center', padding: '32px' }}>You have no active rotation assignments at this time.</p>
        ) : (
          <div style={{ display: 'grid', gap: '24px', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}>
            {assignments.map(a => {
              const todayRecord = getTodayRecord(a.id);
              return (
              <div key={a.id} className="card-hover" style={{ border: '1.5px solid #FFEBEE', borderRadius: '20px', padding: '24px', background: 'white' }}>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-dark)' }}>
                  <Hospital size={22} color="#FFB6C1" /> {a.area?.name}
                </h3>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-dark)' }}>
                    <CalendarRange size={18} color="#FFB6C1" /> 
                    <span style={{ fontWeight: 600 }}>Date:</span> {a.start_date} - {a.end_date}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-dark)' }}>
                    <Clock size={18} color="#FFB6C1" /> 
                    <span style={{ fontWeight: 600 }}>Shift:</span> {a.shift_start_time} - {a.shift_end_time} ({a.shift_type})
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <span className="badge badge-active">{a.status}</span>
                </div>

                <div style={{ background: '#FFF5F7', padding: '20px', borderRadius: '16px', marginTop: '16px', border: '1px dashed #FFB6C1' }}>
                  <h4 style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: '#FF8BA7', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Daily Attendance</h4>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button 
                      className="btn-primary" 
                      style={{ flex: 1, padding: '10px', fontSize: '0.9rem' }}
                      onClick={() => handleClockInOut(a.id, 'in')}
                      disabled={todayRecord?.actual_time_in}
                    >
                      {todayRecord?.actual_time_in ? `In: ${todayRecord.actual_time_in}` : 'Clock In'}
                    </button>
                    <button 
                      className="btn-secondary" 
                      style={{ flex: 1, padding: '10px', fontSize: '0.9rem' }}
                      onClick={() => handleClockInOut(a.id, 'out')}
                      disabled={!todayRecord?.actual_time_in || todayRecord?.actual_time_out}
                    >
                      {todayRecord?.actual_time_out ? `Out: ${todayRecord.actual_time_out}` : 'Clock Out'}
                    </button>
                  </div>
                </div>
              </div>
            )})}
          </div>
        )}
      </div>

      {/* SETTINGS MODAL */}
      {showSettings && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(4px)' }}>
          <div className="card" style={{ maxWidth: '500px', width: '90%', maxHeight: '90vh', overflowY: 'auto', padding: '32px', position: 'relative' }}>
            {!forcePasswordChange && (
              <button onClick={() => setShowSettings(false)} style={{ position: 'absolute', top: '20px', right: '20px', border: 'none', background: 'none', cursor: 'pointer', color: 'var(--text-light)' }}>
                <X size={24} />
              </button>
            )}
            
            {forcePasswordChange ? (
              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <ShieldCheck size={48} color="#FF8BA7" style={{ marginBottom: '16px' }} />
                <h2 style={{ color: 'var(--text-dark)' }}>Security Update Required</h2>
                <p style={{ color: 'var(--text-light)' }}>For your security, please update your default password before proceeding to your dashboard.</p>
              </div>
            ) : (
              <h2 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Settings size={24} color="#FFB6C1" /> Account Settings
              </h2>
            )}

            {error && <div className="alert alert-error" style={{ marginBottom: '20px' }}>{error}</div>}
            {success && <div className="alert alert-success" style={{ marginBottom: '20px' }}>{success}</div>}

            {!forcePasswordChange && (
              <div style={{ marginBottom: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ position: 'relative', marginBottom: '16px' }}>
                  <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: '#FFF5F7', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', border: '3px solid #FFEBEE' }}>
                    {profile?.profile_picture ? (
                      <img src={profile.profile_picture} alt="Profile" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <User size={48} color="#FFB6C1" />
                    )}
                  </div>
                  <label style={{ position: 'absolute', bottom: 0, right: 0, background: 'var(--primary-gradient)', padding: '8px', borderRadius: '50%', cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', display: 'flex' }}>
                    <Camera size={16} color="white" />
                    <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleProfilePictureUpload} />
                  </label>
                </div>
                <h3 style={{ margin: 0 }}>{profile?.username}</h3>
                <p style={{ color: 'var(--text-light)', marginTop: '4px' }}>Member since {profile?.created_at?.split('T')[0]}</p>
              </div>
            )}

            <form onSubmit={handlePasswordChange}>
              <h4 style={{ marginBottom: '16px', color: 'var(--text-dark)', borderBottom: '1.5px solid #FFF5F7', paddingBottom: '8px' }}>Change Password</h4>
              <div style={{ marginBottom: '16px' }}>
                <label className="label">Current Password</label>
                <input 
                  type="password" 
                  className="input-field" 
                  required 
                  value={passwordData.current_password}
                  onChange={e => setPasswordData({...passwordData, current_password: e.target.value})}
                />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label className="label">New Password</label>
                <input 
                  type="password" 
                  className="input-field" 
                  required 
                  value={passwordData.new_password}
                  onChange={e => setPasswordData({...passwordData, new_password: e.target.value})}
                />
              </div>
              <div style={{ marginBottom: '24px' }}>
                <label className="label">Confirm New Password</label>
                <input 
                  type="password" 
                  className="input-field" 
                  required 
                  value={passwordData.confirm_password}
                  onChange={e => setPasswordData({...passwordData, confirm_password: e.target.value})}
                />
              </div>
              <button type="submit" className="btn-primary" style={{ width: '100%' }} disabled={isUpdating}>
                {isUpdating ? 'Updating...' : 'Save Settings'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
