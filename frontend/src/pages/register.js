import { authService } from '../services/auth.service.js';
import { showAlert } from '../components/alert.js';

export function renderRegister() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-brand">
          <i class="bi bi-headset brand-icon"></i>
          <h1>AI Support Desk</h1>
          <p>Crea tu cuenta</p>
        </div>
        <form id="registerForm" novalidate>
          <div class="mb-3">
            <label class="form-label fw-semibold">Nombre completo</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-person"></i></span>
              <input type="text" class="form-control" id="name" placeholder="Tu nombre" required />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Email</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-envelope"></i></span>
              <input type="email" class="form-control" id="email" placeholder="correo@ejemplo.com" required />
            </div>
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold">Contraseña</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-lock"></i></span>
              <input type="password" class="form-control" id="password" placeholder="Mínimo 6 caracteres" required />
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2 fw-semibold" id="submitBtn">
            Crear Cuenta
          </button>
        </form>
        <hr class="my-3" />
        <p class="text-center text-muted mb-0" style="font-size:0.875rem">
          ¿Ya tienes cuenta? <a href="#/login" class="text-primary fw-semibold">Inicia sesión</a>
        </p>
      </div>
    </div>
  `;

  document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creando cuenta...';
    try {
      await authService.register({
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
      });
      window.location.hash = '/dashboard';
    } catch (err) {
      showAlert(err.message, 'danger');
      btn.disabled = false;
      btn.textContent = 'Crear Cuenta';
    }
  });
}
