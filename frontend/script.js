'use strict';

/* ---------- Configuração ----------
   Caminhos conforme os include_router do main.py.
   Formato real de GET /dashboard/{line_id} (LineSnapshotSchema):
   { id, name, target_oee, ideal_production_rate, current_production_rate, total_runtime_minutes,
     simulation_status: "idle" | "running",
     machines: [{ id, name, base_failure_rate, wear_level, last_start_time, last_stop_time,
                  maintenance_start_at, maintenance_end_at, status: "idle" | "stop" | "maintenance" | "production" }],
     active_op: { id, code, product_name, quantity_planned, quantity_produced, quantity_good, quantity_bad, status, ... } | null }
   O snapshot não traz OEE nem paradas: o painel os busca nos endpoints abaixo. */
const CONFIG = {
  API_BASE: location.protocol === 'file:' ? 'http://localhost:8000' : '',  // vazio = mesma origem (front servido pelo FastAPI)
  POLL_MS: 5000,
  TIMEOUT_MS: 4000,
  DEFAULT_LINE: 1,
  ENDPOINTS: {
    lines: '/api/lines/',
    dashboard: id => `/api/dashboard/${id}`,
    downtime: '/api/events/',  // lista as paradas de todas as linhas; o painel filtra pela linha
    oee: null,                 // ex.: id => `/oee/${id}/latest` (ainda não existe no backend)
  },
};

const state = {
  lineId: localStorage.getItem('line') || CONFIG.DEFAULT_LINE,
  demo: false,
  gen: 0,
  ctrl: null,
  timer: null,
  hasData: false,
};

/* ---------- Utilitários ---------- */
const $ = s => document.querySelector(s);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const num = v => (v == null || v === '' || Number.isNaN(Number(v)) ? null : Number(v));
const fmt = v => (v == null ? '—' : v.toLocaleString('pt-BR', { maximumFractionDigits: 1 }));

// Monta elementos sem innerHTML: textos entram como texto, nunca como HTML.
function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') n.className = v;
    else if (k === 'style') Object.assign(n.style, v);
    else if (k === 'role' || k.startsWith('aria-')) n.setAttribute(k, v);
    else n[k] = v;
  }
  kids.flat().filter(c => c != null && c !== false).forEach(c => n.append(c));
  return n;
}

// Datas sem fuso (ex.: "2026-10-15T10:00:00") são tratadas como UTC, como o backend grava.
function parseDate(s) {
  if (!s) return null;
  const str = String(s);
  const d = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(str) ? str : str + 'Z');
  return Number.isNaN(d.getTime()) ? null : d;
}
const fmtTime = s => parseDate(s)?.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) ?? null;
function fmtDur(sec) {
  sec = Math.max(0, Math.round(sec));
  if (sec < 60) return `${sec} s`;
  const m = Math.floor(sec / 60);
  return m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${m % 60} min`;
}

// Aceita status em maiúsculas ou minúsculas (os enums do backend costumam vir em maiúsculas).
const STATUS = {
  production: ['run', 'Produzindo'], running: ['run', 'Em operação'],
  idle: ['idle', 'Ociosa'],
  maintenance: ['maint', 'Em manutenção'],
  stop: ['fail', 'Parada'], stopped: ['fail', 'Interrompida'], failure: ['fail', 'Com falha'],
  broken: ['fail', 'Com falha'], down: ['fail', 'Com falha'], error: ['fail', 'Com falha'],
};
const statusOf = s => STATUS[String(s ?? '').toLowerCase()] || ['idle', s ? String(s) : 'Sem status'];

const TYPE_LABEL = {
  failure: 'Falha', preventive_maintenance: 'Manutenção preventiva',
  inspection: 'Inspeção', undefined_production: 'Produção indefinida',
};
const SEVERITY = { low: 'baixa', mid: 'média', high: 'alta' };
const typeLabel = t => TYPE_LABEL[String(t ?? '').toLowerCase()] || String(t ?? '').toLowerCase().replace(/_/g, ' ');

/* ---------- Normalização ---------- */
const OEE_KEYS = ['availability', 'performance', 'quality', 'oee'];
function normalize(d, downtime, oeeRaw) {
  const line = d.line || d;                       // o snapshot real é plano: os campos da linha ficam na raiz
  const raw = oeeRaw || d.oee || null;
  // Os valores já vêm em 0-100 (o oee_service multiplica por 100). O schema de OEE grafa "perfomance".
  const oee = raw ? Object.fromEntries(OEE_KEYS.map(k => [k, num(raw[k] ?? (k === 'performance' ? raw.perfomance : null))])) : null;
  return { line, op: d.active_op || null, machines: d.machines || [], oee, downtime, target: num(line.target_oee) ?? 85 };
}

/* ---------- Renderização ---------- */
function renderLine(line) {
  $('#line-name').textContent = line.name || `Linha ${state.lineId}`;
  const cur = num(line.current_production_rate), ideal = num(line.ideal_production_rate), runtime = num(line.total_runtime_minutes);
  const parts = [];
  if (cur != null && ideal != null) parts.push(`Ritmo atual ${fmt(cur)} de ${fmt(ideal)} peças/min`);
  if (runtime != null) parts.push(`${fmtDur(runtime * 60)} de operação acumulada`);
  $('#line-meta').textContent = parts.join(', ');

  const badge = $('#line-status');
  if (line.simulation_status) {
    const [cls, label] = statusOf(line.simulation_status);
    badge.className = `badge is-${cls}`;
    badge.textContent = label;
    badge.hidden = false;
  } else badge.hidden = true;
}

function renderOee(o, target) {
  for (const k of OEE_KEYS) {
    const v = o ? o[k] : null;
    $(`#v-${k}`).textContent = v == null ? '—' : `${fmt(v)}%`;
    $(`#b-${k}`).style.width = `${v == null ? 0 : clamp(v, 0, 100)}%`;
  }
  const v = o?.oee;
  $('#t-oee').dataset.state = v == null ? 'none' : v >= target ? 'ok' : v >= target - 15 ? 'warn' : 'bad';
  $('#target').textContent = `(meta ${fmt(target)}%)`;
  $('#oee-note').textContent = o ? '' : 'OEE indisponível: o snapshot do dashboard não traz OEE. Defina CONFIG.ENDPOINTS.oee quando o backend expuser esse dado.';
}

