import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8001',
});

// Automatically attach token to every request if it exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Automatically log out on 401
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.clear();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const checkHealth = async () => {
    try {
        const res = await api.get('/health');
        return res.data.status === 'ok';
    } catch (err) {
        return false;
    }
};

export default api;
