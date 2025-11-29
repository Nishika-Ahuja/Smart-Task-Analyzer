from rest_framework import serializers
from .models import Task

class TaskModelSerializer(serializers.ModelSerializer):
    dependencies = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), many=True, required=False)

    class Meta:
        model = Task
        fields = ["id", "title", "due_date", "estimated_hours", "importance", "dependencies"]

class InputTaskSerializer(serializers.Serializer):
   
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, default=1.0)
    importance = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)
    dependencies = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
