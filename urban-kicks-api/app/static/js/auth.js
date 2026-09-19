/**
 * ARCHIVO: app/static/js/auth.js
 * PROPÓSITO: Lógica de autenticación del frontend Urban Kicks Admin.
 *
 * Flujo:
 *  1. Usuario envía el formulario de login.
 *  2. Se hace POST a /api/v1/auth/login con las credenciales en JSON.
 *  3. Si OK (200): el token se guarda en una cookie HttpOnly-simulada
 *     y se redirige a /admin/dashboard.
 *     Nota: El servidor también puede set-cookie via /admin/login si se
 *     prefiere, pero aquí lo manejamos en JS para mantener la separación.
 *  4. Si error (401 / red): se muestra el bloque #feedback-alert con el
 *     mensaje de error, respetando los estilos originales del diseño.
 */

// ------------------------------------------------------------------
// togglePasswordVisibility
// Alterna entre tipo 'password' y 'text' en el campo de contraseña.
// Mantiene el comportamiento original del code.html.
// ------------------------------------------------------------------
function togglePasswordVisibility() {
  const input = document.getElementById('corporate-password');
  const icon  = document.getElementById('pwd-icon');
  if (input.type === 'password') {
    input.type        = 'text';
    icon.textContent  = 'visibility_off';
  } else {
    input.type        = 'password';
    icon.textContent  = 'visibility';
  }
}

// ------------------------------------------------------------------
// showFeedback
// Muestra el bloque #feedback-alert con el mensaje y estilo dados.
// type: 'success' | 'error'
// ------------------------------------------------------------------
function showFeedback(message, type) {
  const alert     = document.getElementById('feedback-alert');
  const alertText = document.getElementById('feedback-text');
  const alertIcon = document.getElementById('feedback-icon');

  // Limpiar clases de estado previas
  alert.classList.remove(
    'hidden',
    'bg-acid-green/20', 'text-on-surface',
    'bg-error-container', 'text-on-error-container'
  );

  alertText.textContent = message;

  if (type === 'success') {
    alertIcon.textContent = 'security';
    alert.classList.add('bg-acid-green/20', 'text-on-surface');
  } else {
    alertIcon.textContent = 'error_outline';
    alert.classList.add('bg-error-container', 'text-on-error-container');
  }

  alert.classList.remove('hidden');
}

// ------------------------------------------------------------------
// resetButton
// Restaura el botón de submit a su estado original.
// ------------------------------------------------------------------
function resetButton() {
  const btn      = document.getElementById('submit-btn');
  const btnText  = document.getElementById('btn-text');
  const btnArrow = document.getElementById('btn-arrow');

  btn.disabled = false;
  btnText.textContent = 'INGRESAR AL SISTEMA';
  btnArrow.textContent = 'arrow_forward';
  btnArrow.classList.remove('animate-spin');
  btn.classList.remove('bg-charcoal');
  btn.classList.add('bg-primary');
}

// ------------------------------------------------------------------
// handleFormSubmit
// Captura el submit del formulario y ejecuta el flujo de autenticación
// contra el endpoint POST /api/v1/auth/login.
// ------------------------------------------------------------------
async function handleFormSubmit(e) {
  e.preventDefault();

  const btn      = document.getElementById('submit-btn');
  const btnText  = document.getElementById('btn-text');
  const btnArrow = document.getElementById('btn-arrow');

  // --- Estado: cargando ---
  btn.disabled = true;
  btnText.textContent  = 'VERIFICANDO CREDENCIALES...';
  btnArrow.textContent = 'sync';
  btnArrow.classList.add('animate-spin');

  const username = document.getElementById('corporate-id').value.trim();
  const password = document.getElementById('corporate-password').value;

  try {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // --- Estado: autorizado ---
      btnText.textContent  = 'AUTORIZADO // REDIRIGIENDO';
      btnArrow.textContent = 'check';
      btnArrow.classList.remove('animate-spin');
      btn.classList.remove('bg-primary');
      btn.classList.add('bg-charcoal');

      // Guardar token en localStorage como fallback
      localStorage.setItem('uk_admin_token', data.access_token);

      // Guardar token en cookie para que el servidor pueda leer en /admin/dashboard
      const maxAge = 60 * 60; // 1 hora en segundos
      document.cookie = `uk_admin_token=${data.access_token}; path=/; max-age=${maxAge}; SameSite=Strict`;

      showFeedback('HANDSHAKE COMPLETADO // ACCEDIENDO A DISPONIBILIDAD BOG-01', 'success');

      // Redirigir al dashboard después de 900ms (mantiene la animación del diseño original)
      setTimeout(() => {
        window.location.href = '/admin/dashboard';
      }, 900);

    } else {
      // --- Estado: error de credenciales (401) ---
      btnArrow.classList.remove('animate-spin');
      resetButton();

      const errorMessage = data.detail
        ? `ACCESO DENEGADO // ${data.detail.toUpperCase()}`
        : 'CREDENCIALES INCORRECTAS // INTENTA DE NUEVO';
      showFeedback(errorMessage, 'error');
    }

  } catch (networkError) {
    // --- Estado: error de red ---
    btnArrow.classList.remove('animate-spin');
    resetButton();
    showFeedback('ERROR DE CONEXIÓN // VERIFICA EL SERVIDOR', 'error');
    console.error('[Urban Kicks Auth] Error de red:', networkError);
  }

  return false;
}
