"""
API views for the accounts app v1.

Handles phone verification and user registration endpoints.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from apps.accounts.models import PhoneVerification
from apps.accounts.notifications import send_phone_verification_code
from .serializers import (
    SendOTPSerializer,
    VerifyOTPAndRegisterSerializer,
)

User = get_user_model()

# Minimum cooldown time between OTP requests (in seconds)
OTP_COOLDOWN_SECONDS = 120  # 2 minutes


def get_tokens_for_user(user):
    """
    Generate JWT access and refresh tokens for a user.

    Args:
        user (User): The authenticated user instance.

    Returns:
        dict: Contains 'refresh' and 'access' token strings.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SendOTPView(generics.GenericAPIView):
    """
    API endpoint to request a phone verification code.

    POST /api/v1/auth/send-otp/

    Returns a session_token to use in the verify-otp-register step
    instead of requiring the user to re-enter their phone number.

    Request Body:
        {"phone_number": "09123456789"}

    Response (200 OK):
        {
            "detail": "Verification code sent.",
            "session_token": "abc123-def456-..."
        }
    """
    serializer_class = SendOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle OTP sending request with rate limiting."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        # Rate limiting: Check if a code was recently sent to this number
        recent_verification = PhoneVerification.objects.filter(
            phone_number=phone_number,
            created_at__gte=timezone.now() - timedelta(seconds=OTP_COOLDOWN_SECONDS)
        ).order_by('-created_at').first()

        if recent_verification:
            # Calculate remaining cooldown time
            cooldown_end = recent_verification.created_at + timedelta(
                seconds=OTP_COOLDOWN_SECONDS
            )
            remaining_seconds = int(
                (cooldown_end - timezone.now()).total_seconds()
            )

            if remaining_seconds > 0:
                return Response(
                    {
                        'detail': _(
                            'Please wait %(seconds)d seconds before requesting '
                            'a new code.'
                        ) % {'seconds': remaining_seconds}
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # Generate a new TOTP secret and get the current valid code
        verification, code = PhoneVerification.start_verification(phone_number)

        # Send the code via the notification layer
        send_phone_verification_code(phone_number, code)

        return Response(
            {
                'detail': _('Verification code sent.'),
                'session_token': verification.session_token,
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPAndRegisterView(generics.GenericAPIView):
    """
    API endpoint to verify TOTP code and complete registration.

    POST /api/v1/auth/verify-otp-register/

    Uses session_token from send-otp response instead of phone_number.

    Request Body:
        {
            "session_token": "abc123-def456-...",
            "otp_code": "123456",
            "password": "securepass123",
            "email": "optional@example.com",
            "full_name": "Optional Name"
        }

    Response (201 Created):
        {
            "detail": "Registration successful.",
            "user": {...},
            "tokens": {...}
        }
    """
    serializer_class = VerifyOTPAndRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle registration verification and user creation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Create the user with verified phone number
        user = User.objects.create_user(
            phone_number=data['phone_number'],
            password=data['password'],
            email=data.get('email'),
            full_name=data.get('full_name'),
            is_phone_verified=True
        )

        # Generate JWT tokens for immediate login
        tokens = get_tokens_for_user(user)

        return Response(
            {
                'detail': _('Registration successful.'),
                'user': {
                    'phone_number': user.phone_number,
                    'full_name': user.full_name,
                    'email': user.email,
                },
                'tokens': tokens,
            },
            status=status.HTTP_201_CREATED
        )
