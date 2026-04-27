from rest_framework import generics, mixins, serializers, permissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .serializers import ListSerializer, TaskSerializer
from apps.todos.models import List, Task
from ...filters import TaskFilter


# pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


# List Views
class ListCreateView(generics.ListCreateAPIView):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return List.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return List.objects.filter(user=self.request.user)


class ListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "list_id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# Task Views
class TaskCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def perform_create(self, serializer):
        list_id_from_data = self.request.data.get("list")

        if not list_id_from_data:
            raise serializers.ValidationError(
                {"list": "List ID is required in the request data."}
            )

        try:
            # Retrieve the List object, ensuring it belongs to the current user
            list_obj = List.objects.get(
                list_id=list_id_from_data, user=self.request.user
            )
            # Save the task, linking it to the retrieved list object
            serializer.save(list=list_obj)
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
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # task belong to the current user .
        return self.queryset.filter(list__user=self.request.user)


class TaskListCreateForListView(
    mixins.ListModelMixin,  
    mixins.CreateModelMixin,  
    generics.GenericAPIView,  
):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # The 'create' method internally calls perform_create after validation.
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        list_id_from_url = self.kwargs.get("list_id")
        if not list_id_from_url:
            raise serializers.ValidationError(
                {"list": "List ID is required in the URL."}
            )
        try:
            # Retrieve the List object again to ensure it belongs to the current user.
            list_obj = List.objects.get(
                list_id=list_id_from_url, user=self.request.user
            )
            serializer.save(list=list_obj)
        except List.DoesNotExist:
            raise PermissionDenied("You don't have permissions to access this list.")
        except Exception as e:
            # Catch any other unexpected errors during task creation.
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
            # Verify that the list exists and is associated with the authenticated user.
            return List.objects.get(list_id=list_id_from_url, user=self.request.user)
        except List.DoesNotExist:
            raise PermissionDenied("You don't have permissions to access this list.")
