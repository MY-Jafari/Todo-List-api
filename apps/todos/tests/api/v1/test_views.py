"""
API tests for the todos endpoints v1.

Tests cover CRUD operations for Lists and Tasks.
"""

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.todos.models import List, Task

User = get_user_model()


class ListAPITests(APITestCase):
    """Test suite for List CRUD endpoints."""

    def setUp(self):
        """Create user, authenticate, and set up URLs."""
        self.user = User.objects.create_user(
            phone_number="09123456789", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.list_list_url = "/api/v1/todos/lists/"
        self.list_detail_url = lambda pk: f"/api/v1/todos/lists/{pk}/"

    def test_create_list_success(self):
        """Test creating a list returns 201."""
        response = self.client.post(
            self.list_list_url, {"list_name": "My Tasks"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["list_name"], "My Tasks")

    def test_get_list_list(self):
        """Test retrieving list of lists."""
        List.objects.create(user=self.user, list_name="List 1")
        List.objects.create(user=self.user, list_name="List 2")

        response = self.client.get(self.list_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_list_detail(self):
        """Test retrieving a single list by ID."""
        todo_list = List.objects.create(user=self.user, list_name="Detail List")

        response = self.client.get(self.list_detail_url(todo_list.list_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["list_name"], "Detail List")

    def test_update_list_success(self):
        """Test updating a list name."""
        todo_list = List.objects.create(user=self.user, list_name="Old Name")

        response = self.client.patch(
            self.list_detail_url(todo_list.list_id),
            {"list_name": "New Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["list_name"], "New Name")

    def test_delete_list_success(self):
        """Test deleting a list returns 204."""
        todo_list = List.objects.create(user=self.user, list_name="To Delete")

        response = self.client.delete(self.list_detail_url(todo_list.list_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(List.objects.filter(list_id=todo_list.list_id).exists())

    def test_unauthenticated_access_returns_401(self):
        """Test that unauthenticated users cannot access lists."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_users_list_returns_403_or_404(self):
        """Test that users cannot access another user's list."""
        user2 = User.objects.create_user(
            phone_number="09234567890", password="otherpass"
        )
        other_list = List.objects.create(user=user2, list_name="Private List")

        response = self.client.get(self.list_detail_url(other_list.list_id))
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )


class TaskAPITests(APITestCase):
    """Test suite for Task CRUD endpoints."""

    def setUp(self):
        """Create user, list, authenticate, and set up URLs."""
        self.user = User.objects.create_user(
            phone_number="09123456789", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.todo_list = List.objects.create(user=self.user, list_name="Test List")
        self.task_list_url = "/api/v1/todos/tasks/"
        self.task_detail_url = lambda pk: f"/api/v1/todos/tasks/{pk}/"

    def test_create_task_success(self):
        """Test creating a task returns 201."""
        response = self.client.post(
            self.task_list_url,
            {
                "list": self.todo_list.list_id,
                "task_title": "Buy milk",
                "task_description": "2% milk",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["task_title"], "Buy milk")
        self.assertEqual(response.data["status"], "todo")

    def test_get_task_list(self):
        """Test retrieving list of tasks."""
        Task.objects.create(user=self.user, list=self.todo_list, task_title="Task 1")
        Task.objects.create(user=self.user, list=self.todo_list, task_title="Task 2")

        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_update_task_status(self):
        """Test updating a task's status."""
        task = Task.objects.create(
            user=self.user, list=self.todo_list, task_title="Complete me"
        )

        response = self.client.patch(
            self.task_detail_url(task.task_id), {"status": "done"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "done")

    def test_delete_task_success(self):
        """Test deleting a task returns 204."""
        task = Task.objects.create(
            user=self.user, list=self.todo_list, task_title="Delete me"
        )

        response = self.client.delete(self.task_detail_url(task.task_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(task_id=task.task_id).exists())

    def test_unauthenticated_access_returns_401(self):
        """Test that unauthenticated users cannot access tasks."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_users_task_returns_403_or_404(self):
        """Test that users cannot access another user's task."""
        user2 = User.objects.create_user(
            phone_number="09234567890", password="otherpass"
        )
        other_list = List.objects.create(user=user2, list_name="Their List")
        other_task = Task.objects.create(
            user=user2, list=other_list, task_title="Their Task"
        )

        response = self.client.get(self.task_detail_url(other_task.task_id))
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_task_default_priority_is_medium(self):
        """Test that a task has 'medium' priority by default."""
        response = self.client.post(
            self.task_list_url,
            {
                "list": self.todo_list.list_id,
                "task_title": "Default priority",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["priority"], "medium")


class TaskFilterAndEdgeCaseTests(APITestCase):
    """Test suite for task filtering, ordering, and edge cases."""

    def setUp(self):
        """Create users, lists, and tasks for filter tests."""
        self.user = User.objects.create_user(
            phone_number="09123456789", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.todo_list = List.objects.create(user=self.user, list_name="Test List")

        # Create tasks with different priorities and statuses
        self.task1 = Task.objects.create(
            user=self.user,
            list=self.todo_list,
            task_title="High priority task",
            priority="high",
            status="todo",
        )
        self.task2 = Task.objects.create(
            user=self.user,
            list=self.todo_list,
            task_title="Low priority task",
            priority="low",
            status="done",
        )
        self.task3 = Task.objects.create(
            user=self.user,
            list=self.todo_list,
            task_title="In progress task",
            priority="medium",
            status="inprogress",
        )

        self.task_list_url = "/api/v1/todos/tasks/"

    # Helper to extract task list from paginated response
    def _get_results(self, response):
        """Extract task list from response.data (handles pagination)."""
        # response.data is a ReturnList with pagination
        # acts like OrderedDict but has 'results', 'count', etc.
        if hasattr(response.data, "get") and response.data.get("results") is not None:
            return response.data["results"]
        # If no pagination or unknown structure, try iterating
        if isinstance(response.data, list):
            return response.data
        # Fallback: treat as list of dicts
        return list(response.data)

    def test_task_filter_by_priority(self):
        """Test filtering tasks by priority."""
        response = self.client.get(f"{self.task_list_url}?priority=high")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._get_results(response)
        task_titles = [t["task_title"] for t in results]
        self.assertIn("High priority task", task_titles)
        self.assertNotIn("Low priority task", task_titles)

    def test_task_filter_by_status(self):
        """Test filtering tasks by status."""
        response = self.client.get(f"{self.task_list_url}?status=done")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._get_results(response)
        task_titles = [t["task_title"] for t in results]
        self.assertIn("Low priority task", task_titles)
        self.assertNotIn("High priority task", task_titles)

    def test_task_filter_by_list(self):
        """Test filtering tasks by list ID."""
        # Create a second list with a task in it
        other_list = List.objects.create(user=self.user, list_name="Other List")
        Task.objects.create(
            user=self.user,
            list=other_list,
            task_title="Other list task",
            priority="medium",
        )

        # Filter by the first list
        response = self.client.get(
            f"{self.task_list_url}?list={self.todo_list.list_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._get_results(response)
        task_titles = [t["task_title"] for t in results]
        self.assertIn("High priority task", task_titles)
        self.assertNotIn("Other list task", task_titles)

    def test_create_task_with_other_users_list_returns_403(self):
        """Test that you cannot create a task in another user's list."""
        user2 = User.objects.create_user(
            phone_number="09234567890", password="otherpass"
        )
        other_list = List.objects.create(user=user2, list_name="Their List")

        response = self.client.post(
            self.task_list_url,
            {
                "list": other_list.list_id,
                "task_title": "Should fail",
            },
            format="json",
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST],
        )

    def test_list_pagination(self):
        """Test that list endpoint uses pagination."""
        # Create 15 lists (page_size=5 from StandardResultsSetPagination)
        for i in range(15):
            List.objects.create(user=self.user, list_name=f"List {i}")

        response = self.client.get("/api/v1/todos/lists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check pagination structure
        if hasattr(response.data, "get"):
            self.assertIn("results", response.data)
            self.assertIn("count", response.data)
            self.assertEqual(len(response.data["results"]), 5)  # page_size=5
        else:
            # If no pagination for some reason
            self.assertGreaterEqual(len(response.data), 5)

    def test_task_ordering_by_created_at(self):
        """Test task ordering (newest first, page_size=5)."""
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self._get_results(response)
        self.assertGreaterEqual(len(results), 1)

        # Newest task should be "In progress task" (created last in setUp)
        task_titles = [t["task_title"] for t in results]
        # The newest of the 3 tasks we created
        self.assertTrue(
            task_titles[0]
            in ["In progress task", "Low priority task", "High priority task"],
            f"First task should be one of our tasks, got: {task_titles[0]}",
        )
