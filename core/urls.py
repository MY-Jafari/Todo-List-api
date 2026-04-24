from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("todos/", include("apps.todos.urls")),
    path("api/", include("apps.todos.urls")),
]