const stat = (label, v) => el('div', {}, el('dt', {}, label), el('dd', {}, v == null ? '—' : Math.round(v).toLocaleString('pt-BR')));

function renderOp(op) {
  const box = $('#op-body');
  if (!op) { box.replaceChildren(el('p', { class: 'empty' }, 'Nenhuma ordem de produção ativa.')); return; }
  const planned = num(op.quantity_planned) || 0, made = num(op.quantity_produced) || 0;
  const pct = clamp(num(op.progress_percentage) ?? (planned ? (made / planned) * 100 : 0), 0, 100);
  box.replaceChildren(
    el('div', { class: 'op-head' }, el('strong', {}, op.code || 'Sem código'), el('span', { class: 'muted' }, op.product_name || '')),
    el('div', { class: 'bar big', role: 'progressbar', 'aria-label': 'Progresso da ordem', 'aria-valuemin': 0, 'aria-valuemax': 100, 'aria-valuenow': Math.round(pct) },
      el('span', { style: { width: `${pct}%` } })),
    el('p', { class: 'muted' }, `${fmt(pct)}% de ${planned.toLocaleString('pt-BR')} peças planejadas`),
    el('dl', {}, stat('Produzidas', made), stat('Boas', num(op.quantity_good)), stat('Refugo', num(op.quantity_bad))),
  );
}

function renderDowntime(events) {
  const box = $('#downtime-list');
  if (events == null) { box.replaceChildren(el('p', { class: 'empty' }, 'Paradas indisponíveis: confira CONFIG.ENDPOINTS.downtime.')); return; }
  if (!events.length) { box.replaceChildren(el('p', { class: 'empty' }, 'Nenhuma parada registrada para esta linha.')); return; }
  const rows = events
    .map(e => ({ e, start: parseDate(e.start_time), end: parseDate(e.end_time), open: !e.end_time || String(e.status).toLowerCase() === 'open' }))
    .sort((a, b) => (b.open - a.open) || ((b.start?.getTime() || 0) - (a.start?.getTime() || 0)))
    .slice(0, 8);
  box.replaceChildren(el('ul', { class: 'events' }, rows.map(({ e, start, end, open }) => {
    const mins = open ? (start ? (Date.now() - start) / 60000 : null)
      : (num(e.duration_minutes) ?? (start && end ? (end - start) / 60000 : null));
    const sev = SEVERITY[String(e.severity).toLowerCase()];
    return el('li', {},
      el('div', { class: 'ev-top' },
        el('strong', {}, e.reason || typeLabel(e.type) || 'Parada'),
        open ? el('span', { class: 'badge is-fail' }, 'Em andamento') : null),
      el('div', { class: 'ev-sub' }, [typeLabel(e.type), sev && `severidade ${sev}`, start && `início ${fmtTime(e.start_time)}`, mins != null && `duração ${fmtDur(mins * 60)}`].filter(Boolean).join(', ')),
    );
  })));
}

