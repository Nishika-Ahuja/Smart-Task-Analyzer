from datetime import date
from collections import defaultdict, deque

class CircularDependencyError(Exception):
    pass

def detect_cycle(tasks_by_id):

    indeg = {}
    graph = defaultdict(list)
    for tid, t in tasks_by_id.items():
        indeg[tid] = indeg.get(tid, 0)
    for tid, t in tasks_by_id.items():
        for dep in t.get("dependencies", []):
            graph[dep].append(tid)
            indeg[tid] = indeg.get(tid, 0) + 1

    q = deque([n for n, d in indeg.items() if d == 0])
    visited = 0
    while q:
        u = q.popleft()
        visited += 1
        for v in graph.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return visited != len(indeg)

def compute_scores(task_list, strategy="smart", weights=None):


    default_weights = {
        "urgency": 0.35,
        "importance": 0.30,
        "effort": 0.15,
        "dependency": 0.20,
    }
    if weights:
        w = default_weights.copy()
        w.update(weights)
    else:
        w = default_weights

    if strategy == "fast":
        w = {"urgency": 0.1, "importance": 0.1, "effort": 0.7, "dependency": 0.1}
    elif strategy == "impact":
        w = {"urgency": 0.1, "importance": 0.7, "effort": 0.05, "dependency": 0.15}
    elif strategy == "deadline":
        w = {"urgency": 0.7, "importance": 0.15, "effort": 0.1, "dependency": 0.05}

    hours = [max(0.01, (t.get("estimated_hours") or 1.0)) for t in task_list]
    max_hours = max(hours) if hours else 1.0

    tasks_by_id = {}
    for idx, t in enumerate(task_list):
        tid = t.get("id", idx + 1)
        tasks_by_id[tid] = {
            "raw": t,
            "dependencies": t.get("dependencies", []) or []
        }

    if detect_cycle(tasks_by_id):
        raise CircularDependencyError("Circular dependency detected in tasks input.")

    dependents_count = defaultdict(int)
    for tid, v in tasks_by_id.items():
        for dep in v["dependencies"]:
            dependents_count[dep] += 1

    results = []
    today = date.today()
    for tid, v in tasks_by_id.items():
        t = v["raw"]
        title = t.get("title", "Untitled")
        due = t.get("due_date")
        if isinstance(due, str):
            try:
                y, m, d = map(int, due.split("-"))
                due = date(y, m, d)
            except Exception:
                due = None

        days_to_due = (due - today).days if due else None

        # URGENCY SCORE 
        if strategy == "deadline":
            if due:
                # overdue tasks highest priority
                if days_to_due < 0:
                    urgency_score = 1.0
                else:
                    urgency_score = max(0.0, 1.0 - (days_to_due / 365.0))
            else:
                urgency_score = 0.0
        else:
            if days_to_due is None:
                urgency_score = 0.2
            else:
                if days_to_due < 0:
                    urgency_score = min(1.0, 0.9 + (abs(days_to_due)/30.0))
                else:
                    urgency_score = max(0.0, (30 - min(days_to_due,30))/30.0)

        importance_raw = float(t.get("importance") or 5.0)
        importance_score = max(0.0, min(1.0, (importance_raw - 1)/9.0))

        est = float(t.get("estimated_hours") or 1.0)
        effort_score = 1.0 - min(1.0, est / (max_hours or 1.0))

        dep_score = min(1.0, dependents_count.get(tid,0)/max(1,len(task_list)))

        score = (
            w.get("urgency",0)*urgency_score +
            w.get("importance",0)*importance_score +
            w.get("effort",0)*effort_score +
            w.get("dependency",0)*dep_score
        )
        score = max(0.0, min(1.0, score))

        explanation = (
            f"urgency: {urgency_score:.2f}, importance: {importance_score:.2f}, "
            f"effort: {effort_score:.2f}, dependency: {dep_score:.2f} => score {score:.2f}"
        )

        
        results.append({
            "id": tid,
            "title": title,
            "due_date": due.isoformat() if due else None,
            "estimated_hours": est,
            "importance": int(importance_raw),
            "dependencies": v["dependencies"],
            "score": round(score,4),
            "explanation": explanation,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results



