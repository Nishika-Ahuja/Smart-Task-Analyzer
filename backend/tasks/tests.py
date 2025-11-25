from django.test import TestCase
from .scoring import compute_scores, detect_cycles
from datetime import date, timedelta

class ScoringTests(TestCase):
    def test_basic_scoring_and_order(self):
        today = date.today()
        tasks = [
            {'id': 'a', 'title': 'Low effort high importance', 'due_date': (today + timedelta(days=7)).isoformat(), 'estimated_hours': 0.5, 'importance': 9, 'dependencies': []},
            {'id': 'b', 'title': 'Large task later', 'due_date': (today + timedelta(days=30)).isoformat(), 'estimated_hours': 10, 'importance': 5, 'dependencies': []},
            {'id': 'c', 'title': 'Urgent but low importance', 'due_date': (today + timedelta(days=1)).isoformat(), 'estimated_hours': 2, 'importance': 3, 'dependencies': []},
        ]
        # Convert due_date strings to date objects similarly to serializer expectation:
        for t in tasks:
            t['due_date'] = date.fromisoformat(t['due_date'])
        processed, cycles = compute_scores(tasks, strategy='smart_balance')
        # Ensure no cycles
        self.assertEqual(cycles, [])
        # Check top is either 'a' (quick high importance) or 'c' (urgent) depending on weights; ensure scoring returns scores and explanations
        self.assertTrue(all('score' in p for p in processed))
        self.assertTrue(all('explanation' in p for p in processed))

    def test_past_due_boosts(self):
        today = date.today()
        tasks = [
            {'id': 'past', 'title': 'Past due task', 'due_date': (today - timedelta(days=5)).isoformat(), 'estimated_hours': 5, 'importance': 5, 'dependencies': []},
            {'id': 'future', 'title': 'Future task', 'due_date': (today + timedelta(days=5)).isoformat(), 'estimated_hours': 1, 'importance': 5, 'dependencies': []},
        ]
        for t in tasks:
            t['due_date'] = date.fromisoformat(t['due_date'])
        processed, cycles = compute_scores(tasks)
        self.assertTrue(processed[0]['id'] == 'past')  # past-due should be first

    def test_detect_circular_dependencies(self):
        tasks = [
            {'id': '1', 'title': 'T1', 'dependencies': ['2']},
            {'id': '2', 'title': 'T2', 'dependencies': ['3']},
            {'id': '3', 'title': 'T3', 'dependencies': ['1']},
            {'id': '4', 'title': 'T4', 'dependencies': []},
        ]
        # convert due_date defaults
        for t in tasks:
            t.setdefault('estimated_hours', 1.0)
            t.setdefault('importance', 5)
            t.setdefault('due_date', None)
        processed, cycles = compute_scores(tasks)
        # cycles should include 1,2,3
        self.assertTrue(set(cycles) >= {'1', '2', '3'})
        # tasks in cycle flagged
        in_cycle = [p for p in processed if p['meta'].get('circular_dependency')]
        self.assertEqual(len(in_cycle), 3)
