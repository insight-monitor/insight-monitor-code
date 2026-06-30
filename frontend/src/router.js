import { renderLogin } from './pages/login.js';
import { renderRegister } from './pages/register.js';
import { renderDashboard } from './pages/dashboard.js';
import { renderTickets } from './pages/tickets.js';
import { renderTicketDetail } from './pages/ticket-detail.js';
import { renderCreateTicket } from './pages/create-ticket.js';

const PUBLIC_ROUTES = ['/login', '/register'];

const ROUTES = {
  '/login': renderLogin,
  '/register': renderRegister,
  '/dashboard': renderDashboard,
  '/tickets': renderTickets,
  '/tickets/create': renderCreateTicket,
};

export function navigate(path) {
  window.location.hash = path;
}

export function setupRouter() {
  window.addEventListener('hashchange', handleRoute);
  handleRoute();
}

function handleRoute() {
  const hash = window.location.hash.slice(1) || '/login';
  const token = localStorage.getItem('token');

  if (!token && !PUBLIC_ROUTES.includes(hash)) {
    navigate('/login');
    return;
  }

  if (token && PUBLIC_ROUTES.includes(hash)) {
    navigate('/dashboard');
    return;
  }

  const ticketDetailMatch = hash.match(/^\/tickets\/([^/]+)$/) ;
  if (ticketDetailMatch && ticketDetailMatch[1] !== 'create') {
    renderTicketDetail(ticketDetailMatch[1]);
    return;
  }

  const renderer = ROUTES[hash];
  if (renderer) {
    renderer();
  } else {
    navigate(token ? '/dashboard' : '/login');
  }
}
