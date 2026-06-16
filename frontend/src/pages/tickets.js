import { renderLayout } from '../components/layout.js';
import { ticketService } from '../services/ticket.service.js';
import { showAlert } from '../components/alert.js';

const STATUS_MAP = { OPEN: 'Abierto', IN_PROGRESS: 'En Proceso', CLOSED: 'Cerrado' };
const PRIORITY_MAP = { LOW: 'Baja', MEDIUM: 'Media', HIGH: 'Alta', CRITICAL: 'Crítica' };

export function statusBadge(status) {
  const cls = { OPEN: 'badge-open', IN_PROGRESS: 'badge-progress', CLOSED: 'badge-closed' };
  return `<span class="badge rounded-pill ${cls[status] || ''} px-2 py-1">${STATUS_MAP[status] || status}</span>`;
}

export function priorityBadge(priority) {
  const cls = { LOW: 'badge-low', MEDIUM: 'badge-medium', HIGH: 'badge-high', CRITICAL: 'badge-critical' };
  return `<span class="badge rounded-pill ${cls[priority] || ''} px-2 py-1">${PRIORITY_MAP[priority] || priority}</span>`;
}

export function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });
}

let currentFilters = { status: '', priority: '', search: '', page: 1 };

export async function renderTickets() {
  renderLayout({
    title: 'Tickets',
    content: `
      <div class="filters-bar">
        <div class="input-group" style="max-width:280px">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control" id="searchInput" placeholder="Buscar tickets..." value="${currentFilters.search}" />
        </div>
        <select class="form-select" id="statusFilter" style="max-width:160px">
          <option value="">Todos los estados</option>
          <option value="OPEN" ${currentFilters.status === 'OPEN' ? 'selected' : ''}>Abierto</option>
          <option value="IN_PROGRESS" ${currentFilters.status === 'IN_PROGRESS' ? 'selected' : ''}>En Proceso</option>
          <option value="CLOSED" ${currentFilters.status === 'CLOSED' ? 'selected' : ''}>Cerrado</option>
        </select>
        <select class="form-select" id="priorityFilter" style="max-width:160px">
          <option value="">Todas las prioridades</option>
          <option value="LOW">Baja</option>
          <option value="MEDIUM">Media</option>
          <option value="HIGH">Alta</option>
          <option value="CRITICAL">Crítica</option>
        </select>
        <a href="#/tickets/create" class="btn btn-primary ms-auto">
          <i class="bi bi-plus-lg me-1"></i> Nuevo Ticket
        </a>
      </div>
      <div id="ticketsList"><div class="d-flex justify-content-center py-5"><div class="spinner-border text-primary"></div></div></div>
    `,
  });

  await loadTickets();
  bindFilters();
}

async function loadTickets() {
  try {
    const { data, total, page, limit } = await ticketService.getAll(currentFilters);
    const totalPages = Math.ceil(total / limit);

    document.getElementById('ticketsList').innerHTML = data.length === 0
      ? `<div class="empty-state"><i class="bi bi-inbox"></i><p>No se encontraron tickets</p><a href="#/tickets/create" class="btn btn-primary mt-2">Crear primer ticket</a></div>`
      : `
        <div class="data-table">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Título</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Categoría</th>
                <th>Autor</th>
                <th>Fecha</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${data.map(ticket => `
                <tr onclick="window.location.hash='/tickets/${ticket.id}'">
                  <td>
                    <div class="fw-medium">${escHtml(ticket.title)}</div>
                    <small class="text-muted">${ticket._count?.comments || 0} comentario(s)</small>
                  </td>
                  <td>${statusBadge(ticket.status)}</td>
                  <td>${priorityBadge(ticket.priority)}</td>
                  <td><small>${ticket.category || '—'}</small></td>
                  <td><small>${escHtml(ticket.author?.name || '—')}</small></td>
                  <td><small class="text-muted">${formatDate(ticket.createdAt)}</small></td>
                  <td onclick="event.stopPropagation()">
                    <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${ticket.id}" title="Eliminar">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        ${totalPages > 1 ? pagination(page, totalPages) : ''}
      `;

    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('¿Eliminar este ticket?')) return;
        try {
          await ticketService.delete(btn.dataset.id);
          showAlert('Ticket eliminado', 'success');
          await loadTickets();
        } catch (err) { showAlert(err.message, 'danger'); }
      });
    });

    document.querySelectorAll('.page-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        currentFilters.page = +btn.dataset.page;
        loadTickets();
      });
    });
  } catch (err) {
    document.getElementById('ticketsList').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

function bindFilters() {
  let debounce;
  document.getElementById('searchInput')?.addEventListener('input', (e) => {
    clearTimeout(debounce);
    debounce = setTimeout(() => { currentFilters.search = e.target.value; currentFilters.page = 1; loadTickets(); }, 400);
  });
  document.getElementById('statusFilter')?.addEventListener('change', (e) => {
    currentFilters.status = e.target.value; currentFilters.page = 1; loadTickets();
  });
  document.getElementById('priorityFilter')?.addEventListener('change', (e) => {
    currentFilters.priority = e.target.value; currentFilters.page = 1; loadTickets();
  });
}

function pagination(current, total) {
  const pages = Array.from({ length: total }, (_, i) => i + 1);
  return `
    <nav class="mt-3 d-flex justify-content-center">
      <ul class="pagination pagination-sm">
        ${pages.map(p => `
          <li class="page-item ${p === current ? 'active' : ''}">
            <button class="page-link page-btn" data-page="${p}">${p}</button>
          </li>
        `).join('')}
      </ul>
    </nav>`;
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
