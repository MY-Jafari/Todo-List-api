from rest_framework import serializers
from apps.todos.models import List, Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('task_id', 'created_at', 'updated_at')

class ListSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = List
        fields = '__all__'
        read_only_fields = ('list_id', 'created_at', 'updated_at', 'user')
