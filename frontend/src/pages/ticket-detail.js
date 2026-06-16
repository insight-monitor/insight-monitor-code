import { renderLayout } from '../components/layout.js';
import { ticketService } from '../services/ticket.service.js';
import { commentService } from '../services/comment.service.js';
import { showAlert } from '../components/alert.js';
import { statusBadge, priorityBadge, formatDate } from './tickets.js';
import { renderCreateTicket } from './create-ticket.js';
import { authService } from '../services/auth.service.js';

export async function renderTicketDetail(id) {
  renderLayout({ title: 'Detalle del Ticket', content: '<div class="d-flex justify-content-center py-5"><div class="spinner-border text-primary"></div></div>' });

  try {
    const [ticket, comments] = await Promise.all([
      ticketService.getById(id),
      commentService.getByTicket(id),
    ]);
    renderDetail(ticket, comments);
  } catch (err) {
    document.getElementById('pageContent').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

function renderDetail(ticket, comments) {
  const user = authService.getCurrentUser();
  const canEdit = user?.role !== 'USER' || ticket.authorId === user?.id;

  document.getElementById('pageContent').innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
      <a href="#/tickets" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Volver
      </a>
      <div class="d-flex gap-2">
        ${canEdit ? `<button class="btn btn-sm btn-outline-primary" id="editBtn"><i class="bi bi-pencil me-1"></i>Editar</button>` : ''}
        <button class="btn btn-sm btn-outline-info" id="suggestBtn"><i class="bi bi-robot me-1"></i>Sugerir Respuesta</button>
      </div>
    </div>

    <div class="ticket-header">
      <div class="d-flex justify-content-between flex-wrap gap-2 mb-3">
        <div>
          <h4 class="fw-bold mb-1">${escHtml(ticket.title)}</h4>
          <small class="text-muted">
            <i class="bi bi-person me-1"></i>${escHtml(ticket.author?.name || '')} &nbsp;·&nbsp;
            <i class="bi bi-clock me-1"></i>${formatDate(ticket.createdAt)}
          </small>
        </div>
        <div class="d-flex gap-2 align-items-start flex-wrap">
          ${statusBadge(ticket.status)}
          ${priorityBadge(ticket.priority)}
          ${ticket.category ? `<span class="badge bg-secondary rounded-pill">${escHtml(ticket.category)}</span>` : ''}
        </div>
      </div>
      <div class="border-top pt-3">
        <p class="mb-0 text-secondary" style="white-space:pre-wrap">${escHtml(ticket.description)}</p>
      </div>
      ${ticket.assignee ? `
        <div class="border-top pt-2 mt-2">
          <small class="text-muted"><i class="bi bi-person-check me-1"></i>Asignado a: <strong>${escHtml(ticket.assignee.name)}</strong></small>
        </div>` : ''}
    </div>

    <div id="suggestResult" class="d-none mb-3"></div>

    <div class="card">
      <div class="card-header py-3 px-4 fw-semibold d-flex justify-content-between align-items-center">
        <span><i class="bi bi-chat-dots me-2"></i>Comentarios (${comments.length})</span>
        ${canEdit && ticket.status !== 'CLOSED' ? `
          <div class="form-check form-switch mb-0">
            <input class="form-check-input" type="checkbox" id="internalToggle" />
            <label class="form-check-label text-muted" for="internalToggle" style="font-size:0.8rem">Nota interna</label>
          </div>` : ''}
      </div>
      <div class="card-body p-4">
        <div id="commentsList">
          ${comments.length === 0
            ? '<div class="empty-state py-3"><i class="bi bi-chat-square-text" style="font-size:2rem"></i><p class="mt-2">Sin comentarios aún</p></div>'
            : comments.map(c => commentHTML(c, user)).join('')}
        </div>

        ${ticket.status !== 'CLOSED' ? `
          <div class="border-top pt-3 mt-3">
            <form id="commentForm">
              <div class="mb-2">
                <textarea class="form-control" id="commentContent" rows="3" placeholder="Escribe un comentario..."></textarea>
              </div>
              <button type="submit" class="btn btn-primary btn-sm">
                <i class="bi bi-send me-1"></i>Enviar Comentario
              </button>
            </form>
          </div>` : '<div class="text-center text-muted mt-3 py-2 border-top"><small>Este ticket está cerrado</small></div>'}
      </div>
    </div>
  `;

  document.getElementById('editBtn')?.addEventListener('click', () => renderCreateTicket(ticket));

  document.getElementById('suggestBtn')?.addEventListener('click', async () => {
    const btn = document.getElementById('suggestBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>';
    try {
      const { suggestion } = await ticketService.suggest(ticket.id);
      const el = document.getElementById('suggestResult');
      el.className = 'mb-3';
      el.innerHTML = `
        <div class="alert alert-info">
          <div class="d-flex justify-content-between align-items-start mb-1">
            <strong><i class="bi bi-robot me-2"></i>Sugerencia de Respuesta IA</strong>
            <button class="btn-close btn-sm" onclick="this.closest('.alert').parentElement.classList.add('d-none')"></button>
          </div>
          <p class="mb-2 mt-1">${escHtml(suggestion)}</p>
          <button class="btn btn-sm btn-outline-primary" id="useSuggestionBtn">Usar esta respuesta</button>
        </div>`;
      document.getElementById('useSuggestionBtn')?.addEventListener('click', () => {
        const ta = document.getElementById('commentContent');
        if (ta) ta.value = suggestion;
      });
    } catch (err) { showAlert(err.message, 'danger'); }
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-robot me-1"></i>Sugerir Respuesta';
  });

  document.getElementById('commentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const content = document.getElementById('commentContent').value.trim();
    if (!content) return;
    const isInternal = document.getElementById('internalToggle')?.checked || false;
    try {
      const comment = await commentService.create(ticket.id, { content, isInternal });
      const list = document.getElementById('commentsList');
      const empty = list.querySelector('.empty-state');
      if (empty) list.innerHTML = '';
      list.insertAdjacentHTML('beforeend', commentHTML(comment, user));
      document.getElementById('commentContent').value = '';
      if (document.getElementById('internalToggle')) document.getElementById('internalToggle').checked = false;
    } catch (err) { showAlert(err.message, 'danger'); }
  });

  document.querySelectorAll('.delete-comment-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('¿Eliminar comentario?')) return;
      try {
        await commentService.delete(ticket.id, btn.dataset.id);
        btn.closest('.comment-item').remove();
        showAlert('Comentario eliminado', 'success');
      } catch (err) { showAlert(err.message, 'danger'); }
    });
  });
}

function commentHTML(c, currentUser) {
  const canDelete = currentUser?.id === c.authorId || currentUser?.role !== 'USER';
  return `
    <div class="comment-item ${c.isInternal ? 'internal' : ''}">
      <div class="d-flex align-items-start gap-2">
        <div class="comment-avatar">${c.author?.name?.[0]?.toUpperCase() || 'U'}</div>
        <div class="flex-grow-1">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="fw-semibold" style="font-size:0.875rem">${escHtml(c.author?.name || '')}
              ${c.isInternal ? '<span class="badge bg-warning text-dark ms-1" style="font-size:0.7rem">Nota interna</span>' : ''}
            </span>
            <div class="d-flex align-items-center gap-2">
              <span class="comment-meta">${formatDate(c.createdAt)}</span>
              ${canDelete ? `<button class="btn btn-sm text-danger p-0 delete-comment-btn" data-id="${c.id}" title="Eliminar"><i class="bi bi-trash" style="font-size:0.8rem"></i></button>` : ''}
            </div>
          </div>
          <p class="mb-0 text-secondary" style="font-size:0.875rem;white-space:pre-wrap">${escHtml(c.content)}</p>
        </div>
      </div>
    </div>`;
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
