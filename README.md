# Smart Task Analyzer  
### AI-Inspired Task Prioritization System using **Django REST Framework + HTML/JS Frontend**

This project analyzes tasks based on **urgency, importance, effort, and dependencies** and produces a **priority ranking** along with **Top-3 task suggestions**.  
It includes:

- Django backend with advanced scoring algorithm  
- Circular dependency detection  
- REST APIs for analysis & suggestions  
- Frontend with graph visualization  
- Bulk JSON loading  
- Strategy-based prioritization  

---

# 1. Project Overview

Managing multiple tasks manually becomes difficult when:

- Deadlines overlap  
- Some tasks depend on others  
- Importance levels vary  
- Workload is unpredictable  

This system provides **data-driven task prioritization**.

### Features
- Add tasks manually  
- Load tasks via JSON  
- Auto-detect circular dependencies  
- Visual dependency graph  
- Customizable strategies  
- Top 3 prioritized task suggestions  
- Priority badges (High/Medium/Low)  
- Tooltip breakdowns explaining score  

---

# 2. System Architecture

### **Backend – Django REST Framework**
- Validates tasks  
- Computes priority score  
- Detects circular dependencies  
- Implements strategies  
- Generates detailed explanations  
- Exposes two endpoints:

```
POST /api/tasks/analyze/
POST /api/tasks/suggest/
```

---

### Frontend – HTML + JS
- Interactive task form  
- JSON bulk input  
- Displays analyzed tasks  
- Renders dependency graph  
- Shows suggestions  
- Calls Django APIs  
- Uses **vis-network.js** for graph visualization  

---

# 3. Design Decisions (Documentation Required)

This explains *why* each component was built the way it is.

## **3.1 Why Django REST Framework?**
- Clean JSON APIs  
- Built-in validation  
- Easy error handling  
- Perfect for quick backend development  
- Works seamlessly with frontend JS  

DRF provides speed + reliability for this assignment.

---

## **3.2 Why Use a Custom Algorithm Instead of ML?**
- Fully explainable  
- Deterministic  
- Works offline  
- Fast for small datasets  
- Transparent scoring breakdown  

This is ideal for priority decisions where logic must be clear.

---

## **3.3 Why SQLite?**
- Zero setup  
- Fast performance  
- Ideal for a local project  
- Django's default ORM works instantly  

---

## **3.4 Why No Database Storage for Tasks?**
Tasks are analyzed in real-time.  
Saving them was not part of assignment requirements.

The frontend manages tasks in a JS array.

---

## **3.5 Why Use vis-network.js for Dependency Graphs?**
- Simple  
- Lightweight  
- Supports directed edges  
- Great for representing task dependencies visually  

---

## **3.6 Why Circular Dependency Detection?**
To catch invalid scenarios like:

```
A → depends on B  
B → depends on A
```

Circular loops break prioritization.  
We implemented **Kahn’s Algorithm** to detect cycles safely.

---

## **3.7 Why Strategies?**
Different users have different workflows:

| Strategy | Meaning |
|----------|---------|
| smart | balanced for real life |
| fast | quick wins first |
| impact | high-importance first |
| deadline | time-sensitive |

---

# 4. Scoring Algorithm

Each task gets a score between **0.00 – 1.00** based on:

###  Urgency  
```
Overdue → highest urgency  
Due soon  → medium  
No due date → low urgency  
```

### Importance  
Normalized:
```
(importance - 1) / 9
```

### Effort  
Favors smaller tasks:
```
1 - (hours / max_hours)
```

###  Dependency Weight  
```
dependents / total_tasks
```

### Final Score = Weighted Sum
```
score = (urgency*w1 + importance*w2 + effort*w3 + dependency*w4)
```

Weights are customizable.

---

# 5. Circular Dependency Detection

Uses **Topological Sorting (Kahn’s Algorithm)**:

- Build directed graph  
- Compute indegree  
- Remove nodes with zero indegree  
- If unprocessed nodes remain → CYCLE  

If cycle found:
```
"Circular dependency detected"
```

---

# 6. API Endpoints

## **POST /api/tasks/analyze/**
### Request:
```json
{
  "tasks": [
    {
      "title": "Submit Report",
      "due_date": "2025-05-20",
      "estimated_hours": 4,
      "importance": 8,
      "dependencies": [1]
    }
  ],
  "strategy": "smart",
  "weights": { "urgency": 0.4 }
}
```

### Response:
- Sorted tasks  
- Score breakdown  
- Explanation  

---

## **POST /api/tasks/suggest/**
Returns **Top 3 tasks to do next**.

---

# 7. Frontend Features

✔ Add task manually  
✔ Remove tasks  
✔ Paste JSON and load/append  
✔ Switch strategies  
✔ Display priority badges:

- **High** – red  
- **Medium** – yellow  
- **Low** – green  

✔ Tooltips show breakdown  
✔ Graph visualization with arrows  
✔ API integration  

---

# 8. How to Run the Project

### Backend:
```
cd backend
python manage.py migrate
python manage.py runserver
```
Runs at:
```
http://localhost:8000
```

### Frontend:
Just open:
```
frontend/index.html
```


