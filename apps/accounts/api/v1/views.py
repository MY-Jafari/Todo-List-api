"""
API views for the accounts app v1.

Handles phone verification, user registration, and login endpoints.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate

from apps.accounts.models import PhoneVerification, EmailVerification
from apps.accounts.notifications import (
    send_phone_verification_code,
    send_email_verification_code,
)
from .serializers import (
    SendOTPSerializer,
    VerifyOTPAndRegisterSerializer,
    SendLoginOTPSerializer,
    VerifyLoginOTPSerializer,
    LoginSerializer,
    SendEmailVerificationSerializer,
    VerifyEmailSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

User = get_user_model()

# Cooldown time between OTP requests (seconds)
OTP_COOLDOWN_SECONDS = 120  # 2 minutes

# Expiration time for verification token (minutes)
VERIFICATION_TOKEN_MINUTES = 2


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
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def create_verification_token(phone_number, verification_id):
    """
    Create a short-lived JWT token for verification flows.

    Stateless token that carries phone_number and verification_id
    for the verify step without requiring server-side storage.

    Args:
        phone_number (str): Phone number being verified.
        verification_id (str): ID of the PhoneVerification record.

    Returns:
        str: Encoded JWT access token (valid for 2 minutes).
    """
    token = RefreshToken()
    token["phone_number"] = phone_number
    token["verification_id"] = verification_id
    token.set_exp(lifetime=timedelta(minutes=VERIFICATION_TOKEN_MINUTES))
    return str(token.access_token)


class SendOTPView(generics.GenericAPIView):
    """
    API endpoint to request a verification code for registration.

    POST /api/v1/auth/send-otp/

    Request Body:
        {"phone_number": "09123456789"}

    Response:
        {"detail": "Verification code sent.", "verification_token": "eyJ..."}
    """

    serializer_class = SendOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # Rate limiting check
        recent = (
            PhoneVerification.objects.filter(
                phone_number=phone_number,
                created_at__gte=timezone.now()
                - timedelta(seconds=OTP_COOLDOWN_SECONDS),
            )
            .order_by("-created_at")
            .first()
        )

        if recent:
            remaining = int(
                (
                    recent.created_at
                    + timedelta(seconds=OTP_COOLDOWN_SECONDS)
                    - timezone.now()
                ).total_seconds()
            )
            if remaining > 0:
                return Response(
                    {"detail": _(f"Please wait {remaining} seconds.")},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        verification, code = PhoneVerification.start_verification(phone_number)
        verification_token = create_verification_token(
            phone_number, str(verification.id)
        )
        send_phone_verification_code(phone_number, code)

        return Response(
            {
                "detail": _("Verification code sent."),
                "verification_token": verification_token,
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPAndRegisterView(generics.GenericAPIView):
    """
    Verify OTP and complete registration.

    POST /api/v1/auth/verify-otp-register/

    Request Body:
        {
            "verification_token": "eyJ...",
            "otp_code": "123456",
            "password": "securepass123",
            "email": "optional@example.com",
            "full_name": "Optional Name"
        }

    Response: {"detail": "Registration successful.", "user": {...}, "tokens": {...}}
    """

    serializer_class = VerifyOTPAndRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.create_user(
            phone_number=data["phone_number"],
            password=data["password"],
            email=data.get("email"),
            full_name=data.get("full_name"),
            is_phone_verified=True,
        )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "detail": _("Registration successful."),
                "user": {
                    "phone_number": user.phone_number,
                    "full_name": user.full_name,
                    "email": user.email,
                },
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class SendLoginOTPView(generics.GenericAPIView):
    """
    Request a one-time password for login.

    POST /api/v1/auth/send-login-otp/

    Request Body:
        {"phone_number": "09123456789"}

    Response:
        {"detail": "Login code sent.", "verification_token": "eyJ..."}
    """

    serializer_class = SendLoginOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # Rate limiting
        recent = (
            PhoneVerification.objects.filter(
                phone_number=phone_number,
                created_at__gte=timezone.now()
                - timedelta(seconds=OTP_COOLDOWN_SECONDS),
            )
            .order_by("-created_at")
            .first()
        )

        if recent:
            remaining = int(
                (
                    recent.created_at
                    + timedelta(seconds=OTP_COOLDOWN_SECONDS)
                    - timezone.now()
                ).total_seconds()
            )
            if remaining > 0:
                return Response(
                    {"detail": _(f"Please wait {remaining} seconds.")},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        verification, code = PhoneVerification.start_verification(phone_number)
        verification_token = create_verification_token(
            phone_number, str(verification.id)
        )
        send_phone_verification_code(phone_number, code)

        return Response(
            {"detail": _("Login code sent."), "verification_token": verification_token},
            status=status.HTTP_200_OK,
        )


class VerifyLoginOTPView(generics.GenericAPIView):
    """
    Verify login OTP and return access tokens.

    POST /api/v1/auth/verify-login-otp/

    Request Body:
        {
            "verification_token": "eyJ...",
            "otp_code": "123456"
        }

    Response:
        {"detail": "Login successful.", "user": {...}, "tokens": {...}}
    """

    serializer_class = VerifyLoginOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"detail": _("User not found.")}, status=status.HTTP_404_NOT_FOUND
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "detail": _("Login successful."),
                "user": {
                    "phone_number": user.phone_number,
                    "full_name": user.full_name,
                    "email": user.email,
                },
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class LoginView(generics.GenericAPIView):
    """
    Login with phone number and password (default method).

    POST /api/v1/auth/login/

    Request Body:
        {
            "phone_number": "09123456789",
            "password": "mysecret123"
        }

    Response:
        {"detail": "Login successful.", "user": {...}, "tokens": {...}}
    """

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        user = authenticate(request, phone_number=phone_number, password=password)

        if user is None:
            return Response(
                {"detail": _("Invalid phone number or password.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "detail": _("Login successful."),
                "user": {
                    "phone_number": user.phone_number,
                    "full_name": user.full_name,
                    "email": user.email,
                },
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class SendEmailVerificationView(generics.GenericAPIView):
    """
    Send a verification code to the user's email address.

    POST /api/v1/auth/send-email-verification/

    Requires authentication. The user must be logged in.

    Request Body:
        {"email": "user@example.com"}

    Response (200 OK):
        {"detail": "Verification code sent."}
    """

    serializer_class = SendEmailVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle email verification code sending."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Generate verification code and send email
        verification, code = EmailVerification.generate(email=email, user=request.user)
        send_email_verification_code(email, code)

        return Response(
            {"detail": _("Verification code sent to your email.")},
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(generics.GenericAPIView):
    """
    Verify email address with the sent code.

    POST /api/v1/auth/verify-email/

    Requires authentication.

    Request Body:
        {"email": "user@example.com", "code": "123456"}

    Response (200 OK):
        {"detail": "Email verified successfully."}
    """

    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle email verification."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Update user's email verification status
        user = request.user
        user.email = email
        user.email_verified = True
        user.save(update_fields=["email", "email_verified"])

        return Response(
            {"detail": _("Email verified successfully.")}, status=status.HTTP_200_OK
        )


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # Rate limiting
        recent = (
            PhoneVerification.objects.filter(
                phone_number=phone_number,
                created_at__gte=timezone.now()
                - timedelta(seconds=OTP_COOLDOWN_SECONDS),
            )
            .order_by("-created_at")
            .first()
        )

        if recent:
            remaining = int(
                (
                    recent.created_at
                    + timedelta(seconds=OTP_COOLDOWN_SECONDS)
                    - timezone.now()
                ).total_seconds()
            )
            if remaining > 0:
                return Response(
                    {"detail": _(f"Please wait {remaining} seconds.")},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        # Generate TOTP
        verification, code = PhoneVerification.start_verification(phone_number)
        verification_token = create_verification_token(
            phone_number, str(verification.id)
        )
        send_phone_verification_code(phone_number, code)

        return Response(
            {
                "detail": _("Password reset code sent."),
                "verification_token": verification_token,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm password reset with OTP and set new password.

    POST /api/v1/auth/password-reset/confirm/

    Verifies the OTP code and sets a new password for the user.

    Request Body:
        {
            "verification_token": "eyJ...",
            "otp_code": "123456",
            "new_password": "newsecurepass123"
        }

    Response (200 OK):
        {"detail": "Password has been reset successfully."}
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle password reset confirmation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": _("Password has been reset successfully.")},
            status=status.HTTP_200_OK,
        )
