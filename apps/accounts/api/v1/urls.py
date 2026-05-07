"""
URL configuration for accounts API v1.

Defines endpoints for phone verification and registration.
"""

from django.urls import path
from . import views

app_name = 'accounts-v1'

urlpatterns = [
    path(
        'send-otp/',
        views.SendOTPView.as_view(),
        name='send-otp'
    ),
    path(
        'verify-otp-register/',
        views.VerifyOTPAndRegisterView.as_view(),
        name='verify-otp-register'
    ),
]
