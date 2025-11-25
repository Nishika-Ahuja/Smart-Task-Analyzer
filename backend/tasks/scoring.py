# backend/tasks/scoring.py
from datetime import date
from collections import defaultdict, deque

DEFAULT_WEIGHTS = {
    'urgency': 0.4,
    'importance': 0.3,
    'effort': 0.15,
    'dependencies': 0.15
}

STRATEGIES = {
    'fastest_wins': {'urgency': 0.2, 'importance': 0.2, 'effort': 0.5, 'dependencies': 0.1},
    'high_impact': {'urgency': 0.2, 'importance': 0.6, 'effort': 0.1, 'dependencies': 0.1},
    'deadline_driven': {'urgency': 0.6, 'importance': 0.2, 'effort': 0.1, 'dependencies': 0.1},
    'smart_balance': DEFAULT_WEIGHTS,
}

def _safe_days_until_due(due_date):
    if due_date is None:
        return None
    today = date.today()
    return (due_date - today).days

def normalize(value, minv, maxv):
    if maxv == minv:
        return 0.0
    return (value - minv) / (maxv - minv)

def detect_cycles(tasks):
    # tasks: list of dicts with 'id' and 'dependencies' (list of ids)
    graph = defaultdict(list)
    ids = set()
    for t in tasks:
        tid = str(t.get('id', t.get('title')))
        ids.add(tid)
    for t in tasks:
        tid = str(t.get('id', t.get('title')))
        for dep in t.get('dependencies', []):
            graph[tid].append(str(dep))
    visited = {}
    stack = set()
    cycles = set()

    def dfs(node):
        if node in visited:
            return visited[node]
        visited[node] = False
        stack.add(node)
        for nei in graph.get(node, []):
            if nei not in visited:
                if dfs(nei):
                    cycles.add(node)
            elif nei in stack:
                cycles.add(node)
                cycles.add(nei)
        stack.remove(node)
        visited[node] = True
        return visited[node]

    for n in list(ids):
        if n not in visited:
            dfs(n)
    # Return set of node ids that are part of cycles
    return cycles

def compute_scores(tasks, strategy='smart_balance', custom_weights=None):
    """
    tasks: list of dicts with fields:
      id (optional), title, due_date (date or None), estimated_hours (float), importance (1-10), dependencies (list of ids)
    returns list of tasks with extra keys: score (float), explanation (str), meta flags
    """
    if custom_weights:
        weights = custom_weights
    else:
        weights = STRATEGIES.get(strategy, DEFAULT_WEIGHTS)

    # Defensive copy & normalize fields
    processed = []
    for t in tasks:
        pt = {}
        pt['raw'] = t
        pt['id'] = str(t.get('id', t.get('title')))
        pt['title'] = t.get('title', '')
        # due_date may already be date object or None
        pt['due_date'] = t.get('due_date', None)
        pt['estimated_hours'] = float(t.get('estimated_hours', 1.0) or 1.0)
        pt['importance'] = int(t.get('importance', 5) or 5)
        pt['dependencies'] = [str(x) for x in (t.get('dependencies') or [])]
        processed.append(pt)

    # Build lookup to count how many depend on each task (i.e., blockers)
    dependents_count = defaultdict(int)
    for t in processed:
        for dep in t['dependencies']:
            dependents_count[dep] += 1

    # detect cycles
    cycles = detect_cycles(processed)

    # For urgency normalization, compute days_until_due for tasks with date
    days_list = []
    for t in processed:
        d = _safe_days_until_due(t['due_date'])
        t['days_until_due'] = d
        if d is not None:
            days_list.append(d)
    # For normalization, we want urgency high when days small or past-due
    # Transform into "urgency raw" where larger -> more urgent:
    # If past due (days < 0) make it large positive urgency by adding a large constant
    urgency_raw = []
    for t in processed:
        d = t['days_until_due']
        if d is None:
            # treat as low urgency but not zero
            u = 0.0
        else:
            if d < 0:
                # past due: urgency = large value scaled by how overdue
                u = 1000.0 + abs(d)  # ensures past-due outranks upcoming
            else:
                # nearer due => higher urgency. Use inverse days (bounded).
                # Cap at 365 days to avoid tiny numbers
                capped = min(d, 365)
                u = (365 - capped)  # bigger means more urgent
        urgency_raw.append(u)
        t['urgency_raw'] = u

    # Normalize urgency_raw to 0..1
    if urgency_raw:
        minu = min(urgency_raw)
        maxu = max(urgency_raw)
    else:
        minu = 0
        maxu = 1
    for t in processed:
        t['urgency_score'] = normalize(t['urgency_raw'], minu, maxu)

    # Importance normalized 1..10 -> 0..1
    for t in processed:
        t['importance_score'] = (t['importance'] - 1) / 9.0 if t['importance'] is not None else 0.5

    # Effort: lower estimated_hours => higher score. Use 1/(1+h) then normalize
    effort_raw = []
    for t in processed:
        h = max(0.0, t['estimated_hours'])
        t['effort_raw'] = 1.0 / (1.0 + h)  # when h=0 => 1.0, as h grows -> small
        effort_raw.append(t['effort_raw'])
    mine = min(effort_raw) if effort_raw else 0.0
    maxe = max(effort_raw) if effort_raw else 1.0
    for t in processed:
        t['effort_score'] = normalize(t['effort_raw'], mine, maxe)

    # Dependencies score: how many tasks depend on this task (blocker), normalize
    dep_counts = []
    for t in processed:
        c = dependents_count.get(t['id'], 0)
        t['dependents_count'] = c
        dep_counts.append(c)
    mind = min(dep_counts) if dep_counts else 0
    maxd = max(dep_counts) if dep_counts else 1
    for t in processed:
        t['dependency_score'] = normalize(t['dependents_count'], mind, maxd)

    # Compose final score using weights
    for t in processed:
        w = weights
        score = (
            w.get('urgency', 0) * t['urgency_score'] +
            w.get('importance', 0) * t['importance_score'] +
            w.get('effort', 0) * t['effort_score'] +
            w.get('dependencies', 0) * t['dependency_score']
        )
        # If task is in cycle, boost and flag explanation
        meta = {}
        explanation_parts = []
        if t['id'] in cycles:
            # Boost score to top; but keep it bounded by adding a strong boost
            score += 0.25  # add a chunk to push cycles up
            meta['circular_dependency'] = True
            explanation_parts.append('Part of a circular dependency (needs resolution).')
        else:
            meta['circular_dependency'] = False

        # If past-due add explicit note
        if t['days_until_due'] is not None and t['days_until_due'] < 0:
            explanation_parts.append(f"Past due by {abs(t['days_until_due'])} day(s).")

        # If no due date
        if t['days_until_due'] is None:
            explanation_parts.append("No due date specified (treated as lower urgency).")

        # Quick-win note
        if t['estimated_hours'] <= 1.0:
            explanation_parts.append("Quick win — low estimated effort.")

        # Important note
        if t['importance'] >= 8:
            explanation_parts.append("High importance.")

        # Dependency note if it blocks others
        if t['dependents_count'] > 0:
            explanation_parts.append(f"Blocks {t['dependents_count']} task(s).")

        t['score'] = round(score, 6)
        t['explanation'] = " | ".join(explanation_parts) if explanation_parts else "Balanced by scores."
        t['meta'] = meta

    # Sort descending by score and return
    processed_sorted = sorted(processed, key=lambda x: x['score'], reverse=True)
    return processed_sorted, list(cycles)
