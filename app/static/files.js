const state = {
  page: 1,
  pageSize: 20,
  total: 0,
  items: [],
  selectAllMode: false,
};

function $(id) {
  return document.getElementById(id);
}

function updateHint() {
  const hint = $("sel-hint");
  if (state.selectAllMode) {
    hint.textContent = `Выбраны все файлы (${state.total})`;
    return;
  }
  const n = document.querySelectorAll(".file-cb:checked").length;
  hint.textContent = n ? `Выбрано на странице: ${n}` : "";
}

function renderRows() {
  const tbody = $("files-table").querySelector("tbody");
  tbody.innerHTML = "";

  for (const item of state.items) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input type="checkbox" class="file-cb" value="${item.id}"></td>
      <td>${item.name}</td>
      <td>${item.downloaded_at_nsk}</td>
    `;
    tbody.appendChild(tr);
  }

  if (state.selectAllMode) {
    tbody.querySelectorAll(".file-cb").forEach((cb) => {
      cb.checked = true;
      cb.disabled = true;
    });
    $("sel-page").checked = true;
    $("sel-page").disabled = true;
  } else {
    $("sel-page").disabled = false;
    $("sel-page").checked = false;
  }

  tbody.querySelectorAll(".file-cb").forEach((cb) => {
    cb.addEventListener("change", updateHint);
  });
  updateHint();
}

function renderPager() {
  const pages = Math.max(1, Math.ceil(state.total / state.pageSize));
  const pager = $("pager");
  pager.innerHTML = "";

  const prev = document.createElement("button");
  prev.className = "btn";
  prev.textContent = "←";
  prev.disabled = state.page <= 1;
  prev.onclick = () => loadPage(state.page - 1);

  const info = document.createElement("span");
  info.className = "muted";
  info.textContent = `Стр. ${state.page} из ${pages} · всего ${state.total}`;

  const next = document.createElement("button");
  next.className = "btn";
  next.textContent = "→";
  next.disabled = state.page >= pages;
  next.onclick = () => loadPage(state.page + 1);

  pager.append(prev, info, next);
}

async function loadPage(page) {
  state.page = page;
  const res = await fetch(
    `/api/files?page=${state.page}&page_size=${state.pageSize}`
  );
  if (!res.ok) throw new Error("list " + res.status);
  const data = await res.json();
  state.items = data.items;
  state.total = data.total;
  renderRows();
  renderPager();
}

function renderDigitRow(counts) {
  const wrap = document.createElement("div");
  wrap.className = "digit-row";
  for (let d = 0; d <= 9; d++) {
    const key = String(d);
    const cell = document.createElement("div");
    cell.className = "digit-cell";
    cell.innerHTML = `<span class="digit">${key}</span><span class="count">${counts[key] ?? 0}</span>`;
    wrap.appendChild(cell);
  }
  return wrap;
}

function renderStats(data) {
  const panel = $("stats-panel");
  panel.hidden = false;
  
  const totalBox = $("stats-total"); 
  totalBox.replaceChildren(renderDigitRow(data.total));

  const filesBox = $("stats-files");
  filesBox.innerHTML = "";

  for (const f of data.files) {
    const block = document.createElement("div");
    block.className = "file-stats";
    const title = document.createElement("h4");
    title.textContent = f.name;
    block.appendChild(title);
    block.appendChild(renderDigitRow(f.counts));
    filesBox.appendChild(block);
  }
}

async function calculate() {
  let body;
  if (state.selectAllMode) {
    body = { mode: "all", ids: [] };
  } else {
    const ids = [...document.querySelectorAll(".file-cb:checked")].map((cb) =>
      Number(cb.value)
    );
    if (!ids.length) {
      alert("Выберите хотя бы один файл");
      return;
    }
    body = { mode: "ids", ids };
  }

  const btn = $("btn-calc");
  btn.disabled = true;
  btn.textContent = "Считаю…";
  try {
    const res = await fetch("/api/files/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || res.status);
    }
    const data = await res.json();
    renderStats(data);
  } catch (e) {
    alert("Ошибка расчёта: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Произвести расчёты";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("sel-page").addEventListener("change", (e) => {
    if (state.selectAllMode) return;
    document.querySelectorAll(".file-cb").forEach((cb) => {
      cb.checked = e.target.checked;
    });
    updateHint();
  });

  $("sel-all").addEventListener("change", (e) => {
    state.selectAllMode = e.target.checked;
    renderRows();
  });

  $("btn-calc").addEventListener("click", calculate);

  loadPage(1).catch((e) => alert("Не удалось загрузить список: " + e.message));
});


