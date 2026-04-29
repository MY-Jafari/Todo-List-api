from rest_framework import generics, mixins, serializers, permissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied, NotFound
from .serializers import ListSerializer, TaskSerializer
from apps.todos.models import List, Task
from ...filters import TaskFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


# List Views
class ListCreateView(generics.ListCreateAPIView):
    """
    List and create todo lists.

    get: Get all lists for the authenticated user.
    post: Create a new todo list.
    """

    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return List.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete a specific todo list.

    get: Get list details by list_id.
    put: Update a list.
    patch: Partially update a list.
    delete: Delete a list and its tasks.
    """

    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "list_id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# Task Views
class TaskCreateView(generics.ListCreateAPIView):
    """
    List and create tasks.

    get: Get all tasks for the authenticated user with optional filtering.
    post: Create a new task in a specified list.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    ordering = ["-created_at"]

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = (
                kwargs["data"].copy()
                if hasattr(kwargs["data"], "copy")
                else dict(kwargs["data"])
            )
            data["user"] = self.request.user.id
            kwargs["data"] = data
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        list_id_from_data = self.request.data.get("list")

        if not list_id_from_data:
            raise serializers.ValidationError(
                {"list": "List ID is required in the request data."}
            )

        try:
            list_obj = List.objects.get(
                list_id=list_id_from_data, user=self.request.user
            )
            serializer.save(user=self.request.user, list=list_obj)
        except List.DoesNotExist:
            raise PermissionDenied(
                "You do not have permission to access this list or the list is not found."
            )
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while creating the task: {e}"
            )

    def get_queryset(self):
        return Task.objects.filter(list__user=self.request.user)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete a specific task.

    get: Get task details by ID.
    put: Update a task.
    patch: Partially update a task (e.g., status or priority).
    delete: Delete a task.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = (
                kwargs["data"].copy()
                if hasattr(kwargs["data"], "copy")
                else dict(kwargs["data"])
            )
            data["user"] = self.request.user.id
            kwargs["data"] = data
        return super().get_serializer(*args, **kwargs)

    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save(user=self.request.user, list=instance.list)

    def get_queryset(self):
        return self.queryset.filter(list__user=self.request.user)


class TaskListCreateForListView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    """
    List and create tasks for a specific todo list.

    get: Get all tasks in a list by list_id.
    post: Create a new task in the specified list.
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    ordering = ["-created_at"]

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = (
                kwargs["data"].copy()
                if hasattr(kwargs["data"], "copy")
                else dict(kwargs["data"])
            )
            data["user"] = self.request.user.id
            kwargs["data"] = data
        return super().get_serializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        list_id_from_url = self.kwargs.get("list_id")
        if not list_id_from_url:
            raise serializers.ValidationError(
                {"list": "List ID is required in the URL."}
            )
        try:
            list_obj = List.objects.get(
                list_id=list_id_from_url, user=self.request.user
            )
            serializer.save(user=self.request.user, list=list_obj)
        except List.DoesNotExist:
            raise PermissionDenied("You don't have permissions to access this list.")
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while creating the task for list {list_id_from_url}: {e}"
            )

    def get_queryset(self):
        list_id = self.kwargs.get("list_id")
        if not list_id:
            raise NotFound("list_id not found in URL parameters.")
        return Task.objects.filter(list_id=list_id, list__user=self.request.user)

    def get_list_object(self):
        list_id_from_url = self.kwargs.get("list_id")
        if not list_id_from_url:
            raise NotFound("list_id not found in URL parameters.")
        try:
            return List.objects.get(list_id=list_id_from_url, user=self.request.user)
        except List.DoesNotExist:
            raise PermissionDenied("You don't have permissions to access this list.")
