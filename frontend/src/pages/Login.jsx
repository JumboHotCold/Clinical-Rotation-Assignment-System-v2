import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, RefreshCcw, Activity } from 'lucide-react';
import api, { checkHealth } from '../api';
import logo from '../assets/SPUS-logo1.webp';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking'); // 'checking', 'online', 'offline'
  const navigate = useNavigate();

  useEffect(() => {
    const verifyServer = async () => {
      const isAlive = await checkHealth();
      setServerStatus(isAlive ? 'online' : 'offline');
    };

    verifyServer();
    const interval = setInterval(verifyServer, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Pre-validation for students (C- prefix or Email)
    const isEmail = username.includes('@');
    if (username !== 'admin' && !username.startsWith('C-') && !isEmail) {
      setError('Enter your Student ID (C-XXXX) or Email Address');
      setLoading(false);
      return;
    }

    try {
      const response = await api.post('/auth/token', {
        username,
        password,
        role: "not_used_here"
      });

      const { access_token, role, user_id, must_change_password } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      localStorage.setItem('user_id', user_id);
      localStorage.setItem('must_change_password', must_change_password);

      if (role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/student');
      }
    } catch (err) {
      if (!err.response) {
        setError('Cannot connect to Backend Server. Please ensure uvicorn is running on port 8001.');
        setServerStatus('offline');
      } else if (err.response.status === 401) {
        setError('Invalid username or password');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const isInvalidFormat = username !== '' && username !== 'admin' && !username.startsWith('C-') && !username.includes('@');

  return (
    <div className="flex-center">
      <div className="card card-hover" style={{ maxWidth: '420px', width: '100%', textAlign: 'center', padding: '40px 32px' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
          <img src={logo} alt="SPUS Logo" style={{ maxWidth: '80px', height: 'auto' }} />
        </div>
        <h2 style={{ marginBottom: '8px', fontSize: '1.75rem', fontWeight: '700' }}>Welcome Back</h2>
        <p style={{ color: 'var(--text-light)', marginBottom: '32px', fontSize: '0.95rem' }}>Clinical Rotation Management</p>

        {/* Server Status Indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          marginBottom: '24px',
          padding: '8px 16px',
          borderRadius: '12px',
          fontSize: '0.85rem',
          fontWeight: 600,
          background: serverStatus === 'online' ? '#E8F5E9' : serverStatus === 'offline' ? '#FFEBEE' : '#F5F5F5',
          color: serverStatus === 'online' ? '#2E7D32' : serverStatus === 'offline' ? '#C62828' : '#757575',
          border: `1px solid ${serverStatus === 'online' ? '#C8E6C9' : serverStatus === 'offline' ? '#FFCDD2' : '#E0E0E0'}`
        }}>
          {serverStatus === 'checking' && <RefreshCcw size={14} className="animate-spin" />}
          {serverStatus === 'online' && <Activity size={14} />}
          {serverStatus === 'offline' && <AlertCircle size={14} />}
          {serverStatus === 'checking' ? 'Checking connection...' : serverStatus === 'online' ? 'Backend System Online' : 'Backend System Offline'}
        </div>

        {error && (
          <div className="alert alert-error" style={{ fontSize: '0.9rem', textAlign: 'left' }}>
            <AlertCircle size={18} /> {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ textAlign: 'left' }}>
          <div style={{ marginBottom: '16px' }}>
            <label className="label">Username or Student ID</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. C-2023-001 or admin"
              value={username}
              onChange={(e) => {
                let val = e.target.value;
                if (val.toLowerCase().startsWith('c') && !val.includes('@')) {
                  val = val.toUpperCase();
                } else if (val === 'admin') {
                  val = val.toLowerCase();
                }
                setUsername(val);
                setError('');
              }}
              style={{
                borderColor: isInvalidFormat ? '#FFB6C1' : '',
                marginBottom: isInvalidFormat ? '4px' : '20px'
              }}
              required
            />
            {isInvalidFormat && (
              <span style={{ color: '#D32F2F', fontSize: '0.8rem', display: 'block', marginBottom: '16px' }}>
                Please enter a valid Student ID or Email
              </span>
            )}
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label className="label">Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In to Portal'}
          </button>
        </form>

      </div>
    </div>
  );
}
