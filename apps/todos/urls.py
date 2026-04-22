from django.urls import path, include

urlpatterns = [
    path('api/', include([
        path('v1/', include('apps.todos.api.v1.urls')),
    ])),
]
