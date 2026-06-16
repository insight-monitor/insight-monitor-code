import { authService } from '../services/auth.service.js';

export function renderLayout({ title, content }) {
  const app = document.getElementById('app');
  const user = authService.getCurrentUser();
  const hash = window.location.hash.slice(1);

  const navItems = [
    { path: '/dashboard',      icon: 'speedometer2',     label: 'Dashboard' },
    { path: '/tickets',        icon: 'ticket-detailed',  label: 'Tickets' },
    { path: '/tickets/create', icon: 'plus-circle',      label: 'Nuevo Ticket' },
  ];

  app.innerHTML = `
    <div class="app-layout">
      <nav class="sidebar" id="sidebar">
        <a href="#/dashboard" class="sidebar-brand">
          <i class="bi bi-headset"></i>
          AI Support Desk
        </a>
        <div class="sidebar-nav">
          <ul>
            ${navItems.map(({ path, icon, label }) => `
              <li><a href="#${path}" class="${hash === path ? 'active' : ''}">
                <i class="bi bi-${icon}"></i> ${label}
              </a></li>
            `).join('')}
          </ul>
        </div>
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">${user?.name?.[0]?.toUpperCase() || 'U'}</div>
            <div>
              <div class="user-name">${user?.name || 'Usuario'}</div>
              <div class="user-role">${user?.role?.toLowerCase() || ''}</div>
            </div>
          </div>
          <button class="btn btn-sm btn-outline-danger w-100" id="logoutBtn">
            <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
          </button>
        </div>
      </nav>

      <main class="main-content">
        <div class="topbar">
          <h2>${title}</h2>
        </div>
        <div class="page-content" id="pageContent">
          ${content}
        </div>
      </main>
    </div>
  `;

  document.getElementById('logoutBtn')?.addEventListener('click', () => authService.logout());
}
