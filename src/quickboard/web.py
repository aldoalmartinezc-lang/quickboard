from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def root() -> str:
    return """<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>QuickBoard</title>
  <style>
    :root { color-scheme: light; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #f8fafc; color: #0f172a; }
    main { max-width: 1100px; margin: 0 auto; display: grid; gap: 16px; }
    header { display: flex; justify-content: space-between; gap: 16px; align-items: baseline; flex-wrap: wrap; }
    section { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; box-shadow: 0 1px 2px rgba(15, 23, 42, .05); }
    .grid { display: grid; grid-template-columns: 320px 1fr; gap: 16px; }
    input, button { font: inherit; }
    input { padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 10px; width: 100%; box-sizing: border-box; }
    button { padding: 10px 14px; border: 0; border-radius: 10px; background: #0f172a; color: white; cursor: pointer; }
    button.secondary { background: #334155; }
    button.ghost { background: #e2e8f0; color: #0f172a; }
    .stack { display: grid; gap: 10px; }
    .board-item { display: flex; justify-content: space-between; gap: 8px; padding: 10px 12px; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 8px; cursor: pointer; }
    .board-item.active { border-color: #0f172a; background: #f1f5f9; }
    .list { border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; margin-bottom: 12px; }
    .card { border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; margin-top: 8px; background: #fff; }
    .muted { color: #64748b; font-size: 14px; }
    .row { display: grid; grid-template-columns: 1fr auto; gap: 8px; }
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>QuickBoard</h1>
      <p class=\"muted\">Tu kanban personal vía API REST. Sin cuentas, sin fricción.</p>
    </div>
    <div class=\"muted\" id=\"health\">Cargando health…</div>
  </header>

  <section class=\"grid\">
    <div class=\"stack\">
      <div class=\"stack\">
        <label>Nuevo board</label>
        <div class=\"row\"><input id=\"board-name\" placeholder=\"Inbox\" /><button onclick=\"createBoard()\">Crear</button></div>
      </div>
      <div>
        <h2>Boards</h2>
        <div id=\"boards\" class=\"stack\"></div>
      </div>
    </div>

    <div class=\"stack\">
      <div class=\"stack\">
        <label>Buscar cards</label>
        <div class=\"row\"><input id=\"search-q\" placeholder=\"texto\" /><button class=\"secondary\" onclick=\"searchCards()\">Buscar</button></div>
        <div id=\"search-results\" class=\"stack\"></div>
      </div>
      <div id=\"board-detail\" class=\"stack\"></div>
    </div>
  </section>
</main>
<script>
let activeBoardId = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  if (response.status === 204) return null;
  return response.json();
}

async function loadHealth() {
  const health = await api('/health');
  document.getElementById('health').textContent = `${health.status} · v${health.version}`;
}

async function loadBoards() {
  const boards = await api('/boards');
  const container = document.getElementById('boards');
  container.innerHTML = '';
  boards.forEach((board) => {
    const item = document.createElement('div');
    item.className = 'board-item' + (board.id === activeBoardId ? ' active' : '');
    item.innerHTML = `<strong>${board.name}</strong><span class='muted'>#${board.id}</span>`;
    item.onclick = () => openBoard(board.id);
    container.appendChild(item);
  });
  if (!activeBoardId && boards.length) {
    await openBoard(boards[0].id);
  }
}

async function openBoard(boardId) {
  activeBoardId = boardId;
  await loadBoards();
  const board = await api(`/boards/${boardId}`);
  const container = document.getElementById('board-detail');
  container.innerHTML = `
    <section>
      <div class='row'>
        <div>
          <h2>${board.name}</h2>
          <div class='muted'>Board #${board.id}</div>
        </div>
        <div class='stack' style='min-width: 260px;'>
          <input id='rename-board' placeholder='Renombrar board' />
          <button onclick='renameActiveBoard()'>Renombrar</button>
          <button class='ghost' onclick='deleteActiveBoard()'>Eliminar</button>
        </div>
      </div>
    </section>
    <section>
      <div class='row'>
        <input id='new-list-name' placeholder='Nueva list (Todo)' />
        <button onclick='createList()'>Agregar list</button>
      </div>
    </section>
    ${board.lists.map(renderList).join('') || '<p class="muted">Sin lists todavía.</p>'}
  `;
}

function renderList(list) {
  return `
    <div class='list'>
      <h3>${list.name}</h3>
      <div class='muted'>List #${list.id}</div>
      <div class='stack'>
        ${list.cards.map((card) => `<div class='card'><strong>${card.title}</strong><div class='muted'>${card.description || ''}</div><div class='muted'>Tags: ${(card.tags || []).join(', ') || '—'}</div></div>`).join('') || '<p class="muted">Sin cards.</p>'}
      </div>
      <div class='row' style='margin-top: 12px;'>
        <input id='card-title-${list.id}' placeholder='Nueva card' />
        <button onclick='createCard(${list.id})'>Agregar card</button>
      </div>
      <input id='card-desc-${list.id}' placeholder='Descripción opcional' style='margin-top: 8px;' />
      <input id='card-tags-${list.id}' placeholder='Tags separados por coma' style='margin-top: 8px;' />
    </div>
  `;
}

async function createBoard() {
  const input = document.getElementById('board-name');
  await api('/boards', { method: 'POST', body: JSON.stringify({ name: input.value }) });
  input.value = '';
  await loadBoards();
}

async function renameActiveBoard() {
  const name = document.getElementById('rename-board').value;
  await api(`/boards/${activeBoardId}`, { method: 'PATCH', body: JSON.stringify({ name }) });
  await loadBoards();
  await openBoard(activeBoardId);
}

async function deleteActiveBoard() {
  await api(`/boards/${activeBoardId}`, { method: 'DELETE' });
  activeBoardId = null;
  await loadBoards();
  document.getElementById('board-detail').innerHTML = '';
}

async function createList() {
  const name = document.getElementById('new-list-name').value;
  await api(`/boards/${activeBoardId}/lists`, { method: 'POST', body: JSON.stringify({ name }) });
  await openBoard(activeBoardId);
}

async function createCard(listId) {
  const title = document.getElementById(`card-title-${listId}`).value;
  const description = document.getElementById(`card-desc-${listId}`).value;
  const tags = document.getElementById(`card-tags-${listId}`).value.split(',').map((item) => item.trim()).filter(Boolean);
  await api(`/lists/${listId}/cards`, { method: 'POST', body: JSON.stringify({ title, description, tags }) });
  await openBoard(activeBoardId);
}

async function searchCards() {
  const q = document.getElementById('search-q').value;
  const results = await api(`/cards/search?q=${encodeURIComponent(q)}`);
  const container = document.getElementById('search-results');
  container.innerHTML = results.length
    ? results.map((card) => `<div class='card'><strong>${card.title}</strong><div class='muted'>${card.description || ''}</div><div class='muted'>List #${card.list_id} · Tags: ${(card.tags || []).join(', ') || '—'}</div></div>`).join('')
    : '<p class="muted">Sin resultados.</p>';
}

loadHealth();
loadBoards();
</script>
</body>
</html>"""
