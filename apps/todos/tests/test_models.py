import pytest
from django.contrib.auth import get_user_model
from apps.todos.models import List, Task

User = get_user_model()


@pytest.mark.django_db
class TestListModel:
    def test_create_list(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        list_instance = List.objects.create(
            user=user, list_name="My Test List", description="A description"
        )
        assert list_instance.list_name == "My Test List"
        assert str(list_instance) == "My Test List"


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        list_instance = List.objects.create(user=user, list_name="Test List")
        task = Task.objects.create(
            user=user,
            list=list_instance,
            task_title="Test Task",
            task_description="Task description",
            priority="high",
            status="inprogress",
        )
        assert task.task_title == "Test Task"
        assert str(task) == "Test Task"
        assert task.priority == "high"
        assert task.status == "inprogress"
