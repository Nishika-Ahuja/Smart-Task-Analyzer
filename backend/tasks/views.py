# backend/tasks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer
from .scoring import compute_scores, STRATEGIES
from datetime import date
from rest_framework.decorators import api_view
import json

class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    Accepts JSON array of tasks and optional strategy or custom weights.
    Returns tasks sorted by computed score and cycles (if any).
    """
    def post(self, request):
        payload = request.data
        # Accept either {"tasks": [...] , "strategy": "..."} or bare list
        if isinstance(payload, dict) and 'tasks' in payload:
            tasks_in = payload['tasks']
            strategy = payload.get('strategy', 'smart_balance')
            custom_weights = payload.get('weights')
        elif isinstance(payload, list):
            tasks_in = payload
            strategy = request.query_params.get('strategy', 'smart_balance')
            custom_weights = None
        else:
            return Response({'error': 'Request must be a list of tasks or object with "tasks" key.'}, status=status.HTTP_400_BAD_REQUEST)

        validated = []
        errors = []
        for i, t in enumerate(tasks_in):
            ser = TaskInputSerializer(data=t)
            if not ser.is_valid():
                errors.append({'index': i, 'errors': ser.errors})
            else:
                validated.append(ser.validated_data)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        # Convert due_date back to date objects (serializers validated)
        processed, cycles = compute_scores(validated, strategy=strategy, custom_weights=custom_weights)
        # Build response
        out = []
        for p in processed:
            out.append({
                'id': p['id'],
                'title': p['title'],
                'due_date': p['due_date'].isoformat() if p['due_date'] else None,
                'estimated_hours': p['estimated_hours'],
                'importance': p['importance'],
                'dependencies': p['dependencies'],
                'score': p['score'],
                'explanation': p['explanation'],
                'meta': p['meta']
            })
        return Response({'tasks': out, 'cycles': cycles})

class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/?strategy=...
    Expects tasks to be provided in request body (POST-style), because we need task data.
    Because the assignment requests GET, we accept tasks via JSON in body of GET
    (some clients don't send body with GET — alternative: accept POST for suggest).
    For robustness, support both body and query param 'tasks' (JSON-encoded).
    """
    def get(self, request):
        # Extract tasks from body or query param
        try:
            if request.body:
                payload = json.loads(request.body.decode('utf-8'))
            else:
                payload = {}
        except Exception:
            payload = {}

        tasks_in = None
        if isinstance(payload, dict) and 'tasks' in payload:
            tasks_in = payload['tasks']
        else:
            qp = request.query_params.get('tasks')
            if qp:
                try:
                    tasks_in = json.loads(qp)
                except Exception:
                    return Response({'error': 'Invalid JSON in query param tasks'}, status=status.HTTP_400_BAD_REQUEST)

        if tasks_in is None:
            return Response({'error': 'GET /api/tasks/suggest/ requires tasks list in request body or tasks query param'}, status=status.HTTP_400_BAD_REQUEST)

        strategy = request.query_params.get('strategy', 'smart_balance')

        # Validate
        validated = []
        errors = []
        for i, t in enumerate(tasks_in):
            ser = TaskInputSerializer(data=t)
            if not ser.is_valid():
                errors.append({'index': i, 'errors': ser.errors})
            else:
                validated.append(ser.validated_data)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        processed, cycles = compute_scores(validated, strategy=strategy)
        # Pick top 3 with explanations
        top3 = processed[:3]
        suggestions = []
        for p in top3:
            suggestions.append({
                'id': p['id'],
                'title': p['title'],
                'score': p['score'],
                'explanation': p['explanation'],
                'why': _build_suggestion_explanation(p)
            })
        return Response({'suggestions': suggestions, 'cycles': cycles})

def _build_suggestion_explanation(p):
    # Friendly sentences for UI
    parts = []
    if p['meta'].get('circular_dependency'):
        parts.append('This task is part of a circular dependency — resolving it will unblock others.')
    if p['days_until_due'] is not None:
        if p['days_until_due'] < 0:
            parts.append(f"It is past due by {abs(p['days_until_due'])} day(s).")
        elif p['days_until_due'] <= 2:
            parts.append(f"Due in {p['days_until_due']} day(s) — urgent.")
    if p['dependents_count'] > 0:
        parts.append(f"Blocks {p['dependents_count']} other task(s).")
    if p['estimated_hours'] <= 1.0:
        parts.append("Quick win (low estimated hours).")
    if not parts:
        parts.append("Selected based on combined urgency, importance and effort.")
    return " ".join(parts)
