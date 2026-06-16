const BASE = '/api';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  };

  const res = await fetch(`${BASE}${endpoint}`, config);

  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.hash = '/login';
    throw new Error('Sesión expirada');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: `Error ${res.status}` }));
    throw new Error(err.message || `Error ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get:    (url)        => request(url),
  post:   (url, data)  => request(url, { method: 'POST',   body: JSON.stringify(data) }),
  put:    (url, data)  => request(url, { method: 'PUT',    body: JSON.stringify(data) }),
  patch:  (url, data)  => request(url, { method: 'PATCH',  body: JSON.stringify(data) }),
  delete: (url)        => request(url, { method: 'DELETE' }),
};
