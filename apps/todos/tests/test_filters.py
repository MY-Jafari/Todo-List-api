import pytest
from django.contrib.auth import get_user_model
from apps.todos.models import Task, List
from apps.todos.filters import TaskFilter

User = get_user_model()


@pytest.mark.django_db
def test_task_filtering():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="password"
    )
    list1 = List.objects.create(user=user, list_name="List 1")
    list2 = List.objects.create(user=user, list_name="List 2")

    Task.objects.create(
        user=user, list=list1, task_title="Buy Milk", priority="low", status="todo"
    )
    Task.objects.create(
        user=user,
        list=list1,
        task_title="Buy Bread",
        priority="medium",
        status="inprogress",
    )
    Task.objects.create(
        user=user, list=list2, task_title="Read Book", priority="high", status="done"
    )

    queryset = Task.objects.all()
    data = {"search": "Buy", "status": "todo"}
    filterset = TaskFilter(data=data, queryset=queryset)
    filtered_qs = filterset.qs

    assert filtered_qs.count() == 1
    assert filtered_qs.first().task_title == "Buy Milk"
