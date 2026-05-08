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

    # Email verification
    path('send-email-verification/', views.SendEmailVerificationView.as_view(), name='send-email-verification'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),

    # Password reset
    path('password-reset/request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
