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

The Smart Task Analyzer solves this problem by offering **data-driven task prioritization**.  
It uses a clear scoring algorithm, a dependency graph, and customizable strategies to help users decide what to do next.

### Features
- Add tasks manually  
- Load tasks via JSON  
- Auto-detect circular dependencies  
- Visual dependency graph  
- Customizable strategies (smart / fast / impact / deadline)  
- Top 3 prioritized task suggestions  
- Priority badges (High/Medium/Low)  
- Tooltip breakdowns explaining every score  

---

# 2. Setup Instructions

## Backend Setup (Django)
```
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API runs at:
```
http://localhost:8000
```

##  Frontend Setup
No installation needed.

Simply open:
```
frontend/index.html
```

Your browser frontend communicates with Django APIs automatically.

---

# 3. System Architecture

### **Backend – Django REST Framework**
- Validates tasks  
- Computes priority scores  
- Detects circular dependencies  
- Applies strategy-specific adjustments  
- Generates human-readable explanations  
- Exposes two endpoints:

```
POST /api/tasks/analyze/
POST /api/tasks/suggest/
```

### **Frontend – HTML + JavaScript**
- Interactive UI for adding tasks  
- JSON bulk paste loader  
- Suggestion & analysis panels  
- Dependency graph built using **vis-network.js**  
- Auto-highlighting of High/Medium/Low priority  

---

# 4. Algorithm Explanation 

The Smart Task Analyzer is built around a weighted scoring system that evaluates each task based on four core factors: **urgency**, **importance**, **effort**, and **dependency impact**. Each factor contributes to the final score using a customizable weight system, creating a flexible and context-aware prioritization framework.

**1. Urgency Score:**  
Urgency is calculated using the number of days left until the deadline. Tasks that are overdue receive the maximum urgency score. Tasks that are due soon are scaled proportionally based on how many days remain, while tasks with no deadlines receive a low urgency by default. This ensures that time-sensitive items rise to the top of the list.

**2. Importance Score:**  
Importance is normalized using the formula:  
```
(importance - 1) / 9
```  
This creates a smooth distribution between 0 and 1 regardless of whether the user enters small or large values. Highly important tasks contribute significantly to the final score, which helps favor impactful work.

**3. Effort Score:**  
Effort is modeled inversely:  
```
1 - (hours / max_hours)
```  
Smaller tasks get a higher score because they are easier to complete quickly. This is beneficial when a user chooses the “fast” strategy, which prioritizes low-effort, high-return tasks.

**4. Dependency Score:**  
A dependency graph is constructed where edges represent prerequisite relations. Tasks that unblock more tasks receive a higher dependency score:  
```
dependents / total_tasks
```  
This incentivizes completing “bottleneck tasks” early to improve workflow efficiency.

**Final Weighted Score:**  
The final priority score uses a weighted sum:  
```
score = urgency*w1 + importance*w2 + effort*w3 + dependency*w4
```

The system supports multiple strategies:  
- **Smart:** Balanced scoring.  
- **Fast:** Emphasizes low-effort tasks.  
- **Impact:** Emphasizes importance.  
- **Deadline:** Enforces stronger urgency scaling.

The algorithm also performs **circular dependency detection** using **Kahn's Topological Sorting Algorithm**. If tasks form a loop, the system rejects the input with an error.  
This prevents infinite loops and ensures a valid dependency graph.

Overall, the algorithm is deterministic, explainable, and tunable, making it ideal for real-world task management.

---

# 5. Design Decisions

###  Why Django REST Framework?
- Built-in validators  
- Quick API creation  
- Clean JSON handling  
- Easy error management  

### Why Not Use a Database?
Assignment goal: **real-time analysis**  
Tasks are stored in frontend memory only.

### Why vis-network.js?
- Lightweight graph library  
- Ideal for dependency visualization  
- Supports directional edges  

### Why Weighted Algorithm Instead of ML?
- Transparent results  
- No training required  
- Deterministic scoring  
- More reliable for small datasets  

### Why Top-3 Suggestions?
Matches user productivity patterns and prevents overload.

---

# 6. API Endpoints

## **POST /api/tasks/analyze/**
Request:
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

Response:
- Sorted tasks  
- Score breakdown  
- Explanation  

---

## **POST /api/tasks/suggest/**
Returns the **Top 3 tasks to do next**, with explanation.

---

# 7. Frontend Features

- Add tasks manually  
- Remove tasks  
- Paste JSON and load/append  
- Display priority badges (High/Medium/Low)  
- Strategy selector  
- Tooltip breakdowns  
- Graph visualization with arrows  
- Integration with backend APIs  

---

# 8. Time Breakdown

| Module | Time Spent |
|--------|------------|
| Backend Logic | ~40 min |
| Scoring Algorithm | ~45 min |
| API Development | ~30 min |
| Frontend UI | ~60 min |
| Graph Visualization | ~20 min |
| Testing | ~30 min |
| Documentation | ~20 min |
| **Total** | **~3.5 hours** |

---

# 9. Bonus Challenges Attempted

### Dependency Graph Visualization  
Implemented using **vis-network.js** with directional edges and live updates.

### Circular Dependency Detection  
Implemented fully using Kahn’s Algorithm.

### Score Explanations  
Each task includes a detailed breakdown tooltip.

---

# 10. Future Improvements

- Persist tasks using Django models  
- User authentication  
- Export results to PDF  
- Dark mode UI  
- Drag-and-drop Gantt chart  
- AI-generated suggestions  
- Shared team workspace  
- Voice-based task entry  

---

# 11. How to Run the Project

### Backend:
```
cd backend
python manage.py migrate
python manage.py runserver
```

### Frontend:
Open:
```
frontend/index.html
```


