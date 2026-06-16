import { api } from './api.js';

export const authService = {
  async register(data) {
    const res = await api.post('/auth/register', data);
    localStorage.setItem('token', res.token);
    localStorage.setItem('user', JSON.stringify(res.user));
    return res;
  },

  async login(data) {
    const res = await api.post('/auth/login', data);
    localStorage.setItem('token', res.token);
    localStorage.setItem('user', JSON.stringify(res.user));
    return res;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.hash = '/login';
  },

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user') || 'null');
  },
};
