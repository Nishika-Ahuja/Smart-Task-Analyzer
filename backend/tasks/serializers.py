from rest_framework import serializers
from .models import Task
from datetime import datetime

class TaskInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)  # allow string/numeric ID
    title = serializers.CharField()
    due_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_hours = serializers.FloatField(required=False, default=1.0)
    importance = serializers.IntegerField(required=False, default=5)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    def validate_due_date(self, value):
        if value in (None, ''):
            return None
        try:
            # Expecting YYYY-MM-DD
            return datetime.fromisoformat(value).date()
        except Exception:
            raise serializers.ValidationError("due_date must be ISO format YYYY-MM-DD or empty")
    
    def validate_importance(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("importance must be integer between 1 and 10")
        return value

    def validate_estimated_hours(self, value):
        if value is None:
            return 1.0
        if value < 0:
            raise serializers.ValidationError("estimated_hours must be >= 0")
        return value
