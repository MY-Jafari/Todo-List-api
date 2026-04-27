import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    #ordering
    o = django_filters.OrderingFilter(
        # Which fields to allow for ordering
        fields=(
            ('status', 'status'),
            ('priority', 'priority'),
            ('task_title', 'task_title'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'status': 'Status',
            'priority': 'Priority',
            'task_title': 'Title',
            'created_at': 'Creation Date',
        }
    )

    class Meta:
        model = Task
        fields = ['status', 'priority', 'list', 'task_title']
