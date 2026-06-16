export function showAlert(message, type = 'success') {
  let container = document.querySelector('.alert-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'alert-container';
    document.body.appendChild(container);
  }

  const id = `alert-${Date.now()}`;
  const icons = { success: 'check-circle-fill', danger: 'exclamation-triangle-fill', warning: 'exclamation-circle-fill', info: 'info-circle-fill' };

  const el = document.createElement('div');
  el.id = id;
  el.className = `alert alert-${type} alert-dismissible d-flex align-items-center shadow-sm`;
  el.innerHTML = `<i class="bi bi-${icons[type] || 'info-circle-fill'} me-2"></i><span>${message}</span><button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>`;
  container.appendChild(el);

  setTimeout(() => el.remove(), 4000);
}
