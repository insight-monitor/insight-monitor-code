import { api } from './api.js';

export const commentService = {
  getByTicket: (ticketId) => api.get(`/tickets/${ticketId}/comments`),
  create:      (ticketId, data) => api.post(`/tickets/${ticketId}/comments`, data),
  update:      (ticketId, commentId, data) => api.put(`/tickets/${ticketId}/comments/${commentId}`, data),
  delete:      (ticketId, commentId) => api.delete(`/tickets/${ticketId}/comments/${commentId}`),
};
