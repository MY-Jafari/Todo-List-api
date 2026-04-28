import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.todos.models import List, Task

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_user(api_client):
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password'
    )
    api_client.force_authenticate(user=user)
    return user, api_client

@pytest.mark.django_db
def test_list_create_view(authenticated_user):
    user, client = authenticated_user
    url = reverse("list-list-create")
    data = {"list_name": "My New List", "description": "This is a test list"}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data["list_name"] == "My New List"
    assert List.objects.filter(user=user, list_name="My New List").exists()

@pytest.mark.django_db
def test_list_retrieve_update_destroy_view(authenticated_user):
    user, client = authenticated_user
    list_obj = List.objects.create(user=user, list_name="To Update")
    url = reverse("list-detail", kwargs={"list_id": list_obj.list_id})

    # Retrieve
    response_get = client.get(url)
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.data["list_name"] == "To Update"

    # Update
    update_data = {"list_name": "Updated List Name"}
    response_put = client.put(url, update_data)
    assert response_put.status_code == status.HTTP_200_OK, response_put.data
    
    list_obj.refresh_from_db()
    assert list_obj.list_name == "Updated List Name"

    # Destroy
    response_delete = client.delete(url)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT
    assert not List.objects.filter(pk=list_obj.pk).exists()

@pytest.mark.django_db
def test_task_create_view(authenticated_user):
    user, client = authenticated_user
    list_obj = List.objects.create(user=user, list_name="Tasks for List")
    url = reverse("task-create")
    data = {
        "list": list_obj.list_id,
        "task_title": "New Task for List",
        "priority": "high",
        "status": "todo"
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data["task_title"] == "New Task for List"
    assert Task.objects.filter(list=list_obj, task_title="New Task for List").exists()

@pytest.mark.django_db
def test_task_create_view_invalid_list(authenticated_user):
    user, client = authenticated_user
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='password'
    )
    other_list = List.objects.create(user=other_user, list_name="Other User's List")
    
    url = reverse("task-create")
    data = {
        "list": other_list.list_id,
        "task_title": "Task for Wrong List",
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.data

@pytest.mark.django_db
def test_task_list_create_for_list_view(authenticated_user):
    user, client = authenticated_user
    list_obj = List.objects.create(user=user, list_name="Specific List")
    url = reverse("tasks-by-list", kwargs={"list_id": list_obj.list_id})

    task_data = {
        "task_title": "Task in Specific List",
        "list": list_obj.list_id
    }
    response_post = client.post(url, task_data)
    assert response_post.status_code == status.HTTP_201_CREATED, response_post.data
    assert Task.objects.filter(list=list_obj, task_title="Task in Specific List").exists()

    response_get = client.get(url)
    assert response_get.status_code == status.HTTP_200_OK
    assert len(response_get.data["results"]) == 1
    assert response_get.data["results"][0]["task_title"] == "Task in Specific List"

@pytest.mark.django_db
def test_task_retrieve_update_destroy_view(authenticated_user):
    user, client = authenticated_user
    list_obj = List.objects.create(user=user, list_name="Tasks List")
    task_obj = Task.objects.create(
        user=user,
        list=list_obj,
        task_title="Task to Manage",
        status='todo'
    )
    url = reverse("task-detail", kwargs={"pk": task_obj.task_id})

    # Retrieve
    response_get = client.get(url)
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.data["task_title"] == "Task to Manage"

    update_data = {
        "status": "done",
        "priority": "low"
    }
    response_patch = client.patch(url, update_data, format='json')
    assert response_patch.status_code == status.HTTP_200_OK, response_patch.data
    
    task_obj.refresh_from_db()
    assert task_obj.status == "done"
    assert task_obj.priority == "low"

    # Destroy
    response_delete = client.delete(url)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(pk=task_obj.pk).exists()
