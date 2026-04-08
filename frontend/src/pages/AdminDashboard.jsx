import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, UsersRound, Hospital, CalendarRange, Plus, AlertTriangle, Trash2, Edit, BarChart, Stethoscope, UserCheck, UserX, Users } from 'lucide-react';
import Swal from 'sweetalert2';
import api from '../api';
import AreaStudentsView from '../components/AreaStudentsView';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('assignments');
  const navigate = useNavigate();

  // Data state
  const [students, setStudents] = useState([]);
  const [areas, setAreas] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [stats, setStats] = useState({ total_students: 0, total_areas: 0, active_assignments: 0 });

  // Form state
  const [newStudent, setNewStudent] = useState({ student_id_number: 'C-', first_name: '', last_name: '', program: 'BS Nursing', year_level: '2nd Year', contact_email: '', contact_phone: '' });
  const [newArea, setNewArea] = useState({ name: '', max_capacity: 1 });
  const [newAssignment, setNewAssignment] = useState({ student_id: '', area_id: '', start_date: '', end_date: '', shift_start_time: '08:00', shift_end_time: '16:00', shift_type: 'Morning' });

  // Edit Area State
  const [editingAreaId, setEditingAreaId] = useState(null);
  const [editAreaName, setEditAreaName] = useState('');
  const [editAreaMaxCapacity, setEditAreaMaxCapacity] = useState(1);

  // UI state
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchDashboardData = async () => {
    try {
      // Use Promise.allSettled to prevent one error from blocking all data
      const [stRes, arRes, asRes, statRes] = await Promise.allSettled([
        api.get('/students/'),
        api.get('/areas/'),
        api.get('/assignments/'),
        api.get('/analytics/dashboard')
      ]);

      if (stRes.status === 'fulfilled') setStudents(stRes.value.data);
      if (arRes.status === 'fulfilled') setAreas(arRes.value.data);
      if (asRes.status === 'fulfilled') setAssignments(asRes.value.data);
      if (statRes.status === 'fulfilled') setStats(statRes.value.data);

    } catch (err) {
      console.error("Dashboard fetch error:", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    Swal.fire({
      title: 'Sign Out?',
      text: 'Are you sure you want to sign out?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#D32F2F',
      cancelButtonColor: '#6B7280',
      confirmButtonText: 'Yes, sign out',
      cancelButtonText: 'Cancel'
    }).then((result) => {
      if (result.isConfirmed) {
        localStorage.clear();
        navigate('/login');
      }
    });
  };

  const showMessage = (type, msg) => {
    if (type === 'error') { setError(msg); setSuccess(''); }
    else { setSuccess(msg); setError(''); }
    setTimeout(() => { setError(''); setSuccess(''); }, 5000);
  }

  // --- STUDENT CRUD ---
  const handleCreateStudent = async (e) => {
    e.preventDefault();
    try {
      await api.post('/students/', newStudent);
      showMessage('success', 'Student created successfully');
      setNewStudent({ ...newStudent, student_id_number: 'C-', first_name: '', last_name: '', contact_email: '', contact_phone: '' });
      fetchDashboardData();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to create student');
    }
  };

  const handleDeleteStudent = async (studentId, studentName) => {
    const result = await Swal.fire({
      title: 'Delete Student?',
      html: `<div style="text-align: left;">
        <p><strong>${studentName}</strong></p>
        <p style="color: #d32f2f; margin-top: 12px; font-weight: 500;">⚠️ This action is irreversible and will:</p>
        <ul style="text-align: left; margin: 8px 0;">
          <li>Delete the student profile</li>
          <li>Delete all related assignments</li>
          <li>Delete all attendance records</li>
        </ul>
      </div>`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d32f2f',
      cancelButtonColor: '#757575',
      confirmButtonText: 'Yes, Delete Student',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    });

    if (!result.isConfirmed) return;

    // Show loading state
    Swal.fire({
      title: 'Deleting...',
      allowOutsideClick: false,
      allowEscapeKey: false,
      didOpen: async () => {
        Swal.showLoading();
        try {
          await api.delete(`/students/${studentId}`);
          Swal.fire({
            title: 'Deleted!',
            text: 'Student and all associated records have been permanently deleted.',
            icon: 'success',
            confirmButtonColor: '#4caf50'
          });
          fetchDashboardData();
        } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete student. Please try again.';
          Swal.fire({
            title: 'Error',
            text: errorMessage,
            icon: 'error',
            confirmButtonColor: '#d32f2f'
          });
          console.error('Delete student error:', err);
        }
      }
    });
  }

  const handleToggleStatus = async (student) => {
    try {
      const newStatus = student.status === 'Active' ? 'Inactive' : 'Active';
      await api.put(`/students/${student.id}`, { status: newStatus });
      showMessage('success', `Student status updated to ${newStatus}`);
      fetchDashboardData();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to update student status');
    }
  }

  // --- AREA CRUD ---
  const handleCreateArea = async (e) => {
    e.preventDefault();
    try {
      await api.post('/areas/', newArea);
      showMessage('success', 'Area created successfully');
      setNewArea({ name: '', max_capacity: 1 });
      fetchDashboardData();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to create area');
    }
  };

  const handleDeleteArea = async (areaId, areaName) => {
    const result = await Swal.fire({
      title: 'Delete Clinical Facility?',
      html: `<div style="text-align: left;">
        <p><strong>${areaName}</strong></p>
        <p style="color: #d32f2f; margin-top: 12px; font-weight: 500;">⚠️ This action is irreversible and will:</p>
        <ul style="text-align: left; margin: 8px 0;">
          <li>Delete the facility</li>
          <li>Delete all related assignments</li>
          <li>Delete all student attendance records for this facility</li>
        </ul>
        <p style="color: #ff6f00; margin-top: 12px; font-weight: 500;">ℹ️ Ensure no active assignments exist before deleting.</p>
      </div>`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d32f2f',
      cancelButtonColor: '#757575',
      confirmButtonText: 'Yes, Delete Facility',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    });

    if (!result.isConfirmed) return;

    // Show loading state
    Swal.fire({
      title: 'Deleting...',
      allowOutsideClick: false,
      allowEscapeKey: false,
      didOpen: async () => {
        Swal.showLoading();
        try {
          await api.delete(`/areas/${areaId}`);
          Swal.fire({
            title: 'Deleted!',
            text: 'Clinical facility and all associated records have been permanently deleted.',
            icon: 'success',
            confirmButtonColor: '#4caf50'
          });
          fetchDashboardData();
        } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete facility. Please try again.';
          Swal.fire({
            title: 'Error',
            text: errorMessage,
            icon: 'error',
            confirmButtonColor: '#d32f2f'
          });
          console.error('Delete area error:', err);
        }
      }
    });
  }

  const startEditArea = (area) => {
    setEditingAreaId(area.id);
    setEditAreaName(area.name);
    setEditAreaMaxCapacity(area.max_capacity);
  };

  const cancelEditArea = () => {
    setEditingAreaId(null);
    setEditAreaName('');
    setEditAreaMaxCapacity(1);
  };

  const saveEditArea = async (id) => {
    try {
      await api.put(`/areas/${id}`, { name: editAreaName, max_capacity: editAreaMaxCapacity });
      showMessage('success', 'Facility updated successfully');
      setEditingAreaId(null);
      fetchDashboardData();
    } catch (err) {
      showMessage('error', 'Failed to update facility');
    }
  };

  // --- ASSIGNMENT CRUD ---
  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    try {
      // Ensure times have seconds for strict SQL time format
      const payload = {
        ...newAssignment,
        shift_start_time: newAssignment.shift_start_time.length === 5 ? newAssignment.shift_start_time + ':00' : newAssignment.shift_start_time,
        shift_end_time: newAssignment.shift_end_time.length === 5 ? newAssignment.shift_end_time + ':00' : newAssignment.shift_end_time,
      }
      await api.post('/assignments/', payload);
      showMessage('success', 'Assignment created successfully! Conflict check passed.');
      fetchDashboardData();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Conflict Detected: Failed to create assignment');
    }
  };

  const handleDeleteAssignment = async (assignmentId, studentName, areaName) => {
    const result = await Swal.fire({
      title: 'Delete Assignment?',
      html: `<div style="text-align: left;">
        <p><strong>${studentName}</strong> → <strong>${areaName}</strong></p>
        <p style="color: #d32f2f; margin-top: 12px; font-weight: 500;">⚠️ This action is irreversible and will:</p>
        <ul style="text-align: left; margin: 8px 0;">
          <li>Remove the rotation assignment</li>
          <li>Delete all attendance records for this assignment</li>
        </ul>
      </div>`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d32f2f',
      cancelButtonColor: '#757575',
      confirmButtonText: 'Yes, Delete Assignment',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    });

    if (!result.isConfirmed) return;

    // Show loading state
    Swal.fire({
      title: 'Deleting...',
      allowOutsideClick: false,
      allowEscapeKey: false,
      didOpen: async () => {
        Swal.showLoading();
        try {
          await api.delete(`/assignments/${assignmentId}`);
          Swal.fire({
            title: 'Deleted!',
            text: 'Assignment has been permanently deleted.',
            icon: 'success',
            confirmButtonColor: '#4caf50'
          });
          fetchDashboardData();
        } catch (err) {
          const errorMessage = err.response?.data?.detail || 'Failed to delete assignment. Please try again.';
          Swal.fire({
            title: 'Error',
            text: errorMessage,
            icon: 'error',
            confirmButtonColor: '#d32f2f'
          });
          console.error('Delete assignment error:', err);
        }
      }
    });
  }

  return (
    <div style={{ padding: '32px', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '2.25rem', color: 'var(--text-dark)' }}>
          <div style={{ background: 'var(--primary-gradient)', padding: '10px', borderRadius: '16px', display: 'flex', boxShadow: '0 8px 24px rgba(255, 182, 193, 0.4)' }}>
            <Stethoscope size={28} color="white" />
          </div>
          Admin Portal
        </h1>
        <button onClick={handleLogout} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px', border: '1.5px solid #FFEBEE', color: '#D32F2F', padding: '10px 20px' }}>
          <LogOut size={18} /> Sign Out
        </button>
      </header>

      {/* Analytics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '40px' }}>
        <div className="card" style={{ padding: '24px', borderLeft: '6px solid #FFB6C1' }}>
          <div style={{ color: 'var(--text-light)', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>Total Students</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-dark)' }}>{stats.total_students}</div>
        </div>
        <div className="card" style={{ padding: '24px', borderLeft: '6px solid #FFB6C1' }}>
          <div style={{ color: 'var(--text-light)', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>Clinical Areas</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-dark)' }}>{stats.total_areas}</div>
        </div>
        <div className="card" style={{ padding: '24px', borderLeft: '4px solid #FF8BA7', background: 'linear-gradient(to right, #FFF5F7, #FFFFFF)' }}>
          <div style={{ color: 'var(--text-light)', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>Active Assignments</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#FF8BA7' }}>{stats.active_assignments}</div>
        </div>
      </div>

      {error && <div className="alert alert-error"><AlertTriangle size={20} /> {error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="tabs">
        <div className={`tab ${activeTab === 'assignments' ? 'active' : ''}`} onClick={() => setActiveTab('assignments')}>
          <CalendarRange size={18} /> Rotations
        </div>
        <div className={`tab ${activeTab === 'students' ? 'active' : ''}`} onClick={() => setActiveTab('students')}>
          <UsersRound size={18} /> Student Database
        </div>
        <div className={`tab ${activeTab === 'areas' ? 'active' : ''}`} onClick={() => setActiveTab('areas')}>
          <Hospital size={18} /> Clinical Facilities
        </div>
        <div className={`tab ${activeTab === 'areaStudents' ? 'active' : ''}`} onClick={() => setActiveTab('areaStudents')}>
          <Users size={18} /> Area Assignments
        </div>
      </div>

      <div className="card">
        {/* ASSIGNMENTS TAB */}
        {activeTab === 'assignments' && (
          <div>
            <h2 style={{ marginBottom: '24px' }}>Create Rotation Assignment</h2>
            <form onSubmit={handleCreateAssignment} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', alignItems: 'end', marginBottom: '40px' }}>
              <div>
                <label className="label">Student</label>
                <select className="input-field" style={{ marginBottom: 0 }} required value={newAssignment.student_id} onChange={e => setNewAssignment({ ...newAssignment, student_id: e.target.value })}>
                  <option value="">Select Student...</option>
                  {students.map(s => <option key={s.id} value={s.id}>{s.first_name} {s.last_name} ({s.student_id_number})</option>)}
                </select>
              </div>
              <div>
                <label className="label">Clinical Area</label>
                <select className="input-field" style={{ marginBottom: 0 }} required value={newAssignment.area_id} onChange={e => setNewAssignment({ ...newAssignment, area_id: e.target.value })}>
                  <option value="">Select Area...</option>
                  {areas.map(a => <option key={a.id} value={a.id}>{a.name} (Cap: {a.max_capacity})</option>)}
                </select>
              </div>
              <div>
                <label className="label">Date Range</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input type="date" className="input-field" style={{ marginBottom: 0 }} required value={newAssignment.start_date} onChange={e => setNewAssignment({ ...newAssignment, start_date: e.target.value })} />
                  <input type="date" className="input-field" style={{ marginBottom: 0 }} required value={newAssignment.end_date} onChange={e => setNewAssignment({ ...newAssignment, end_date: e.target.value })} />
                </div>
              </div>
              <div style={{ gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
                <div>
                  <label className="label">Time Range</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input type="time" className="input-field" style={{ marginBottom: 0 }} required value={newAssignment.shift_start_time} onChange={e => setNewAssignment({ ...newAssignment, shift_start_time: e.target.value })} />
                    <input type="time" className="input-field" style={{ marginBottom: 0 }} required value={newAssignment.shift_end_time} onChange={e => setNewAssignment({ ...newAssignment, shift_end_time: e.target.value })} />
                  </div>
                </div>
                <div>
                  <label className="label">Shift Details</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <select className="input-field" style={{ marginBottom: 0, width: '60%' }} value={newAssignment.shift_type} onChange={e => setNewAssignment({ ...newAssignment, shift_type: e.target.value })}>
                      <option>Morning</option>
                      <option>Afternoon</option>
                      <option>Night</option>
                    </select>
                    <button type="submit" className="btn-primary" style={{ flexGrow: 1 }}><Plus size={18} /> Assign</button>
                  </div>
                </div>
              </div>
            </form>

            <h3 style={{ borderBottom: '2.5px solid #FFF5F7', paddingBottom: '16px', marginBottom: '24px', color: 'var(--text-dark)' }}>Active Rotation Schedule</h3>
            <div className="table-container">
              <table>
                <thead><tr><th>Student</th><th>Facility</th><th>Schedule</th><th>Times</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  {assignments.map(a => (
                    <tr key={a.id}>
                      <td><div style={{ fontWeight: 600 }}>{a.student?.first_name} {a.student?.last_name}</div><div style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>{a.student?.student_id_number}</div></td>
                      <td>{a.area?.name}</td>
                      <td>{a.start_date}<br /><span style={{ color: 'var(--text-light)', fontSize: '0.85rem' }}>to {a.end_date}</span></td>
                      <td>{a.shift_start_time} - {a.shift_end_time}<br /><span style={{ color: 'var(--text-light)', fontSize: '0.85rem' }}>({a.shift_type})</span></td>
                      <td><span className="badge badge-active">{a.status}</span></td>
                      <td>
                        <button onClick={() => handleDeleteAssignment(a.id, `${a.student?.first_name} ${a.student?.last_name}`, a.area?.name)} style={{ background: 'none', border: 'none', color: '#E53935', cursor: 'pointer', padding: '8px' }}><Trash2 size={18} /></button>
                      </td>
                    </tr>
                  ))}
                  {assignments.length === 0 && <tr><td colSpan="6" style={{ textAlign: 'center', padding: '32px' }}>No active assignments found</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* STUDENTS TAB */}
        {activeTab === 'students' && (
          <div>
            <h2 style={{ marginBottom: '24px' }}>Register New Student</h2>
            <form onSubmit={handleCreateStudent} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', alignItems: 'end', marginBottom: '40px' }}>
              <div>
                <label className="label">Student ID (C-)</label>
                <input type="text" className="input-field" style={{ marginBottom: 0 }} required value={newStudent.student_id_number} onChange={e => setNewStudent({ ...newStudent, student_id_number: e.target.value.toUpperCase() })} />
              </div>
              <div>
                <label className="label">First Name</label>
                <input type="text" className="input-field" style={{ marginBottom: 0 }} required value={newStudent.first_name} onChange={e => setNewStudent({ ...newStudent, first_name: e.target.value })} />
              </div>
              <div>
                <label className="label">Last Name</label>
                <input type="text" className="input-field" style={{ marginBottom: 0 }} required value={newStudent.last_name} onChange={e => setNewStudent({ ...newStudent, last_name: e.target.value })} />
              </div>
              <div>
                <label className="label">Program</label>
                <select className="input-field" style={{ marginBottom: 0 }} required value={newStudent.program} onChange={e => setNewStudent({ ...newStudent, program: e.target.value })}>
                  <option>BS Nursing</option>
                </select>
              </div>
              <div>
                <label className="label">Year Level</label>
                <select className="input-field" style={{ marginBottom: 0 }} required value={newStudent.year_level} onChange={e => setNewStudent({ ...newStudent, year_level: e.target.value })}>
                  <option>2nd Year</option>
                  <option>3rd Year</option>
                  <option>4th Year</option>
                </select>
              </div>
              <div>
                <label className="label">Contact Email</label>
                <input type="email" className="input-field" style={{ marginBottom: 0 }} required value={newStudent.contact_email} onChange={e => setNewStudent({ ...newStudent, contact_email: e.target.value })} />
              </div>
              <button type="submit" className="btn-primary" style={{ marginBottom: 0 }}><Plus size={18} /> Create Profile</button>
            </form>

            <h3 style={{ borderBottom: '2.5px solid #FFF5F7', paddingBottom: '16px', marginBottom: '24px', color: 'var(--text-dark)' }}>Student Database</h3>
            <div className="table-container">
              <table>
                <thead><tr><th>ID</th><th>Name</th><th>Program</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  {students.map(s => (
                    <tr key={s.id}>
                      <td style={{ fontWeight: 600 }}>{s.student_id_number}</td>
                      <td>{s.first_name} {s.last_name}</td>
                      <td>{s.program} ({s.year_level})</td>
                      <td>
                        <span className={`badge ${s.status === 'Active' ? 'badge-active' : 'badge-inactive'}`}>
                          {s.status}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '4px' }}>
                          <button
                            onClick={() => handleToggleStatus(s)}
                            title={s.status === 'Active' ? 'Deactivate Student' : 'Activate Student'}
                            style={{ background: 'none', border: 'none', color: s.status === 'Active' ? '#9E9E9E' : '#4CAF50', cursor: 'pointer', padding: '8px' }}
                          >
                            {s.status === 'Active' ? <UserX size={18} /> : <UserCheck size={18} />}
                          </button>
                          <button
                            onClick={() => handleDeleteStudent(s.id, `${s.first_name} ${s.last_name} (${s.student_id_number})`)}
                            title="Delete Permanently (Irreversible)"
                            style={{ background: 'none', border: 'none', color: '#E53935', cursor: 'pointer', padding: '8px' }}
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {students.length === 0 && <tr><td colSpan="5" style={{ textAlign: 'center', padding: '32px' }}>No students found</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* AREAS TAB */}
        {activeTab === 'areas' && (
          <div>
            <h2 style={{ marginBottom: '24px' }}>Add Clinical Facility</h2>
            <form onSubmit={handleCreateArea} style={{ display: 'flex', gap: '20px', alignItems: 'end', marginBottom: '40px' }}>
              <div style={{ flexGrow: 2 }}>
                <label className="label">Facility/Area Name</label>
                <input type="text" className="input-field" style={{ marginBottom: 0 }} required value={newArea.name} onChange={e => setNewArea({ ...newArea, name: e.target.value })} />
              </div>
              <div style={{ flexGrow: 1 }}>
                <label className="label">Max Capacity (Students)</label>
                <input type="number" min="1" className="input-field" style={{ marginBottom: 0 }} required value={newArea.max_capacity} onChange={e => setNewArea({ ...newArea, max_capacity: parseInt(e.target.value) })} />
              </div>
              <button type="submit" className="btn-primary" style={{ marginBottom: 0 }}><Plus size={18} /> Add Facility</button>
            </form>

            <h3 style={{ borderBottom: '2.5px solid #FFF5F7', paddingBottom: '16px', marginBottom: '24px', color: 'var(--text-dark)' }}>Registered Facilities</h3>
            <div className="table-container">
              <table>
                <thead><tr><th>Facility Name</th><th>Capacity limit</th><th>Actions</th></tr></thead>
                <tbody>
                  {areas.map(a => (
                    <tr key={a.id}>
                      {editingAreaId === a.id ? (
                        <>
                          <td>
                            <input type="text" className="input-field" style={{ marginBottom: 0 }} value={editAreaName} onChange={e => setEditAreaName(e.target.value)} />
                          </td>
                          <td>
                            <input type="number" min="1" className="input-field" style={{ marginBottom: 0 }} value={editAreaMaxCapacity} onChange={e => setEditAreaMaxCapacity(parseInt(e.target.value))} />
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '4px' }}>
                              <button onClick={() => saveEditArea(a.id)} style={{ background: 'none', border: 'none', color: '#4CAF50', cursor: 'pointer', padding: '8px', fontWeight: 'bold' }} title="Save">Save</button>
                              <button onClick={cancelEditArea} style={{ background: 'none', border: 'none', color: '#9E9E9E', cursor: 'pointer', padding: '8px', fontWeight: 'bold' }} title="Cancel">Cancel</button>
                            </div>
                          </td>
                        </>
                      ) : (
                        <>
                          <td style={{ fontWeight: 600 }}>{a.name}</td>
                          <td><span className="badge badge-inactive">Max: {a.max_capacity}</span></td>
                          <td>
                            <div style={{ display: 'flex', gap: '4px' }}>
                              <button onClick={() => startEditArea(a)} style={{ background: 'none', border: 'none', color: '#1976D2', cursor: 'pointer', padding: '8px' }} title="Edit">
                                <Edit size={18} />
                              </button>
                              <button onClick={() => handleDeleteArea(a.id, a.name)} style={{ background: 'none', border: 'none', color: '#E53935', cursor: 'pointer', padding: '8px' }} title="Delete">
                                <Trash2 size={18} />
                              </button>
                            </div>
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                  {areas.length === 0 && <tr><td colSpan="3" style={{ textAlign: 'center', padding: '32px' }}>No facilities found</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Area Students Tab */}
      {activeTab === 'areaStudents' && (
        <div className="card">
          <AreaStudentsView adminView={true} />
        </div>
      )}
    </div>
  );
}
