from rest_framework import generics, serializers, status , permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .serializers import ListSerializer, TaskSerializer
from apps.todos.models import List, Task

# List Views
class ListCreateView(generics.CreateAPIView):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class ListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

# Task Views
class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        list_id_from_data = self.request.data.get('list') 

        if not list_id_from_data:
            raise serializers.ValidationError({"list": "List ID is required in the request data."})

        try:
            # Retrieve the List object, ensuring it belongs to the current user
            list_obj = List.objects.get(list_id=list_id_from_data, user=self.request.user)
            # Save the task, linking it to the retrieved list object
            serializer.save(list=list_obj) 
        except List.DoesNotExist:
            raise PermissionDenied("You do not have permission to access this list or the list is not found.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while creating the task: {e}")
class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        #task belong to the current user .
        return self.queryset.filter(list__user=self.request.user)
    
class TaskListCreateForListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        list_id_from_url = self.kwargs.get('list_id') 

        if not list_id_from_url:
            raise NotFound("list_id not found in URL parameters.")

        try:
            # Retrieve the List object to ensure it exists and the user has access
            List.objects.get(list_id=list_id_from_url, user=self.request.user)
            # Filter tasks for the specific list. The Task model uses 'list_id' as the foreign key field.
            return Task.objects.filter(list_id=list_id_from_url) 
        except List.DoesNotExist:
            raise PermissionDenied("You don't have permissions to access this list.")

    def perform_create(self, serializer):
        list_id_from_url = self.kwargs.get('list_id') 

        if not list_id_from_url:
            raise serializers.ValidationError({"list": "List ID is required in the URL."}) # Adjusted error message

        try:
            # Retrieve the List object, ensuring it belongs to the current user
            list_obj = List.objects.get(list_id=list_id_from_url, user=self.request.user)
            # Save the task, linking it to the retrieved list object
            serializer.save(list=list_obj) 
        except List.DoesNotExist:
            raise PermissionDenied("You don't have permissions to access this list.")
        except Exception as e:
            # Catch any other unexpected errors during task creation
            raise Exception(f"An unexpected error occurred while creating the task for list {list_id_from_url}: {e}")
