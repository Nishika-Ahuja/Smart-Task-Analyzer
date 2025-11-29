const taskForm = document.getElementById("taskForm");
const taskListEl = document.getElementById("taskList");
const analyzeBtn = document.getElementById("analyzeBtn");
const suggestBtn = document.getElementById("suggestBtn");
const strategySelect = document.getElementById("strategySelect");
const resultList = document.getElementById("resultList");
const suggestionList = document.getElementById("suggestList");
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const clearListBtn = document.getElementById("clearList");
const graphOutput = document.getElementById("graphOutput");

const bulkInput = document.getElementById("bulkInput");
const loadBulk = document.getElementById("loadBulk");
const appendBulk = document.getElementById("appendBulk");
const bulkError = document.getElementById("bulkError");

const weightInputs = {
  urgency: document.getElementById("weightUrgency"),
  importance: document.getElementById("weightImportance"),
  effort: document.getElementById("weightEffort"),
  dependency: document.getElementById("weightDependency"),
};

let tasks = [];
let nextId = 1;


function renderTasks() {
  taskListEl.innerHTML = "";
  if (!tasks.length) {
    taskListEl.innerHTML = "<div class='muted-small'>No tasks yet. Add one or paste a JSON array.</div>";
    updateGraph();
    return;
  }

  tasks.forEach(t => {
    const div = document.createElement("div");
    div.className = "task-item";
    div.innerHTML = `
      <div class="meta">
        <div class="title-row"><strong>${escapeHtml(t.title)}</strong><div class="meta-small">ID: ${t.id}</div></div>
        <div class="meta-small">${t.due_date ? 'Due: '+t.due_date : 'No due date'} · ${t.estimated_hours}h · Importance ${t.importance}</div>
      </div>
      <div style="display:flex;gap:0.6rem;align-items:center">
        <button class="small-remove" data-id="${t.id}" title="Remove">✕</button>
      </div>
    `;
    taskListEl.appendChild(div);
  });

  document.querySelectorAll(".small-remove").forEach(btn => btn.addEventListener("click", (e) => {
    const id = +e.target.dataset.id;
    tasks = tasks.filter(t => t.id !== id);
    tasks.forEach(t => {
      if (t.dependencies) t.dependencies = t.dependencies.filter(d => d !== id);
    });
    renderTasks();
  }));

  updateGraph();
}

function updateGraph() {
  let text = "";
  tasks.forEach(t => {
    text += `${t.id}: ${t.title}\n`;
    text += `   Depends on → [${(t.dependencies || []).join(", ")}]\n\n`;
  });
  graphOutput.textContent = text || "No tasks.";

  const nodes = tasks.map(t => ({ id: t.id, label: `${t.id}: ${t.title}`, color: '#89CFF0' }));
  const edges = [];
  tasks.forEach(t => {
    if(t.dependencies && t.dependencies.length) {
      t.dependencies.forEach(dep => {
        if(tasks.find(x => x.id === dep)) edges.push({ from: dep, to: t.id, arrows: 'to', color: '#555' });
      });
    }
  });

  const container = document.getElementById('graphVis');
  const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
  const options = {
    layout: { hierarchical: { enabled: true, direction: 'UD', sortMethod: 'directed' } },
    nodes: { shape: 'box', font: { size: 14 }, margin: 10 },
    edges: { smooth: { type: 'cubicBezier', forceDirection: 'vertical' } },
    physics: { enabled: false }
  };
  new vis.Network(container, data, options);
}


taskForm.addEventListener("submit", e => {
  e.preventDefault();
  const data = new FormData(taskForm);
  const title = (data.get("title") || "").trim();
  if (!title) return alert("Title is required.");

  const estRaw = data.get("estimated_hours");
  const est = Number.isFinite(Number(estRaw)) ? parseInt(estRaw, 10) : 1;
  const importance = Number.isFinite(Number(data.get("importance"))) ? parseInt(data.get("importance"), 10) : 5;
  const depsStr = data.get("dependencies") || "";
  const deps = depsStr.split(",").map(s => parseInt(s.trim())).filter(Boolean);

  tasks.push({
    id: nextId++,
    title,
    due_date: data.get("due_date") || null,
    estimated_hours: est,
    importance,
    dependencies: deps
  });

  taskForm.reset();
  renderTasks();
});