function renderMachines(list) {
  const box = $('#machines-list');
  if (!list.length) { box.replaceChildren(el('p', { class: 'empty' }, 'Nenhuma máquina cadastrada nesta linha.')); return; }
  box.replaceChildren(...list.map(m => {
    const [cls, label] = statusOf(m.status);
    const wear = clamp(num(m.wear_level) ?? 0, 0, 100);
    const when = cls === 'maint' ? fmtTime(m.maintenance_end_at) && `Manutenção até ${fmtTime(m.maintenance_end_at)}`
      : cls === 'run' ? fmtTime(m.last_start_time) && `Ligada desde ${fmtTime(m.last_start_time)}`
      : fmtTime(m.last_stop_time) && `Parada desde ${fmtTime(m.last_stop_time)}`;
    return el('article', { class: `machine is-${cls}` },
      el('div', { class: 'm-head' }, el('h3', {}, m.name || `Máquina ${m.id}`), m.code ? el('span', {}, m.code) : null),
      el('p', { class: 'state' }, label),
      el('div', { class: 'wear-row' }, el('span', {}, 'Desgaste'), el('span', {}, `${fmt(wear)}%`)),
      el('div', { class: `meter ${wear >= 80 ? 'w-bad' : wear >= 50 ? 'w-warn' : 'w-ok'}`, role: 'meter', 'aria-label': 'Desgaste', 'aria-valuemin': 0, 'aria-valuemax': 100, 'aria-valuenow': Math.round(wear) },
        el('span', { style: { width: `${wear}%` } })),
      el('p', { class: 'm-note' }, [when, num(m.breakdown_count) != null ? `${m.breakdown_count} quebras` : null].filter(Boolean).join(', ')),
    );
  }));
}

function render(d) {
  renderLine(d.line);
  renderOee(d.oee, d.target);
  renderOp(d.op);
  renderDowntime(d.downtime);
  renderMachines(d.machines);
  state.hasData = true;
}

function setConn(kind, detail = '') {
  const c = $('#conn');
  c.className = 'conn';
  if (kind === 'ok') {
    c.textContent = `Atualizado às ${new Date().toLocaleTimeString('pt-BR')}`;
  } else if (kind === 'demo') {
    c.classList.add('is-demo');
    c.textContent = `Modo demonstração: dados simulados no navegador. Atualizado às ${new Date().toLocaleTimeString('pt-BR')}`;
  } else {
    c.classList.add('is-error');
    c.textContent = `Sem resposta de ${CONFIG.API_BASE || location.origin} (${detail}). ${state.hasData ? 'Mostrando os últimos dados recebidos. ' : ''}Nova tentativa em ${CONFIG.POLL_MS / 1000} s. Para ver o painel sem backend, use "Dados de demonstração".`;
  }
}

/* ---------- Dados de demonstração (mesmo formato da API real) ---------- */
const demo = { tick: 0, produced: 140 };
function mockSnapshot() {
  demo.tick++;
  const failing = demo.tick % 24 >= 18;
  demo.produced = (demo.produced + (failing ? 0 : Math.round(6 + Math.random() * 10))) % 1001;
  const j = (b, s) => clamp(b + (Math.random() - 0.5) * s, 0, 100);
  const a = failing ? j(60, 4) : j(93, 5), p = failing ? j(45, 6) : j(89, 7), q = j(97, 3);
  const now = Date.now(), ago = min => new Date(now - min * 60000).toISOString();
  const good = Math.round(demo.produced * 0.97);
  return {
    snapshot: {
      id: 1, name: 'Linha de envase 1', target_oee: 85, ideal_production_rate: 60,
      current_production_rate: failing ? 0 : j(52, 10), total_runtime_minutes: 95 + demo.tick,
      simulation_status: failing ? 'idle' : 'running',
      machines: [
        { id: 1, name: 'Enchedora', base_failure_rate: 3, wear_level: 34, status: 'production', last_start_time: ago(95) },
        { id: 2, name: 'Rotuladora', base_failure_rate: 3, wear_level: failing ? 88 : 71, status: failing ? 'maintenance' : 'production', last_start_time: ago(95), maintenance_end_at: new Date(now + 8 * 60000).toISOString() },
        { id: 3, name: 'Seladora', base_failure_rate: 3, wear_level: 52, status: 'production', last_start_time: ago(95) },
        { id: 4, name: 'Encaixotadora', base_failure_rate: 3, wear_level: 12, status: 'idle', last_stop_time: ago(140) },
      ],
      active_op: { id: 1, code: 'OP-2026-0142', product_name: 'Garrafa 500 ml', quantity_planned: 1000, quantity_produced: demo.produced, quantity_good: good, quantity_bad: demo.produced - good, status: 'production' },
    },
    oee: { availability: a, performance: p, quality: q, oee: (a * p * q) / 10000 },
    downtime: [
      { id: 1, production_line_id: 1, reason: 'Linha sem ordem de produção ativa', type: 'undefined_production', status: 'close', start_time: ago(180), end_time: ago(150), duration_minutes: 30 },
      ...(failing ? [{ id: 2, production_line_id: 1, reason: 'Falha crítica na rotuladora', type: 'failure', severity: 'high', status: 'open', start_time: ago(2), end_time: null }] : []),
    ],
  };
}

