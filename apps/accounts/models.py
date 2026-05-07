"""
Core models for the accounts app.
This module defines a fully custom User model built from scratch
using AbstractBaseUser and PermissionsMixin.
"""

import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import pyotp
import hashlib
import secrets


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Handles creation of regular users and superusers using phone_number
    as the unique identifier instead of a traditional username field.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and return a regular user with the given phone number and password.

        Args:
            phone_number (str): The user's unique phone number.
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields to set on the user model.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If phone_number is not provided.
        """
        if not phone_number:
            raise ValueError(_("Phone number is required."))

        # Normalize the phone number if needed (e.g., remove spaces)
        # phone_number = self.normalize_phone(phone_number)  # Future enhancement

        user = self.model(phone_number=phone_number, **extra_fields)

        # Hash the password before saving
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Create and return a superuser with all permissions granted.

        Superusers automatically get is_staff, is_superuser, is_active,
        and is_phone_verified set to True.

        Args:
            phone_number (str): The superuser's unique phone number.
            password (str, optional): The superuser's password. Defaults to None.
            **extra_fields: Additional fields to set on the user model.

        Returns:
            User: The created superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_phone_verified", True)

        # Enforce that superusers must have staff and superuser flags set to True
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Fully custom User model built from scratch.

    Replaces Django's default User model with a phone_number-based
    authentication system. The phone_number field serves as the unique
    identifier for login instead of a username or email.

    Attributes:
        phone_number (CharField): Unique phone number used for authentication.
        email (EmailField): Optional email address for the user.
        email_verified (BooleanField): Whether the user's email has been verified.
        full_name (CharField): The user's full name (optional).
        is_active (BooleanField): Whether the user account is active.
        is_staff (BooleanField): Whether the user can access the admin panel.
        is_phone_verified (BooleanField): Whether the phone number has been verified.
        date_joined (DateTimeField): The date and time the user registered.
    """

    #  Contact & Identity Fields
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name=_("phone number"),
        help_text=_("Unique phone number used for login and contact."),
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("email address"),
        help_text=_("Optional email address. Will be visible in admin panel."),
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_("email verified"),
        help_text=_("Indicates whether the user has verified their email."),
    )
    full_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("full name"),
        help_text=_("Optional full name of the user."),
    )

    #  Status & Permission Fields
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("active"),
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("staff status"),
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name=_("phone verified"),
        help_text=_("Indicates whether the phone number has been verified via OTP."),
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("date joined"),
        help_text=_("The date and time when the user registered."),
    )

    #  Model Configuration
    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []  # phone_number + password are sufficient for createsuperuser

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        # Add database indexes for frequently queried fields
        indexes = [
            models.Index(fields=["phone_number"], name="phone_number_idx"),
            models.Index(fields=["email"], name="email_idx"),
        ]
        ordering = ["-date_joined"]  # Newest users first

    #  String Representation
    def __str__(self):
        """Return the phone number as the string representation of the user."""
        return self.phone_number

    # Display Name Methods
    def get_full_name(self):
        """
        Return the user's full name.

        Falls back to phone_number if no full_name is set.
        This method is required by Django's admin interface.
        """
        return self.full_name or self.phone_number

    def get_short_name(self):
        """
        Return the short name for the user.

        Returns the first part of full_name if available,
        otherwise falls back to phone_number.
        This method is required by Django's admin interface.
        """
        if self.full_name:
            return self.full_name.split()[0]
        return self.phone_number

    # Helper Methods
    def has_verified_email(self):
        """
        Check if the user has both an email address and has verified it.

        Returns:
            bool: True if email exists and is verified, False otherwise.
        """
        return bool(self.email and self.email_verified)

    def has_verified_phone(self):
        """
        Check if the user's phone number has been verified.

        Returns:
            bool: True if phone is verified, False otherwise.
        """
        return self.is_phone_verified


