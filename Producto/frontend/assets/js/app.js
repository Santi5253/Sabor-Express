// Núcleo de la aplicación (Vista): sesión, peticiones REST, navegación e inactividad.
const API_BASE = '/api/v1';
const TIMEOUT_MS = 3 * 60 * 1000;      // 3 minutos (regla de negocio)
const WARN_MS = 2 * 60 * 1000;         // aviso a los 2 minutos

// ---------- Sesión ----------
function getToken() { return localStorage.getItem('token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch (e) { return null; } }
function setSession(data) {
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify({
    id: data.user_id, name: data.name, role: data.role, branch_id: data.branch_id
  }));
}
function clearSession() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

// ---------- Peticiones REST ----------
async function api(path, { method = 'GET', body, raw = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const res = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  });

  if (raw) {
    if (!res.ok) throw new Error('Error ' + res.status);
    return res;
  }
  if (!res.ok) {
    let detail = 'Error ' + res.status;
    try { const d = await res.json(); if (d && d.detail) detail = d.detail; } catch (e) {}
    throw new Error(detail);
  }
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

// ---------- Protección por rol ----------
function requireAuth(allowedRoles) {
  const user = getUser();
  if (!getToken() || !user) { window.location.href = '/login.html'; return null; }
  if (allowedRoles && !allowedRoles.includes(user.role)) { window.location.href = '/login.html'; return null; }
  return user;
}

function logout() {
  clearSession();
  window.location.href = '/login.html';
}

// ---------- Barra superior ----------
const NAV_BY_ROLE = {
  Mesero: [['/take-order.html', 'Take Order'], ['/my-orders.html', 'My Orders'], ['/tables.html', 'Tables']],
  Cajero: [['/close-and-pay.html', 'Close & Pay']],
  Administrador: [['/admin.html', 'Configuration'], ['/reports.html', 'Reports'], ['/tables.html', 'Tables']]
};

function renderTopbar() {
  const user = getUser();
  if (!user) return;
  const links = (NAV_BY_ROLE[user.role] || []).map(([href, label]) =>
    `<a href="${href}" class="${location.pathname === href ? 'active' : ''}">${label}</a>`).join('');
  const bar = document.createElement('div');
  bar.className = 'topbar';
  bar.innerHTML = `
    <div class="brand">🍽️ SaborExpress</div>
    <div class="nav">${links}</div>
    <div class="user">
      <span>${user.name}</span><span class="role">${user.role}</span>
      <button class="sm secondary" onclick="logout()">Log out</button>
    </div>`;
  document.body.prepend(bar);
}

// ---------- Cierre por inactividad (3 min) ----------
let inactivityTimer, warnTimer;
function resetInactivity() {
  clearTimeout(inactivityTimer); clearTimeout(warnTimer);
  warnTimer = setTimeout(() => toast('Your session will expire in 1 minute due to inactivity', 'warn', 6000), WARN_MS);
  inactivityTimer = setTimeout(() => { clearSession(); window.location.href = '/login.html?expired=1'; }, TIMEOUT_MS);
}
function startInactivityMonitor() {
  ['click', 'keydown', 'mousemove', 'scroll'].forEach(e => document.addEventListener(e, resetInactivity));
  resetInactivity();
}

// ---------- Utilidades UI ----------
function toast(msg, type = 'success', ms = 3500) {
  let el = document.getElementById('toast');
  if (!el) { el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; document.body.appendChild(el); }
  el.className = 'toast show ' + type;
  el.textContent = msg;
  setTimeout(() => { el.className = 'toast ' + type; }, ms);
}

function money(n) { return 'S/ ' + Number(n || 0).toFixed(2); }
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

// ---------- Arranque común ----------
function initPage(allowedRoles) {
  const user = requireAuth(allowedRoles);
  if (!user) return null;
  renderTopbar();
  startInactivityMonitor();
  return user;
}
