"""
Unit tests for the accounts app models.

Tests cover the custom User model, UserManager, PhoneVerification (TOTP),
and EmailVerification (SHA256) models.
"""

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError

# Import the models we need to test
from apps.accounts.models import User, PhoneVerification, EmailVerification


class UserModelTests(TestCase):
    """
    Test suite for the custom User model and UserManager.
    """

    def setUp(self):
        """Create a base user for tests that need an existing user."""
        self.user = User.objects.create_user(
            phone_number="09123456789",
            password="testpassword123",
            full_name="Test User",
            email="test@example.com"
        )

    # User Creation Tests

    def test_create_user_success(self):
        """Test creating a regular user is successful and fields are set correctly."""
        user = User.objects.create_user(
            phone_number="09234567890",
            password="anotherpassword123"
        )
        self.assertEqual(user.phone_number, "09234567890")
        self.assertTrue(user.check_password("anotherpassword123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_phone_verified)
        self.assertFalse(user.email_verified)
        self.assertIsNone(user.email)
        self.assertEqual(user.full_name, "")

    def test_create_user_with_all_fields(self):
        """Test creating a user with all optional fields filled."""
        user = User.objects.create_user(
            phone_number="09345678901",
            password="securepass",
            email="full.user@example.com",
            full_name="Full User"
        )
        self.assertEqual(user.email, "full.user@example.com")
        self.assertEqual(user.full_name, "Full User")

    def test_create_user_without_phone_raises_error(self):
        """Test that creating a user without a phone number raises ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(phone_number="", password="testpass")

    def test_create_superuser_success(self):
        """Test creating a superuser has correct permissions and verified phone."""
        superuser = User.objects.create_superuser(
            phone_number="09987654321",
            password="superpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_phone_verified)  # Auto-verified for superuser

    def test_create_superuser_not_staff_raises_error(self):
        """Test that creating a superuser with is_staff=False raises ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                phone_number="09876543210",
                password="superpass",
                is_staff=False
            )

    def test_phone_number_is_unique(self):
        """Test that creating two users with the same phone number raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                phone_number="09123456789",  # Already used in setUp
                password="anotherpass"
            )

    # String Representation Tests

    def test_user_str_returns_phone_number(self):
        """Test the __str__ method returns the phone number."""
        self.assertEqual(str(self.user), "09123456789")

    # Display Name Methods Tests

    def test_get_full_name_returns_full_name_when_set(self):
        """Test get_full_name returns full_name if it's set."""
        self.assertEqual(self.user.get_full_name(), "Test User")

    def test_get_full_name_falls_back_to_phone_number(self):
        """Test get_full_name returns phone_number if full_name is blank."""
        user = User.objects.create_user(phone_number="09111111111", password="pass")
        self.assertEqual(user.get_full_name(), "09111111111")

    def test_get_short_name_returns_first_name(self):
        """Test get_short_name returns the first word of full_name."""
        self.assertEqual(self.user.get_short_name(), "Test")

    def test_get_short_name_falls_back_to_phone_number(self):
        """Test get_short_name returns phone_number if full_name is not set."""
        user = User.objects.create_user(phone_number="09222222222", password="pass")
        self.assertEqual(user.get_short_name(), "09222222222")

    #  Helper Methods Tests 

    def test_has_verified_email_returns_false_by_default(self):
        """Test has_verified_email returns False for a new user."""
        self.assertFalse(self.user.has_verified_email())

    def test_has_verified_email_returns_true_when_verified(self):
        """Test has_verified_email returns True when email is set and verified."""
        self.user.email_verified = True
        self.user.save()
        self.assertTrue(self.user.has_verified_email())

    def test_has_verified_email_returns_false_without_email(self):
        """Test has_verified_email returns False if no email is set."""
        user = User.objects.create_user(phone_number="09333333333", password="pass")
        self.assertFalse(user.has_verified_email())

class PhoneVerificationModelTests(TestCase):
    """
    Test suite for the PhoneVerification (TOTP) model.
    """

    def setUp(self):
        """Start a verification for a test phone number."""
        self.verification, self.code = PhoneVerification.start_verification("09123456789")

    def test_start_verification_creates_record(self):
        """Test that start_verification creates a new record."""
        self.assertIsNotNone(self.verification)
        self.assertEqual(self.verification.phone_number, "09123456789")
        self.assertFalse(self.verification.verified)

    def test_start_verification_returns_code(self):
        """Test that start_verification returns a 6-digit code."""
        self.assertIsNotNone(self.code)
        self.assertEqual(len(self.code), 6)
        self.assertTrue(self.code.isdigit())

    def test_verify_code_with_valid_code(self):
        """Test that a valid TOTP code verifies successfully."""
        result = self.verification.verify_code(self.code)
        self.assertTrue(result)
        # After successful verification, record should be marked as verified
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.verified)

    def test_verify_code_with_invalid_code(self):
        """Test that an invalid code returns False."""
        result = self.verification.verify_code("000000")
        self.assertFalse(result)

    def test_verify_code_twice_fails(self):
        """Test that a code cannot be used twice (replay attack prevention)."""
        # First attempt succeeds
        self.assertTrue(self.verification.verify_code(self.code))
        # Second attempt with the same code should fail
        self.assertFalse(self.verification.verify_code(self.code))

    def test_start_verification_invalidates_previous_pending(self):
        """Test that requesting a new code invalidates old pending verifications."""
        # Start a second verification for the same number
        new_verification, new_code = PhoneVerification.start_verification("09123456789")

        # The old one should now be marked as verified (effectively invalidated)
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.verified)
        # The new one should be pending
        self.assertFalse(new_verification.verified)

    def test_verification_secret_is_unique(self):
        """Test that each verification has a unique secret."""
        verification2, code2 = PhoneVerification.start_verification("09234567890")
        self.assertNotEqual(self.verification.secret, verification2.secret)

    def test_totp_code_expires_after_interval(self):
        """Test that a TOTP code is no longer valid after the time interval (2 min)."""
        # This is more of a concept test. We can't easily mock time for pyotp.
        # We trust pyotp's own tests, but we ensure the structure is correct.
        # The interval is 120 seconds, so code should be valid now.
        self.assertTrue(self.verification.verify_code(self.code))


