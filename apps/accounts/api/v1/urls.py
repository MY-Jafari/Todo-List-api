"""
URL configuration for accounts API v1.
"""

from django.urls import path
from . import views

app_name = 'accounts-v1'

urlpatterns = [
    # Registration
    path('send-otp/', views.SendOTPView.as_view(), name='send-otp'),
    path('verify-otp-register/', views.VerifyOTPAndRegisterView.as_view(), name='verify-otp-register'),

    # Login (password)
    path('login/', views.LoginView.as_view(), name='login'),

    # Login (OTP)
    path('send-login-otp/', views.SendLoginOTPView.as_view(), name='send-login-otp'),
    path('verify-login-otp/', views.VerifyLoginOTPView.as_view(), name='verify-login-otp'),
]
