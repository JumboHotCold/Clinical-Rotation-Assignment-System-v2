import { useState, useEffect } from 'react';
import { Search, MapPin, Clock, Users, ChevronDown, ChevronUp, Hospital } from 'lucide-react';
import api from '../api';

export default function AreaStudentsView({ adminView = false, onlyMyAreas = false }) {
    const [areasData, setAreasData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedAreas, setExpandedAreas] = useState({});
    const [expandedSchedules, setExpandedSchedules] = useState({});

    // Search and filter state
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all'); // 'all', 'area', 'date', 'name'
    const [selectedDate, setSelectedDate] = useState('');

    useEffect(() => {
        fetchAreaStudents();
    }, []);

    const fetchAreaStudents = async () => {
        setLoading(true);
        setError('');
        try {
            let endpoint;
            if (adminView) {
                // Admin can see all areas
                endpoint = '/areas/';
                const response = await api.get(endpoint);
                const areas = response.data;

                // Fetch students for each area
                const areasWithStudents = await Promise.all(
                    areas.map(async (area) => {
                        try {
                            const studentsRes = await api.get(`/areas/${area.id}/students`);
                            return studentsRes.data;
                        } catch (err) {
                            console.error(`Failed to fetch students for area ${area.id}`, err);
                            return {
                                area_id: area.id,
                                area_name: area.name,
                                max_capacity: area.max_capacity,
                                schedules: []
                            };
                        }
                    })
                );

                setAreasData(areasWithStudents);
            } else {
                // Student can only see their areas
                const response = await api.get('/students/me/coassignees');
                setAreasData(response.data);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load area students');
            console.error('Fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const toggleAreaExpand = (areaId) => {
        setExpandedAreas(prev => ({
            ...prev,
            [areaId]: !prev[areaId]
        }));
    };

    const toggleScheduleExpand = (scheduleKey) => {
        setExpandedSchedules(prev => ({
            ...prev,
            [scheduleKey]: !prev[scheduleKey]
        }));
    };

    const getScheduleKey = (area_id, schedule) => {
        return `${area_id}-${schedule.shift_type}-${schedule.shift_start_time}-${schedule.start_date}`;
    };

    // Filter functions
    const matches = (student, schedule, area) => {
        const searchLower = searchTerm.toLowerCase();

        if (!searchTerm && !selectedDate) return true;

        const studentMatchesName =
            student.first_name.toLowerCase().includes(searchLower) ||
            student.last_name.toLowerCase().includes(searchLower) ||
            student.student_id_number.toLowerCase().includes(searchLower);

        const areaMatchesName = area.area_name.toLowerCase().includes(searchLower);
        const dateMatches = !selectedDate || schedule.start_date === selectedDate;

        if (filterType === 'all') {
            return (studentMatchesName || areaMatchesName) && dateMatches;
        } else if (filterType === 'area') {
            return areaMatchesName && dateMatches;
        } else if (filterType === 'date') {
            return dateMatches;
        } else if (filterType === 'name') {
            return studentMatchesName && dateMatches;
        }

        return true;
    };

    // Get today's date in YYYY-MM-DD format
    const getTodayDate = () => {
        const today = new Date();
        return today.toISOString().split('T')[0];
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr + 'T00:00:00');
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const formatTime = (timeStr) => {
        if (!timeStr) return '';
        const [hours, minutes] = timeStr.split(':');
        const hour = parseInt(hours);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:${minutes} ${ampm}`;
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '1rem', color: 'var(--text-light)' }}>Loading area assignments...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '20px', background: '#FFEBEE', color: '#C62828', borderRadius: '8px' }}>
                {error}
            </div>
        );
    }

    return (
        <div>
            <h2 style={{ marginBottom: '24px' }}>
                {adminView ? 'All Areas & Student Assignments' : 'My Assigned Areas & Co-Students'}
            </h2>

            {/* Search and Filter Section */}
            <div style={{ marginBottom: '24px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
                    <div style={{ position: 'relative' }}>
                        <Search size={18} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-light)' }} />
                        <input
                            type="text"
                            placeholder="Search by student name or area..."
                            className="input-field"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{ paddingLeft: '40px' }}
                        />
                    </div>

                    <div>
                        <select
                            className="input-field"
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                        >
                            <option value="all">Filter: All</option>
                            <option value="area">Filter: By Area Name</option>
                            <option value="name">Filter: By Student Name</option>
                            <option value="date">Filter: By Date</option>
                        </select>
                    </div>

                    <div>
                        <input
                            type="date"
                            className="input-field"
                            value={selectedDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                            placeholder="Filter by date..."
                        />
                    </div>
                </div>
            </div>

            {/* Areas List */}
            {areasData.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                    {adminView
                        ? 'No areas found. Create a clinical area first.'
                        : 'You have no active area assignments yet.'
                    }
                </div>
            ) : (
                <div style={{ display: 'grid', gap: '16px' }}>
                    {areasData.map((area) => {
                        const isExpanded = expandedAreas[area.area_id];

                        // Filter schedules based on search
                        const filteredSchedules = area.schedules.filter(schedule =>
                            schedule.students.some(student => matches(student, schedule, area))
                        );

                        // Count total students in area
                        const totalStudentsInArea = area.schedules.reduce((sum, schedule) =>
                            sum + schedule.students.length, 0
                        );

                        if (filterType !== 'all' && selectedDate && filteredSchedules.length === 0) {
                            return null; // Skip if no matches
                        }

                        return (
                            <div
                                key={area.area_id}
                                className="card"
                                style={{
                                    overflow: 'hidden',
                                    border: '1px solid #FFE0E6'
                                }}
                            >
                                {/* Area Header */}
                                <div
                                    onClick={() => toggleAreaExpand(area.area_id)}
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        padding: '20px',
                                        cursor: 'pointer',
                                        background: 'linear-gradient(to right, #FFF5F7, #FFFFFF)',
                                        borderBottom: isExpanded ? '2px solid #FFB6C1' : 'none'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
                                        <div style={{
                                            background: 'var(--primary-gradient)',
                                            color: 'white',
                                            width: '40px',
                                            height: '40px',
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            <Hospital size={20} />
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-dark)' }}>
                                                {area.area_name}
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>
                                                <Users size={14} style={{ marginRight: '4px', display: 'inline' }} />
                                                {totalStudentsInArea} student{totalStudentsInArea !== 1 ? 's' : ''} •
                                                Capacity: {area.max_capacity}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ color: 'var(--text-light)' }}>
                                        {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                                    </div>
                                </div>

                                {/* Schedules List */}
                                {isExpanded && (
                                    <div style={{ padding: '0' }}>
                                        {filteredSchedules.length === 0 ? (
                                            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-light)' }}>
                                                No matching schedules found
                                            </div>
                                        ) : (
                                            filteredSchedules.map((schedule, scheduleIdx) => {
                                                const scheduleKey = getScheduleKey(area.area_id, schedule);
                                                const scheduleExpanded = expandedSchedules[scheduleKey];
                                                const filteredStudents = schedule.students.filter(student =>
                                                    matches(student, schedule, area)
                                                );

                                                return (
                                                    <div
                                                        key={scheduleIdx}
                                                        style={{
                                                            borderTop: scheduleIdx > 0 ? '1px solid #F0F0F0' : 'none'
                                                        }}
                                                    >
                                                        {/* Schedule Header */}
                                                        <div
                                                            onClick={() => toggleScheduleExpand(scheduleKey)}
                                                            style={{
                                                                display: 'flex',
                                                                justifyContent: 'space-between',
                                                                alignItems: 'center',
                                                                padding: '16px 20px',
                                                                background: '#FAFAFA',
                                                                cursor: 'pointer',
                                                                borderLeft: '4px solid #FFB6C1'
                                                            }}
                                                        >
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flex: 1 }}>
                                                                <div>
                                                                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-dark)' }}>
                                                                        <Clock size={16} style={{ marginRight: '6px', display: 'inline' }} />
                                                                        {formatTime(schedule.shift_start_time)} - {formatTime(schedule.shift_end_time)}
                                                                    </div>
                                                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>
                                                                        {schedule.shift_type} • {formatDate(schedule.start_date)} to {formatDate(schedule.end_date)}
                                                                    </div>
                                                                </div>
                                                                <div style={{
                                                                    background: '#FFE0E6',
                                                                    color: '#C2185B',
                                                                    padding: '4px 12px',
                                                                    borderRadius: '16px',
                                                                    fontSize: '0.85rem',
                                                                    fontWeight: 600
                                                                }}>
                                                                    {filteredStudents.length} student{filteredStudents.length !== 1 ? 's' : ''}
                                                                </div>
                                                            </div>
                                                            <div style={{ color: 'var(--text-light)' }}>
                                                                {scheduleExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                                                            </div>
                                                        </div>

                                                        {/* Students List */}
                                                        {scheduleExpanded && (
                                                            <div style={{ padding: '16px 20px', background: '#FFFFFF' }}>
                                                                <div style={{ display: 'grid', gap: '12px' }}>
                                                                    {filteredStudents.map((student, studentIdx) => (
                                                                        <div
                                                                            key={studentIdx}
                                                                            style={{
                                                                                padding: '12px 16px',
                                                                                background: '#FFF9FA',
                                                                                borderRadius: '8px',
                                                                                borderLeft: '3px solid #FFB6C1',
                                                                                display: 'flex',
                                                                                justifyContent: 'space-between',
                                                                                alignItems: 'flex-start'
                                                                            }}
                                                                        >
                                                                            <div style={{ flex: 1 }}>
                                                                                <div style={{ fontWeight: 700, color: 'var(--text-dark)', marginBottom: '4px' }}>
                                                                                    {student.first_name} {student.last_name}
                                                                                </div>
                                                                                <div style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>
                                                                                    ID: {student.student_id_number}
                                                                                </div>
                                                                                <div style={{ fontSize: '0.8rem', color: 'var(--text-light)', marginTop: '4px' }}>
                                                                                    {student.program} • {student.year_level}
                                                                                </div>
                                                                                <div style={{ fontSize: '0.8rem', color: '#1976D2', marginTop: '4px' }}>
                                                                                    📧 {student.contact_email} • 📱 {student.contact_phone}
                                                                                </div>
                                                                            </div>
                                                                            <div style={{
                                                                                textAlign: 'right',
                                                                                paddingLeft: '16px'
                                                                            }}>
                                                                                {student.status === 'Active' ? (
                                                                                    <span style={{
                                                                                        display: 'inline-block',
                                                                                        background: '#E8F5E9',
                                                                                        color: '#2E7D32',
                                                                                        padding: '4px 12px',
                                                                                        borderRadius: '16px',
                                                                                        fontSize: '0.8rem',
                                                                                        fontWeight: 600
                                                                                    }}>
                                                                                        Active
                                                                                    </span>
                                                                                ) : (
                                                                                    <span style={{
                                                                                        display: 'inline-block',
                                                                                        background: '#FFEBEE',
                                                                                        color: '#C62828',
                                                                                        padding: '4px 12px',
                                                                                        borderRadius: '16px',
                                                                                        fontSize: '0.8rem',
                                                                                        fontWeight: 600
                                                                                    }}>
                                                                                        Inactive
                                                                                    </span>
                                                                                )}
                                                                            </div>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })
                                        )}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
