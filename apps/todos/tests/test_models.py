"""
Unit tests for the todos app models.

Tests cover List and Task models.
"""

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from apps.todos.models import List, Task

User = get_user_model()


class ListModelTests(TestCase):
    """Test suite for the List model."""

    def setUp(self):
        """Create a test user for foreign key relations."""
        self.user = User.objects.create_user(
            phone_number="09123456789", password="testpass123"
        )

    def test_create_list_success(self):
        """Test creating a list with valid data."""
        todo_list = List.objects.create(user=self.user, list_name="My Work Tasks")

        self.assertEqual(todo_list.list_name, "My Work Tasks")
        self.assertEqual(todo_list.user, self.user)
        self.assertIsNotNone(todo_list.created_at)

    def test_create_list_without_user_raises_error(self):
        """Test that creating a list without user fails."""
        with self.assertRaises(IntegrityError):
            List.objects.create(list_name="Orphan List")

    def test_list_str_returns_list_name(self):
        """Test __str__ returns the list name."""
        todo_list = List.objects.create(user=self.user, list_name="Personal")
        self.assertEqual(str(todo_list), "Personal")

    def test_two_users_can_have_same_list_name(self):
        """Test that two users can have lists with the same name."""
        user2 = User.objects.create_user(
            phone_number="09234567890", password="testpass456"
        )

        List.objects.create(user=self.user, list_name="Work")
        List.objects.create(user=user2, list_name="Work")

        self.assertEqual(List.objects.filter(list_name="Work").count(), 2)


class TaskModelTests(TestCase):
    """Test suite for the Task model."""

    def setUp(self):
        """Create a user and a list for task tests."""
        self.user = User.objects.create_user(
            phone_number="09123456789", password="testpass123"
        )
        self.todo_list = List.objects.create(user=self.user, list_name="Test List")

    def test_create_task_success(self):
        """Test creating a task with valid data."""
        task = Task.objects.create(
            user=self.user,
            list=self.todo_list,
            task_title="Buy groceries",
            task_description="Milk, eggs, bread",
        )

        self.assertEqual(task.task_title, "Buy groceries")
        self.assertEqual(task.task_description, "Milk, eggs, bread")
        self.assertEqual(task.list, self.todo_list)
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, "todo")
        self.assertIsNotNone(task.created_at)

    def test_task_priority_choices(self):
        """Test that task priority accepts valid choices."""
        task = Task.objects.create(
            user=self.user,
            list=self.todo_list,
            task_title="Urgent task",
            priority="high",
        )
        self.assertEqual(task.priority, "high")

    def test_task_status_choices(self):
        """Test that task status accepts valid choices."""
        task = Task.objects.create(
            user=self.user,
            list=self.todo_list,
            task_title="In progress task",
            status="inprogress",
        )
        self.assertEqual(task.status, "inprogress")

    def test_task_default_status_is_todo(self):
        """Test that new tasks have 'todo' status by default."""
        task = Task.objects.create(
            user=self.user, list=self.todo_list, task_title="Default status task"
        )
        self.assertEqual(task.status, "todo")

    def test_task_str_returns_task_title(self):
        """Test __str__ returns the task title."""
        task = Task.objects.create(
            user=self.user, list=self.todo_list, task_title="Read a book"
        )
        self.assertEqual(str(task), "Read a book")