class PhoneVerification(models.Model):
    """
    Stores a TOTP secret key for phone number verification.

    Uses Time-based One-Time Password (TOTP) via pyotp.
    No need to store OTP codes in the database — they are
    generated and verified using the secret and current time.

    Attributes:
        phone_number (CharField): The phone number being verified.
        session_token (CharField): A unique token used to link the
            send-otp and verify-otp steps without exposing the phone number.
        secret (CharField): Base32 secret used to generate TOTP codes.
        created_at (DateTimeField): When this verification record was created.
        verified (BooleanField): Whether the phone has been verified.
    """
    phone_number = models.CharField(
        max_length=11,
        verbose_name=_('phone number'),
        help_text=_('The phone number being verified.')
    )
    session_token = models.CharField(
        max_length=64,
        unique=True,
        default=uuid.uuid4,
        verbose_name=_('session token'),
        help_text=_('Unique token to identify this verification session.')
    )
    secret = models.CharField(
        max_length=32,
        verbose_name=_('TOTP secret'),
        help_text=_('Base32 secret key for TOTP generation.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
        help_text=_('When this verification was initiated.')
    )
    verified = models.BooleanField(
        default=False,
        verbose_name=_('verified'),
        help_text=_('Whether verification was successful.')
    )

    class Meta:
        verbose_name = _('phone verification')
        verbose_name_plural = _('phone verifications')
        indexes = [
            models.Index(fields=['phone_number', 'verified'], name='phone_verify_idx'),
            models.Index(fields=['session_token'], name='session_token_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        """Return a string representation of the verification attempt."""
        status = 'verified' if self.verified else 'pending'
        return f'Verification for {self.phone_number} ({status})'

    @classmethod
    def start_verification(cls, phone_number):
        """
        Begin a new verification process for the given phone number.

        - Cancels any previous pending verifications for this phone.
        - Generates a new TOTP secret and saves it.
        - Returns the current valid TOTP code.

        Args:
            phone_number (str): The phone number to verify.

        Returns:
            tuple: (PhoneVerification instance, current_otp_code)
        """
        # Mark all previous pending verifications as expired/verified
        cls.objects.filter(phone_number=phone_number, verified=False).update(
            verified=True  # Effectively invalidates old secrets
        )

        # Generate a new secret and create record
        secret = pyotp.random_base32()
        verification = cls.objects.create(
            phone_number=phone_number,
            secret=secret
        )

        # Generate the current TOTP code (valid for 120 seconds)
        totp = pyotp.TOTP(secret, interval=120)
        code = totp.now()

        return verification, code

    def verify_code(self, code):
        """
        Verify a TOTP code against this verification's secret.

        The code is valid for the configured interval (default 120 seconds)
        and can be verified once within that window. After successful
        verification, this record is marked as verified.

        Args:
            code (str): The 6-digit code entered by the user.

        Returns:
            bool: True if the code is valid, False otherwise.
        """
        if self.verified:
            return False  # Already verified, prevent reuse

        totp = pyotp.TOTP(self.secret, interval=120)

        # valid_window=0 means only current time window, no drift
        if totp.verify(code, valid_window=0):
            self.verified = True
            self.save(update_fields=['verified'])
            return True

        return False
class EmailVerification(models.Model):
    """
    Stores email verification codes securely using SHA256 hashing.

    The plaintext code is never stored in the database. Only its hash
    is persisted. The code is sent to the user's email and verified
    by comparing hashes.

    Attributes:
        email (EmailField): The email address being verified.
        user (ForeignKey): The user requesting the verification.
        code_hash (CharField): SHA256 hash of the verification code.
        created_at (DateTimeField): When this verification was created.
        is_used (BooleanField): Whether the code has been used.
    """

    email = models.EmailField(
        verbose_name=_("email address"), help_text=_("The email being verified.")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_verifications",
        verbose_name=_("user"),
        help_text=_("The user verifying their email."),
    )
    code_hash = models.CharField(
        max_length=64,
        verbose_name=_("code hash"),
        help_text=_("SHA256 hash of the plaintext verification code."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text=_("When this verification code was generated."),
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_("is used"),
        help_text=_("Whether this code has already been used."),
    )

    class Meta:
        verbose_name = _("email verification")
        verbose_name_plural = _("email verifications")
        indexes = [
            models.Index(fields=["email", "is_used"], name="email_verify_idx"),
            models.Index(fields=["user", "is_used"], name="user_email_verify_idx"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        """Return a string representation of the verification attempt."""
        return f"Email verification for {self.email}"

    def is_expired(self):
        """
        Check if the verification code has expired.

        Codes are valid for 10 minutes.

        Returns:
            bool: True if expired, False otherwise.
        """
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() > expiration_time

    def is_valid(self):
        """
        Check if the verification is still valid.

        Valid means: not used yet and not expired.

        Returns:
            bool: True if valid, False otherwise.
        """
        return not self.is_used and not self.is_expired()

    @classmethod
    def generate(cls, email, user):
        """
        Generate a new verification code for the given email and user.

        - Cancels any previous unused codes for this email+user.
        - Creates a random 6-digit code.
        - Stores only the SHA256 hash of the code.
        - Returns the instance and the plaintext code (to send to the user).

        Args:
            email (str): The email to verify.
            user (User): The user requesting verification.

        Returns:
            tuple: (EmailVerification instance, plaintext_code)
        """
        # Invalidate previous codes for this email+user
        cls.objects.filter(email=email, user=user, is_used=False).update(is_used=True)

        # Generate a cryptographically secure random 6-digit code
        plaintext_code = "".join(str(secrets.randbelow(10)) for _ in range(6))

        # Hash the code before storing
        code_hash = hashlib.sha256(plaintext_code.encode()).hexdigest()

        verification = cls.objects.create(email=email, user=user, code_hash=code_hash)

        return verification, plaintext_code

    def verify_code(self, code):
        """
        Verify a plaintext code against the stored hash.

        Args:
            code (str): The 6-digit code entered by the user.

        Returns:
            bool: True if the code matches and is valid, False otherwise.
        """
        if not self.is_valid():
            return False

        # Hash the input code and compare with stored hash
        input_hash = hashlib.sha256(code.encode()).hexdigest()

        if input_hash == self.code_hash:
            self.is_used = True
            self.save(update_fields=["is_used"])
            return True

        return False
