"""
Serializers for the accounts API v1.

Handles validation and deserialization of registration requests.
"""

import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import PhoneVerification

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for requesting a phone verification code.

    Validates that the provided phone number is a valid Iranian
    mobile number and is not already registered.
    """
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        help_text=_('Iranian phone number (11 digits, starting with 09).')
    )

    def validate_phone_number(self, value):
        """
        Validate that the phone number is a valid Iranian mobile number.

        Checks:
            1. Exactly 11 digits
            2. Starts with '09'
            3. All remaining characters are digits
            4. Not already registered

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            serializers.ValidationError: If format is invalid or already registered.
        """
        # Regex pattern for Iranian mobile numbers: 09 + 9 digits = 11 digits
        pattern = r'^09\d{9}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                _('Invalid phone number format. '
                  'Must be 11 digits starting with 09 (e.g., 09123456789).')
            )

        # Check if phone number is already registered
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                _('This phone number is already registered.')
            )

        return value


class VerifyOTPAndRegisterSerializer(serializers.Serializer):
    """
    Serializer for verifying a TOTP code and completing registration.

    Uses a session_token from the send-otp response instead of
    requiring the user to re-enter their phone number.
    """
    session_token = serializers.CharField(
        help_text=_('Session token received from the send-otp response.')
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
        Verify the session token and TOTP code.

        Validates that the session token is valid and matches
        a pending phone verification, then checks the TOTP code
        against the stored secret.

        Args:
            data (dict): The input data.

        Returns:
            dict: The validated data with phone_number added.

        Raises:
            serializers.ValidationError: If session token is invalid
                or the code is incorrect/expired.
        """
        session_token = data['session_token']
        otp_code = data['otp_code']

        # Find the verification record by session token
        try:
            verification = PhoneVerification.objects.get(
                session_token=session_token,
                verified=False
            )
        except PhoneVerification.DoesNotExist:
            raise serializers.ValidationError(
                _('Invalid or expired session token. '
                  'Please request a new verification code.')
            )

        # Verify the TOTP code
        if not verification.verify_code(otp_code):
            raise serializers.ValidationError(
                _('Invalid or expired verification code.')
            )

        # Add the phone number from verification to validated data
        data['phone_number'] = verification.phone_number
        return data
