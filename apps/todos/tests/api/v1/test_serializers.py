import pytest
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.todos.models import List, Task
from apps.todos.api.v1.serializers import ListSerializer, TaskSerializer

User = get_user_model()

@pytest.mark.django_db
class TestListSerializer:
    def test_list_serializer_valid(self):
        user = User.objects.create_user(
            username='testuser',
            password='password',
            email='testuser@example.com'
        )
        data = {'list_name': 'Groceries', 'description': 'Weekly shopping list'}
        serializer = ListSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_list_serializer_invalid(self):
        data = {'list_name': ''}  
        serializer = ListSerializer(data=data)
        assert not serializer.is_valid()
        assert 'list_name' in serializer.errors

    def test_list_serializer_read_only_fields(self):
        user = User.objects.create_user(
            username='testuser',
            password='password',
            email='testuser@example.com'
        )
        list_obj = List.objects.create(user=user, list_name='Old List')
        data = {
            'list_name': 'Updated List',
            'list_id': 99,
            'created_at': '2023-01-01T10:00:00Z'
        }
        serializer = ListSerializer(instance=list_obj, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        list_obj.refresh_from_db()
        assert list_obj.list_name == 'Updated List'
        assert list_obj.list_id != 99 


@pytest.mark.django_db
class TestTaskSerializer:
    def test_task_serializer_valid(self):
        user = User.objects.create_user(
            username='testuser',
            password='password',
            email='testuser@example.com'
        )
        list_obj = List.objects.create(user=user, list_name='Test List')
        data = {
            'user': user.id, 
            'list': list_obj.list_id,
            'task_title': 'Buy Groceries',
            'task_description': 'Milk, Eggs, Bread',
            'priority': 'high',
            'status': 'todo'
        }
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_task_serializer_invalid(self):
        data = {'task_title': 'test test test'}
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()
        assert 'list' in serializer.errors
        assert 'user' in serializer.errors
        assert 'task_title' not in serializer.errors

    def test_task_serializer_read_only_fields(self):
        user = User.objects.create_user(
            username='testuser',
            password='password',
            email='testuser@example.com'
        )
        list_obj = List.objects.create(user=user, list_name='Test List')
        task_obj = Task.objects.create(
            user=user, 
            list=list_obj,
            task_title='Old Task'
        )
        data = {
            'task_title': 'New Task',
            'task_id': 99,
            'created_at': '2023-01-01T10:00:00Z'
        }
        serializer = TaskSerializer(instance=task_obj, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        task_obj.refresh_from_db() 
        assert task_obj.task_title == 'New Task'
        assert task_obj.task_id != 99