function showBulkError(msg) {
  bulkError.textContent = msg;
  bulkError.classList.remove("hidden");
  setTimeout(()=>bulkError.classList.add("hidden"), 5000);
}

loadBulk.addEventListener("click", () => {
  const txt = bulkInput.value.trim();
  if (!txt) return showBulkError("Paste JSON array first");
  try {
    const arr = JSON.parse(txt);
    if (!Array.isArray(arr)) return showBulkError("JSON must be an array of tasks");
    tasks = []; nextId = 1;
    arr.forEach(t => {
      if (!t.title) return showBulkError("Each task needs a title");
      const est = Number.isFinite(Number(t.estimated_hours)) ? parseInt(t.estimated_hours, 10) : 1;
      const importance = Number.isFinite(Number(t.importance)) ? parseInt(t.importance, 10) : 5;
      const deps = Array.isArray(t.dependencies) ? t.dependencies.map(n => parseInt(n,10)).filter(Boolean) : [];
      tasks.push({ id: nextId++, title: t.title, due_date: t.due_date || null, estimated_hours: est, importance, dependencies: deps });
    });
    renderTasks();
  } catch (err) {
    showBulkError("Invalid JSON: " + err.message);
  }
});

appendBulk.addEventListener("click", () => {
  const txt = bulkInput.value.trim();
  if (!txt) return showBulkError("Paste JSON array first");
  try {
    const arr = JSON.parse(txt);
    if (!Array.isArray(arr)) return showBulkError("JSON must be an array of tasks");
    arr.forEach(t => {
      if (!t.title) return showBulkError("Each task needs a title");
      const est = Number.isFinite(Number(t.estimated_hours)) ? parseInt(t.estimated_hours, 10) : 1;
      const importance = Number.isFinite(Number(t.importance)) ? parseInt(t.importance, 10) : 5;
      const deps = Array.isArray(t.dependencies) ? t.dependencies.map(n => parseInt(n,10)).filter(Boolean) : [];
      tasks.push({ id: nextId++, title: t.title, due_date: t.due_date || null, estimated_hours: est, importance, dependencies: deps });
    });
    renderTasks();
  } catch (err) {
    showBulkError("Invalid JSON: " + err.message);
  }
});


function getWeights() {
  const w = {};
  for (const key in weightInputs) {
    const val = parseFloat(weightInputs[key]?.value);
    if (!isNaN(val)) w[key] = val;
  }
  return Object.keys(w).length ? w : null;
}

analyzeBtn.addEventListener("click", async () => {
  if (!tasks.length) return alert("Add tasks first!");
  loadingEl.classList.remove("hidden");
  resultList.innerHTML = "";
  errorEl.classList.add("hidden");
  try {
    const res = await fetch("http://localhost:8000/api/tasks/analyze/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tasks, strategy: strategySelect.value, weights: getWeights() })
    });
    const data = await res.json();
    loadingEl.classList.add("hidden");
    if (!res.ok) {
      alert("Error: " + (data.detail || "Server error. Check for circular dependencies or invalid data."));
      return;
    }
    displayResults(data.tasks);
  } catch (err) {
    loadingEl.classList.add("hidden");
    alert("Network error: " + err.message);
  }
});

function formatExplanation(expStr) {
  if(!expStr) return "";
  const parts = expStr.split(",");
  const breakdownArr = [];
  parts.forEach(p => {
    const [k,v] = p.split(":");
    if(!k || !v) return;
    breakdownArr.push({ key: k.trim(), value: parseFloat(v) });
  });
  return breakdownArr;
}

