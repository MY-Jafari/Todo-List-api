from django.urls import path, include

urlpatterns = [
    
    path("", include("apps.todos.api.v1.urls")),
]
