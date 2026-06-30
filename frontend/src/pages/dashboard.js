import { renderLayout } from '../components/layout.js';
import { ticketService } from '../services/ticket.service.js';
import { statusBadge, priorityBadge, formatDate } from './tickets.js';

export async function renderDashboard() {
  renderLayout({ title: 'Dashboard', content: '<div class="d-flex justify-content-center py-5"><div class="spinner-border text-primary"></div></div>' });

  try {
    const [{ data: tickets }, stats] = await Promise.all([
      ticketService.getAll({ limit: 5 }),
      ticketService.getStats(),
    ]);

    const counts = { OPEN: 0, IN_PROGRESS: 0, CLOSED: 0 };
    stats.byStatus.forEach(({ status, _count }) => { counts[status] = _count.status; });
    const total = Object.values(counts).reduce((a, b) => a + b, 0);

    document.getElementById('pageContent').innerHTML = `
      <div class="row g-3 mb-4">
        ${statCard('Total Tickets', total, 'layers', '#6366f1', '#ede9fe')}
        ${statCard('Abiertos', counts.OPEN, 'folder2-open', '#3b82f6', '#dbeafe')}
        ${statCard('En Proceso', counts.IN_PROGRESS, 'arrow-repeat', '#f59e0b', '#fef3c7')}
        ${statCard('Cerrados', counts.CLOSED, 'check-circle', '#10b981', '#d1fae5')}
      </div>

      <div class="row g-3">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center py-3 px-4">
              <span class="fw-semibold">Tickets Recientes</span>
              <a href="#/tickets" class="btn btn-sm btn-outline-primary">Ver todos</a>
            </div>
            <div class="data-table">
              ${tickets.length === 0 ? '<div class="empty-state"><i class="bi bi-inbox"></i><p>No hay tickets aún</p></div>' : `
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Título</th>
                    <th>Estado</th>
                    <th>Prioridad</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  ${tickets.map(t => `
                    <tr onclick="window.location.hash='/tickets/${t.id}'" style="cursor:pointer">
                      <td>
                        <div class="fw-medium">${escHtml(t.title)}</div>
                        <small class="text-muted">${escHtml(t.author?.name || '')}</small>
                      </td>
                      <td>${statusBadge(t.status)}</td>
                      <td>${priorityBadge(t.priority)}</td>
                      <td><small class="text-muted">${formatDate(t.createdAt)}</small></td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>`}
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card h-100">
            <div class="card-header py-3 px-4 fw-semibold">Distribución por Prioridad</div>
            <div class="card-body">
              ${buildPriorityBars(stats.byPriority, total)}
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    document.getElementById('pageContent').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

function statCard(label, value, icon, color, bg) {
  return `
    <div class="col-6 col-xl-3">
      <div class="stat-card">
        <div class="stat-icon" style="background:${bg};color:${color}">
          <i class="bi bi-${icon}"></i>
        </div>
        <div>
          <div class="stat-label">${label}</div>
          <div class="stat-value">${value}</div>
        </div>
      </div>
    </div>`;
}

function buildPriorityBars(byPriority, total) {
  const cfg = {
    LOW:      { label: 'Baja',     color: '#10b981' },
    MEDIUM:   { label: 'Media',    color: '#f59e0b' },
    HIGH:     { label: 'Alta',     color: '#ef4444' },
    CRITICAL: { label: 'Crítica',  color: '#7c3aed' },
  };
  return Object.entries(cfg).map(([key, { label, color }]) => {
    const item = byPriority.find(b => b.priority === key);
    const count = item?._count?.priority || 0;
    const pct = total ? Math.round((count / total) * 100) : 0;
    return `
      <div class="mb-3">
        <div class="d-flex justify-content-between mb-1">
          <small class="fw-medium">${label}</small>
          <small class="text-muted">${count} (${pct}%)</small>
        </div>
        <div class="progress" style="height:8px">
          <div class="progress-bar" style="width:${pct}%;background:${color}"></div>
        </div>
      </div>`;
  }).join('');
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