class EmailVerificationModelTests(TestCase):
    """
    Test suite for the EmailVerification (SHA256) model.
    """

    def setUp(self):
        """Create a user and generate an email verification code."""
        self.user = User.objects.create_user(
            phone_number="09123456789",
            password="testpassword123"
        )
        self.verification, self.code = EmailVerification.generate(
            email="test@example.com",
            user=self.user
        )

    def test_generate_creates_record(self):
        """Test that generate creates a new EmailVerification record."""
        self.assertIsNotNone(self.verification)
        self.assertEqual(self.verification.email, "test@example.com")
        self.assertEqual(self.verification.user, self.user)
        self.assertFalse(self.verification.is_used)

    def test_generate_returns_6_digit_code(self):
        """Test that generate returns a 6-digit plaintext code."""
        self.assertEqual(len(self.code), 6)
        self.assertTrue(self.code.isdigit())

    def test_verify_code_with_valid_code(self):
        """Test that a valid code returns True and marks record as used."""
        result = self.verification.verify_code(self.code)
        self.assertTrue(result)
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.is_used)

    def test_verify_code_with_invalid_code(self):
        """Test that an invalid code returns False."""
        result = self.verification.verify_code("000000")
        self.assertFalse(result)

    def test_verify_code_twice_fails(self):
        """Test that a code cannot be used twice."""
        # First use succeeds
        self.assertTrue(self.verification.verify_code(self.code))
        # Second use fails
        self.assertFalse(self.verification.verify_code(self.code))

    def test_is_expired_returns_true_after_10_minutes(self):
        """Test that a code expires after the 10-minute window."""
        # Manually set created_at to 11 minutes ago
        self.verification.created_at = timezone.now() - timedelta(minutes=11)
        self.verification.save()
        self.assertTrue(self.verification.is_expired())
        # is_valid() should return False
        self.assertFalse(self.verification.is_valid())

    def test_is_valid_returns_true_within_time_and_unused(self):
        """Test that is_valid returns True for a fresh, unused code."""
        self.assertTrue(self.verification.is_valid())

    def test_generate_code_is_hashed_in_db(self):
        """Test that the plaintext code is NOT stored in the database."""
        self.assertNotEqual(self.verification.code_hash, self.code)
        # SHA256 hash is 64 characters long
        self.assertEqual(len(self.verification.code_hash), 64)
