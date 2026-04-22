from django.urls import path
from .views import ListCreateView, ListRetrieveUpdateDestroyView, TaskCreateView, TaskListCreateForListView, TaskRetrieveUpdateDestroyView

urlpatterns = [
    # List URLs
    path('lists/', ListCreateView.as_view(), name='list-create'),
    path('lists/<int:pk>/', ListRetrieveUpdateDestroyView.as_view(), name='list-detail'),
    
    # Task URLs  
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('lists/<int:list_id>/tasks/', TaskListCreateForListView.as_view(), name='tasks-by-list')

]
