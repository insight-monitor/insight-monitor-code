import { renderLayout } from '../components/layout.js';
import { ticketService } from '../services/ticket.service.js';
import { showAlert } from '../components/alert.js';

export function renderCreateTicket(ticketToEdit = null) {
  const isEdit = Boolean(ticketToEdit);
  const t = ticketToEdit || {};

  renderLayout({
    title: isEdit ? 'Editar Ticket' : 'Nuevo Ticket',
    content: `
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header py-3 px-4">
              <h6 class="mb-0 fw-semibold">${isEdit ? 'Editar Ticket' : 'Crear Nuevo Ticket'}</h6>
            </div>
            <div class="card-body p-4">
              <form id="ticketForm" novalidate>
                <div class="mb-3">
                  <label class="form-label fw-semibold">Título <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" id="title" placeholder="Describe el problema brevemente" value="${escHtml(t.title || '')}" required />
                </div>
                <div class="mb-3">
                  <label class="form-label fw-semibold">Descripción <span class="text-danger">*</span></label>
                  <textarea class="form-control" id="description" rows="5" placeholder="Describe el problema en detalle..." required>${escHtml(t.description || '')}</textarea>
                </div>
                <div class="row g-3 mb-3">
                  <div class="col-md-4">
                    <label class="form-label fw-semibold">Prioridad</label>
                    <select class="form-select" id="priority">
                      <option value="LOW" ${t.priority === 'LOW' ? 'selected' : ''}>Baja</option>
                      <option value="MEDIUM" ${(!t.priority || t.priority === 'MEDIUM') ? 'selected' : ''}>Media</option>
                      <option value="HIGH" ${t.priority === 'HIGH' ? 'selected' : ''}>Alta</option>
                      <option value="CRITICAL" ${t.priority === 'CRITICAL' ? 'selected' : ''}>Crítica</option>
                    </select>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label fw-semibold">Categoría</label>
                    <select class="form-select" id="category">
                      <option value="">Sin categoría</option>
                      <option value="Técnico" ${t.category === 'Técnico' ? 'selected' : ''}>Técnico</option>
                      <option value="Red" ${t.category === 'Red' ? 'selected' : ''}>Red</option>
                      <option value="Seguridad" ${t.category === 'Seguridad' ? 'selected' : ''}>Seguridad</option>
                      <option value="Facturación" ${t.category === 'Facturación' ? 'selected' : ''}>Facturación</option>
                      <option value="General" ${t.category === 'General' ? 'selected' : ''}>General</option>
                    </select>
                  </div>
                  ${isEdit ? `
                  <div class="col-md-4">
                    <label class="form-label fw-semibold">Estado</label>
                    <select class="form-select" id="status">
                      <option value="OPEN" ${t.status === 'OPEN' ? 'selected' : ''}>Abierto</option>
                      <option value="IN_PROGRESS" ${t.status === 'IN_PROGRESS' ? 'selected' : ''}>En Proceso</option>
                      <option value="CLOSED" ${t.status === 'CLOSED' ? 'selected' : ''}>Cerrado</option>
                    </select>
                  </div>` : ''}
                </div>
                <div id="aiResult" class="d-none mb-3"></div>
                <div class="d-flex gap-2 flex-wrap">
                  <button type="submit" class="btn btn-primary" id="submitBtn">
                    <i class="bi bi-check-lg me-1"></i> ${isEdit ? 'Guardar Cambios' : 'Crear Ticket'}
                  </button>
                  <button type="button" class="btn btn-outline-secondary" id="aiBtn" title="Clasificar con IA">
                    <i class="bi bi-robot me-1"></i> Clasificar con IA
                  </button>
                  <a href="${isEdit ? '#/tickets/' + t.id : '#/tickets'}" class="btn btn-outline-secondary ms-auto">
                    Cancelar
                  </a>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    `,
  });

  document.getElementById('aiBtn').addEventListener('click', async () => {
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    if (!title || !description) { showAlert('Ingresa título y descripción para clasificar', 'warning'); return; }

    const btn = document.getElementById('aiBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Analizando...';
    try {
      const result = await ticketService.classify({ title, description });
      const priorityValues = { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', CRITICAL: 'CRITICAL' };
      if (priorityValues[result.priority]) document.getElementById('priority').value = result.priority;
      if (result.category) {
        const opt = [...document.getElementById('category').options].find(o => o.value === result.category);
        if (opt) document.getElementById('category').value = result.category;
      }
      const aiResult = document.getElementById('aiResult');
      aiResult.className = 'mb-3';
      aiResult.innerHTML = `
        <div class="alert alert-info py-2 mb-0">
          <i class="bi bi-robot me-2"></i><strong>Análisis IA:</strong> ${escHtml(result.analysis)}
          <span class="badge bg-secondary ms-2">Confianza: ${result.confidence}</span>
        </div>`;
    } catch (err) { showAlert(err.message, 'danger'); }
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-robot me-1"></i> Clasificar con IA';
  });

  document.getElementById('ticketForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    if (!title || !description) { showAlert('Título y descripción son requeridos', 'warning'); return; }

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;

    const payload = {
      title,
      description,
      priority: document.getElementById('priority').value,
      category: document.getElementById('category').value || undefined,
    };
    if (isEdit && document.getElementById('status')) {
      payload.status = document.getElementById('status').value;
    }

    try {
      if (isEdit) {
        await ticketService.update(t.id, payload);
        showAlert('Ticket actualizado', 'success');
        window.location.hash = `/tickets/${t.id}`;
      } else {
        const created = await ticketService.create(payload);
        showAlert('Ticket creado exitosamente', 'success');
        window.location.hash = `/tickets/${created.id}`;
      }
    } catch (err) {
      showAlert(err.message, 'danger');
      btn.disabled = false;
    }
  });
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
