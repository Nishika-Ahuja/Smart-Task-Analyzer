// frontend/script.js
const API_BASE = '/api/tasks'; // adjust if backend hosted elsewhere

const tasks = []; // in-memory list

function el(id){ return document.getElementById(id); }

document.getElementById('task-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const title = el('title').value.trim();
  if(!title) return alert('Title required');
  const id = Date.now().toString(36);
  const due_date = el('due_date').value || null;
  const estimated_hours = parseFloat(el('estimated_hours').value) || 1;
  const importance = parseInt(el('importance').value) || 5;
  const deps = el('dependencies').value.split(',').map(s=>s.trim()).filter(Boolean);
  tasks.push({ id, title, due_date, estimated_hours, importance, dependencies: deps });
  el('title').value=''; el('due_date').value=''; el('dependencies').value='';
  renderLocalTasks();
});

function renderLocalTasks(){
  const r = el('results');
  r.innerHTML = '<h3>Local tasks (not yet analyzed)</h3>';
  tasks.forEach(t=>{
    const div = document.createElement('div'); div.className='task-item';
    div.innerHTML = `<div>
      <strong>${t.title}</strong><div class="explanation">${t.due_date || 'No due date'} • ${t.estimated_hours}h • importance ${t.importance}</div>
    </div><div>${t.id}</div>`;
    r.appendChild(div);
  });
}

el('analyze-btn').addEventListener('click', async () => {
  const bulk = el('bulk-json').value.trim();
  let payloadTasks = tasks.slice();
  if(bulk) {
    try {
      const parsed = JSON.parse(bulk);
      if(Array.isArray(parsed)) payloadTasks = parsed;
      else return alert('Bulk JSON must be array of tasks');
    } catch (err) { return alert('Invalid JSON'); }
  }
  if(payloadTasks.length === 0) return alert('No tasks provided');
  const strategy = el('strategy').value;
  try {
    showLoading();
    const res = await fetch(`${API_BASE}/analyze/`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ tasks: payloadTasks, strategy })
    });
    hideLoading();
    if(!res.ok){
      const err = await res.json();
      return alert('Error: ' + JSON.stringify(err));
    }
    const data = await res.json();
    renderAnalyzed(data.tasks);
  } catch (err){
    hideLoading();
    alert('Network error: ' + err.message);
  }
});

el('suggest-btn').addEventListener('click', async () => {
  const bulk = el('bulk-json').value.trim();
  let payloadTasks = tasks.slice();
  if(bulk) {
    try {
      const parsed = JSON.parse(bulk);
      if(Array.isArray(parsed)) payloadTasks = parsed;
      else return alert('Bulk JSON must be array of tasks');
    } catch (err) { return alert('Invalid JSON'); }
  }
  if(payloadTasks.length === 0) return alert('No tasks provided');
  const strategy = el('strategy').value;
  try {
    showLoading();
    // Because some servers disallow a body on GET, we'll call POST-like analyze endpoint and pick top3 client side
    const res = await fetch(`${API_BASE}/analyze/`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ tasks: payloadTasks, strategy })
    });
    hideLoading();
    if(!res.ok){
      const err = await res.json();
      return alert('Error: ' + JSON.stringify(err));
    }
    const data = await res.json();
    const top3 = data.tasks.slice(0,3);
    renderSuggestions(top3);
  } catch (err){
    hideLoading();
    alert('Network error: ' + err.message);
  }
});

function renderAnalyzed(list){
  const r = el('results'); r.innerHTML = '<h3>Analyzed & Sorted Tasks</h3>';
  list.forEach(t=>{
    const div = document.createElement('div');
    const cls = t.score >= 0.6 ? 'priority-high' : t.score >= 0.35 ? 'priority-medium' : 'priority-low';
    div.className = 'task-item ' + cls;
    div.innerHTML = `<div>
      <strong>${t.title}</strong>
      <div class="explanation">${t.explanation}</div>
      <small>Due: ${t.due_date || '—'} • Effort: ${t.estimated_hours}h • Importance: ${t.importance}</small>
    </div>
    <div>
      <div><strong>${t.score}</strong></div>
      <div style="font-size:0.8rem;color:#6b7280">${t.id}</div>
    </div>`;
    r.appendChild(div);
  });
}

function renderSuggestions(list){
  const r = el('results'); r.innerHTML = '<h3>Top Suggestions</h3>';
  list.forEach(t=>{
    const div = document.createElement('div'); div.className='task-item priority-high';
    div.innerHTML = `<div><strong>${t.title}</strong><div class="explanation">${t.explanation || t.explain}</div><small>Score: ${t.score}</small></div><div>${t.id}</div>`;
    r.appendChild(div);
  });
}

function showLoading(){ /* simple indicator */ document.body.style.cursor='wait'; }
function hideLoading(){ document.body.style.cursor='default'; }
