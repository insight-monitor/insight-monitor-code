import { api } from './api.js';

export const ticketService = {
  getAll: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString();
    return api.get(`/tickets${qs ? '?' + qs : ''}`);
  },
  getById: (id) => api.get(`/tickets/${id}`),
  create:  (data) => api.post('/tickets', data),
  update:  (id, data) => api.put(`/tickets/${id}`, data),
  delete:  (id) => api.delete(`/tickets/${id}`),
  getStats: () => api.get('/tickets/stats'),
  classify: (data) => api.post('/ai/classify', data),
  suggest: (id) => api.get(`/ai/tickets/${id}/suggest`),
};