/* ---------- Busca e ciclo de atualização ---------- */
async function getJSON(path, signal) {
  const r = await fetch(CONFIG.API_BASE + path, { signal, headers: { Accept: 'application/json' } });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

async function refresh() {
  clearTimeout(state.timer);
  state.ctrl?.abort();                       // cancela a requisição anterior (troca de linha)
  state.ctrl = new AbortController();
  const gen = ++state.gen;
  try {
    let snap, dt, oeeRaw = null;
    if (state.demo) {
      ({ snapshot: snap, downtime: dt, oee: oeeRaw } = mockSnapshot());
    } else {
      const sig = AbortSignal.any([state.ctrl.signal, AbortSignal.timeout(CONFIG.TIMEOUT_MS)]);
      const E = CONFIG.ENDPOINTS;
      const optional = path => (path ? getJSON(path, sig).catch(() => null) : Promise.resolve(null));
      const [s, all, o] = await Promise.all([
        getJSON(E.dashboard(state.lineId), sig),
        optional(E.downtime),
        optional(E.oee && E.oee(state.lineId)),
      ]);
      snap = s;
      dt = Array.isArray(all) ? all.filter(e => String(e.production_line_id) === String(state.lineId)) : null;
      oeeRaw = Array.isArray(o) ? o[o.length - 1] : o;
    }
    if (gen !== state.gen) return;
    render(normalize(snap, dt, oeeRaw));
    setConn(state.demo ? 'demo' : 'ok');
  } catch (err) {
    if (gen !== state.gen) return;
    setConn('error', err.name === 'TimeoutError' ? 'tempo esgotado' : err.message);
  }
  // Só agenda a próxima rodada depois que esta terminou: sem requisições sobrepostas.
  if (gen === state.gen && !document.hidden) state.timer = setTimeout(refresh, CONFIG.POLL_MS);
}

async function loadLines() {
  const sel = $('#line-select');
  let lines = [];
  if (state.demo) lines = [{ id: 1, name: 'Linha de envase 1' }];
  else {
    try {
      const r = await getJSON(CONFIG.ENDPOINTS.lines, AbortSignal.timeout(CONFIG.TIMEOUT_MS));
      lines = Array.isArray(r) ? r : r.items || [];
    } catch { /* sem a lista, usa só a linha atual */ }
  }
  if (!lines.length) lines = [{ id: state.lineId }];
  sel.replaceChildren(...lines.map(l => el('option', { value: l.id, textContent: l.name || `Linha ${l.id}` })));
  state.lineId = lines.some(l => String(l.id) === String(state.lineId)) ? state.lineId : lines[0].id;
  sel.value = state.lineId;
}

/* ---------- Inicialização ---------- */
function setupTheme() {
  const btn = $('#theme-toggle');
  const label = () => { btn.textContent = document.documentElement.dataset.theme === 'dark' ? 'Tema claro' : 'Tema escuro'; };
  btn.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch { /* armazenamento indisponível */ }
    label();
  });
  label();
}

document.addEventListener('DOMContentLoaded', async () => {
  setupTheme();

  $('#line-select').addEventListener('change', e => {
    state.lineId = e.target.value;
    localStorage.setItem('line', state.lineId);
    state.hasData = false;
    refresh();
  });

  $('#demo-toggle').addEventListener('click', async e => {
    state.demo = !state.demo;
    e.currentTarget.setAttribute('aria-pressed', String(state.demo));
    state.hasData = false;
    await loadLines();
    refresh();
  });

  // Ao voltar para a aba, atualiza na hora (o ciclo fica parado enquanto a aba está escondida).
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });

  await loadLines();
  refresh();
});
