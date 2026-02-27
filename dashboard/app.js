/* ── Config ─────────────────────────────────────────────────────── */
const API_BASE = "https://mehreenasghar5-ai-employee-vault-gold.hf.space";

/* ── Dummy activity feed (shown immediately, replaced on live data) */
const DUMMY_ACTIVITY = [
  { dot: 'dot-green',  text: 'Agent run completed',          tag: 'gold_agent.py',       time: '2 min ago' },
  { dot: 'dot-gold',   text: 'HITL approval requested',      tag: 'hitl.py',             time: '5 min ago' },
  { dot: 'dot-blue',   text: 'Task moved → Done/',           tag: 'mcp_file_ops',        time: '8 min ago' },
  { dot: 'dot-purple', text: 'Audit event written',          tag: 'audit_logger.py',     time: '8 min ago' },
  { dot: 'dot-green',  text: 'Email classified → Business',  tag: 'mcp_email_ops',       time: '12 min ago' },
  { dot: 'dot-gold',   text: 'CEO Briefing generated',       tag: 'ceo_briefing.py',     time: '15 min ago' },
  { dot: 'dot-red',    text: 'Task retried after error',     tag: 'gold_agent.py',       time: '18 min ago' },
  { dot: 'dot-blue',   text: 'Inbox flushed → Needs_Action', tag: 'inbox_watcher',       time: '22 min ago' },
];

/* ── Helpers ────────────────────────────────────────────────────── */
function el(id)        { return document.getElementById(id); }
function set(id, html) { const e = el(id); if (e) e.innerHTML = html; }

function skeleton() {
  return '<span class="skeleton"></span>';
}

/* ── Fetch wrappers ─────────────────────────────────────────────── */
async function getJSON(path) {
  const r = await fetch(API_BASE + path, { signal: AbortSignal.timeout(5000) });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

/* ── Stat cards ─────────────────────────────────────────────────── */
async function loadHealth() {
  try {
    const data = await getJSON('/health');
    const ok   = data.status === 'healthy';
    set('stat-status', `<span class="card-value ${ok ? 'green' : 'red'}">${ok ? 'Healthy' : 'Degraded'}</span>
                        <p class="card-sub">${ok ? 'DB connected · Keys set' : 'Check secrets / DB'}</p>`);
  } catch {
    set('stat-status', '<span class="card-value red">Offline</span><p class="card-sub">API not reachable</p>');
  }
}

async function loadAgentStatus() {
  try {
    const data = await getJSON('/agent/status');
    set('stat-runs',  `<span class="card-value gold">${data.total_runs ?? '—'}</span>
                       <p class="card-sub">Last run ID: ${data.last_run_id ?? '—'}</p>`);
    set('stat-agent', `<span class="card-value">${data.status ?? '—'}</span>
                       <p class="card-sub">${data.last_run_at ? data.last_run_at.slice(0,16).replace('T',' ') : 'No runs yet'}</p>`);
  } catch {
    set('stat-runs',  '<span class="card-value red">—</span><p class="card-sub">API not reachable</p>');
    set('stat-agent', '<span class="card-value red">—</span>');
  }
}

async function loadHITL() {
  try {
    const data  = await getJSON('/hitl/pending');
    const count = Array.isArray(data) ? data.length : (data.count ?? 0);
    const cls   = count > 0 ? 'gold' : 'green';
    set('stat-hitl', `<span class="card-value ${cls}">${count}</span>
                      <p class="card-sub">${count > 0 ? 'Awaiting review' : 'All clear'}</p>`);
  } catch {
    set('stat-hitl', '<span class="card-value red">—</span>');
  }
}

async function loadMCP() {
  try {
    const data  = await getJSON('/mcp/tools');
    const count = data.count ?? (Array.isArray(data.tools) ? data.tools.length : '—');
    set('stat-mcp', `<span class="card-value gold">${count}</span>
                     <p class="card-sub">Registered tools</p>`);
  } catch {
    set('stat-mcp', '<span class="card-value red">—</span>');
  }
}

async function loadErrors() {
  /* /agent/status exposes error count if available, else fall back to 0 */
  try {
    const data = await getJSON('/agent/status');
    const err  = data.total_errors ?? data.errors ?? 0;
    const cls  = err > 0 ? 'red' : 'green';
    set('stat-errors', `<span class="card-value ${cls}">${err}</span>
                        <p class="card-sub">${err > 0 ? 'Check /Logs' : 'No errors'}</p>`);
  } catch {
    set('stat-errors', '<span class="card-value red">—</span>');
  }
}

/* ── Activity feed ──────────────────────────────────────────────── */
function renderActivity(items) {
  const list = el('activity-list');
  if (!list) return;
  list.innerHTML = items.map(item => `
    <li class="activity-item">
      <span class="activity-dot ${item.dot}"></span>
      <span class="activity-text">${item.text}<span class="tag">${item.tag}</span></span>
      <span class="activity-time">${item.time}</span>
    </li>`).join('');
  set('activity-count', items.length);
}

/* ── Quick-action buttons ────────────────────────────────────────── */
function setupButtons() {
  el('btn-swagger')?.addEventListener('click', () =>
    window.open(`${API_BASE}/docs`, '_blank'));

  el('btn-health')?.addEventListener('click', async () => {
    el('btn-health').textContent = '⏳ Checking…';
    try {
      const d = await getJSON('/health');
      alert(`Status: ${d.status}\n\n${JSON.stringify(d.checks, null, 2)}`);
    } catch { alert('API not reachable — is the server running?'); }
    el('btn-health').textContent = '🩺 Health Check';
  });

  el('btn-mcp')?.addEventListener('click', async () => {
    el('btn-mcp').textContent = '⏳ Loading…';
    try {
      const d = await getJSON('/mcp/tools');
      const names = (d.tools ?? []).map(t => `• ${t.name}`).join('\n');
      alert(`${d.count} MCP Tools registered:\n\n${names}`);
    } catch { alert('API not reachable.'); }
    el('btn-mcp').textContent = '🔧 MCP Tools';
  });

  el('btn-agent')?.addEventListener('click', async () => {
    el('btn-agent').textContent = '⏳ Loading…';
    try {
      const d = await getJSON('/agent/status');
      alert(`Agent Status\n\nStatus:     ${d.status}\nLast Run:   ${d.last_run_id}\nTotal Runs: ${d.total_runs}\nTimestamp:  ${d.last_run_at ?? 'N/A'}`);
    } catch { alert('API not reachable.'); }
    el('btn-agent').textContent = '🤖 Agent Status';
  });
}

/* ── Timestamp ──────────────────────────────────────────────────── */
function setTimestamp() {
  const now = new Date();
  set('last-updated', now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
}

/* ── Init ───────────────────────────────────────────────────────── */
async function init() {
  /* Show skeletons while loading */
  ['stat-status','stat-hitl','stat-mcp','stat-runs','stat-errors'].forEach(id =>
    set(id, skeleton()));

  /* Render dummy activity immediately */
  renderActivity(DUMMY_ACTIVITY);

  /* Fire all stat fetches in parallel */
  await Promise.allSettled([
    loadHealth(),
    loadAgentStatus(),
    loadHITL(),
    loadMCP(),
    loadErrors(),
  ]);

  setTimestamp();
  setupButtons();
}

document.addEventListener('DOMContentLoaded', init);

/* ── Auto-refresh every 30 s ─────────────────────────────────────── */
setInterval(() => {
  loadHealth();
  loadAgentStatus();
  loadHITL();
  loadMCP();
  loadErrors();
  setTimestamp();
}, 30_000);