function displayResults(list) {
  resultList.innerHTML = "";
  list.forEach(t => {
    const badge = getBadgeForScore(t.score);
    const breakdown = formatExplanation(t.explanation); 

    const breakdownStr = breakdown.map(b => `${b.key.charAt(0).toUpperCase() + b.key.slice(1)}: ${(b.value*100).toFixed(0)}%`).join(" · ");
    
    const reasonText = t.reason || "Based on task's urgency, importance, effort, and dependencies.";

    const explanationText = `
      Absolute Score Breakdown: ${breakdownStr}.<br>
      Reason: ${reasonText}<br>
      Note: Analysis is task-by-task. Top Suggestions may rank tasks differently based on relative priority.
    `;

    const item = document.createElement("div");
    item.className = "task-item";
    item.innerHTML = `
      <div class="meta">
        <div class="title-row">
          <strong>${escapeHtml(t.title)}</strong>
          <span class="badge ${badge.class} tooltip" style="margin-left:10px">
            ${badge.label}
            <span class="tooltiptext">${explanationText}</span>
          </span>
        </div>
        <div class="meta-small">${t.due_date ? 'Due: '+t.due_date : 'No due date'} · ${t.estimated_hours}h · Importance ${t.importance}</div>
        <div class="explanation"><strong>Score Breakdown:</strong> ${breakdownStr}</div>
        <div class="explanation"><strong>Reason:</strong> ${reasonText}</div>
      </div>
      <div style="text-align:right">
        <div class="meta-small">Overall Score: ${(t.score*100).toFixed(0)}%</div>
        <div style="margin-top:6px" class="meta-small">${t.dependencies && t.dependencies.length ? 'Depends on: '+t.dependencies.join(', ') : ''}</div>
      </div>
    `;
    resultList.appendChild(item);
  });
}


suggestBtn.addEventListener("click", async () => {
  if (!tasks.length) return alert("Add tasks first!");
  suggestionList.innerHTML = "";
  try {
    const res = await fetch("http://localhost:8000/api/tasks/suggest/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tasks, strategy: strategySelect.value, weights: getWeights() })
    });
    const data = await res.json();
    console.log("Received from backend:", data);
    if (!res.ok) return alert("Error fetching suggestions: " + (data.detail || "Check tasks or circular dependencies"));
    
    data.suggestions.forEach(s => {
      const badge = getBadgeForScore(s.score);
      const breakdown = formatExplanation(s.reason);
      const breakdownStr = breakdown.map(b => `${b.key.charAt(0).toUpperCase() + b.key.slice(1)}: ${(b.value*100).toFixed(0)}%`).join(" · ");
      const reasonText = s.reason || "Ranked relative to other tasks based on priority";

      const explanationText = `
        Score Breakdown: ${breakdownStr}.<br>
        Reason: ${reasonText}<br>
        Note: Suggestions are ranked relative to other tasks. 
        Even if a task is Low in Analysis, it can appear Medium/High here due to higher relative priority.
      `;
      
      suggestionList.innerHTML += `
        <div class="task-item">
          <div class="meta">
            <div class="title-row">
              <strong>${escapeHtml(s.title)}</strong>
              <span class="badge ${badge.class} tooltip" style="margin-left:10px">
                ${badge.label}
                <span class="tooltiptext">${explanationText}</span>
              </span>
            </div>
            <div class="meta-small">Overall Priority: ${(s.score*100).toFixed(0)}%</div>
            <div class="explanation"><strong>Reason:</strong> ${reasonText}</div>
          </div>
        </div>
      `;
    });
  } catch (err) {
    alert("Error fetching suggestions: " + err.message);
  }
});


clearListBtn.addEventListener("click", () => {
  if (!confirm("Clear all tasks?")) return;
  tasks = []; nextId = 1; renderTasks();
});

renderTasks();

function getBadgeForScore(score) {
  if (score >= 0.75) return { label: "High", class: "high" };
  if (score >= 0.40) return { label: "Medium", class: "med" };
  return { label: "Low", class: "low" };
}

function escapeHtml(unsafe) {
  return (unsafe || "").toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}



