"""
Serializers for the accounts API v1.

Handles validation and deserialization of registration, login,
and verification requests.
"""

import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import PhoneVerification

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for requesting a phone verification code for registration.

    Validates that the phone number is a valid Iranian mobile
    and is not already registered.
    """
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        help_text=_('Iranian phone number (11 digits, starting with 09).')
    )

    def validate_phone_number(self, value):
        """
        Validate Iranian mobile number and uniqueness.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            serializers.ValidationError: If format is invalid or already registered.
        """
        pattern = r'^09\d{9}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                _('Invalid phone number format. '
                  'Must be 11 digits starting with 09 (e.g., 09123456789).')
            )

        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                _('This phone number is already registered.')
            )

        return value


class VerifyOTPAndRegisterSerializer(serializers.Serializer):
    """
    Serializer for verifying TOTP and completing registration.

    Uses a JWT verification_token to identify the verification session.
    """
    verification_token = serializers.CharField(
        help_text=_('JWT verification token from send-otp response.')
    )
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text=_('6-digit TOTP code sent to the phone.')
    )
    password = serializers.CharField(
        min_length=6,
        write_only=True,
        help_text=_('Password for the new account (minimum 6 characters).')
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text=_('Optional email address.')
    )
    full_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text=_('Optional full name.')
    )

    def validate(self, data):
        """
        Decode JWT verification token and verify TOTP code.

        Args:
            data (dict): Input data with verification_token and otp_code.

        Returns:
            dict: Validated data with phone_number added.

        Raises:
            serializers.ValidationError: If token or code is invalid.
        """
        verification_token = data['verification_token']
        otp_code = data['otp_code']

        # Decode JWT verification token
        try:
            token = AccessToken(verification_token)
            phone_number = token.get('phone_number')
            verification_id = token.get('verification_id')

            if not phone_number or not verification_id:
                raise serializers.ValidationError(
                    _('Invalid verification token.')
                )

        except TokenError:
            raise serializers.ValidationError(
                _('Expired or invalid verification token. '
                  'Please request a new code.')
            )

        # Find the verification record
        try:
            verification = PhoneVerification.objects.get(
                id=verification_id,
                phone_number=phone_number,
                verified=False
            )
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError(
                _('Verification session not found. '
                  'Please request a new code.')
            )

        # Verify TOTP code
        if not verification.verify_code(otp_code):
            raise serializers.ValidationError(
                _('Invalid or expired verification code.')
            )

        data['phone_number'] = phone_number
        return data


class SendLoginOTPSerializer(serializers.Serializer):
    """
    Serializer for requesting a login OTP code.

    Validates that the phone number belongs to an existing user.
    """
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        help_text=_('Registered Iranian phone number (11 digits, starting with 09).')
    )

    def validate_phone_number(self, value):
        """
        Validate Iranian mobile format and check if registered.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            serializers.ValidationError: If format is invalid or not registered.
        """
        pattern = r'^09\d{9}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                _('Invalid phone number format. '
                  'Must be 11 digits starting with 09 (e.g., 09123456789).')
            )

        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                _('No account found with this phone number.')
            )

        return value


class VerifyLoginOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying login OTP and completing authentication.

    Uses a JWT verification_token to identify the verification session.
    """
    verification_token = serializers.CharField(
        help_text=_('JWT verification token from send-login-otp response.')
    )
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text=_('6-digit TOTP code sent to the phone.')
    )

    def validate(self, data):
        """
        Decode JWT verification token and verify TOTP code for login.

        Args:
            data (dict): Input data with verification_token and otp_code.

        Returns:
            dict: Validated data with phone_number added.

        Raises:
            serializers.ValidationError: If token or code is invalid.
        """
        verification_token = data['verification_token']
        otp_code = data['otp_code']

        # Decode JWT verification token
        try:
            token = AccessToken(verification_token)
            phone_number = token.get('phone_number')
            verification_id = token.get('verification_id')

            if not phone_number or not verification_id:
                raise serializers.ValidationError(
                    _('Invalid verification token.')
                )

        except TokenError:
            raise serializers.ValidationError(
                _('Expired or invalid verification token. '
                  'Please request a new code.')
            )

        # Find the verification record
        try:
            verification = PhoneVerification.objects.get(
                id=verification_id,
                phone_number=phone_number,
                verified=False
            )
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError(
                _('Verification session not found. '
                  'Please request a new code.')
            )

        # Verify TOTP code
        if not verification.verify_code(otp_code):
            raise serializers.ValidationError(
                _('Invalid or expired verification code.')
            )

        data['phone_number'] = phone_number
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for password-based login.

    This is the default login method. Users must provide
    their phone number and password.
    """
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        help_text=_('Registered phone number.')
    )
    password = serializers.CharField(
        write_only=True,
        help_text=_('Account password.')
    )

    def validate_phone_number(self, value):
        """
        Validate Iranian mobile format.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            serializers.ValidationError: If format is invalid.
        """
        pattern = r'^09\d{9}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                _('Invalid phone number format. '
                  'Must be 11 digits starting with 09 (e.g., 09123456789).')
            )

        return value

class SendEmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for requesting an email verification code.

    Validates that the email is not already taken by another user.
    Requires authentication - the user must be logged in.
    """
    email = serializers.EmailField(
        help_text=_('Email address to verify.')
    )

    def validate_email(self, value):
        """
        Check that the email is not already used by another verified user.

        Args:
            value (str): The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            serializers.ValidationError: If email is already taken
                or user is not authenticated.
        """
        user = self.context['request'].user

        # Ensure user is authenticated
        if user.is_anonymous:
            raise serializers.ValidationError(
                _('Authentication is required.')
            )

        # Check if any other user has this email verified
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                _('This email is already registered by another user.')
            )

        return value


class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for verifying an email verification code.

    Validates the code against the stored EmailVerification record.
    """
    email = serializers.EmailField(
        help_text=_('Email address being verified.')
    )
    code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text=_('6-digit verification code sent to the email.')
    )

    def validate(self, data):
        """
        Verify the code against the stored EmailVerification record.

        Args:
            data (dict): Input data with email and code.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If code is invalid, expired,
                or user is not authenticated.
        """
        from apps.accounts.models import EmailVerification

        user = self.context['request'].user

        # Ensure user is authenticated
        if user.is_anonymous:
            raise serializers.ValidationError(
                _('Authentication is required.')
            )

        email = data['email']
        code = data['code']

        try:
            verification = EmailVerification.objects.filter(
                email=email,
                user=user,
                is_used=False
            ).latest('created_at')
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError(
                _('No verification code found for this email. '
                  'Please request a new code.')
            )

        if not verification.verify_code(code):
            raise serializers.ValidationError(
                _('Invalid or expired verification code.')
            )

        return data
