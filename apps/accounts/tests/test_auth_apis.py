"""
API tests for the authentication endpoints.

Covers registration (send-otp, verify-otp-register) and login flows.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User, PhoneVerification


class RegistrationAPITests(APITestCase):
    """
    Test suite for the registration API endpoints.

    Flow:
    1. POST /api/v1/auth/send-otp/ → recive verification_token
    2. POST /api/v1/auth/verify-otp-register/ → create user + JWT
    """

    def setUp(self):
        """Set up test URLs and base data."""
        self.send_otp_url = reverse("accounts-v1:send-otp")
        self.verify_register_url = reverse("accounts-v1:verify-otp-register")
        self.valid_phone = "09123456789"

    #  Helper Methods

    def _request_otp(self, phone_number="09123456789"):
        """
        Helper: Request OTP and return both the verification_token
        and the OTP code from the created verification record.

        Returns:
            tuple: (verification_token, otp_code)
        """
        response = self.client.post(
            self.send_otp_url, {"phone_number": phone_number}, format="json"
        )
        token = response.data["verification_token"]

        # Get the code from the latest pending verification
        verification = PhoneVerification.objects.filter(
            phone_number=phone_number, verified=False
        ).latest("created_at")

        # Generate the current TOTP code from the secret
        import pyotp

        totp = pyotp.TOTP(verification.secret, interval=120)
        code = totp.now()

        return token, code

    #  Send OTP Tests

    def test_send_otp_success(self):
        """
        Test that requesting an OTP for a new phone number succeeds.
        Should return 200 OK with a verification_token.
        """
        response = self.client.post(
            self.send_otp_url, {"phone_number": self.valid_phone}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("verification_token", response.data)
        self.assertIn("detail", response.data)

        # Verify a PhoneVerification record was created
        self.assertTrue(
            PhoneVerification.objects.filter(
                phone_number=self.valid_phone, verified=False
            ).exists()
        )

    def test_send_otp_existing_phone_returns_400(self):
        """
        Test that requesting OTP for an already registered number fails.
        """
        # Create a user first
        User.objects.create_user(phone_number=self.valid_phone, password="testpass")

        response = self.client.post(
            self.send_otp_url, {"phone_number": self.valid_phone}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_otp_invalid_phone_format_returns_400(self):
        """
        Test that invalid Iranian phone numbers are rejected.
        """
        invalid_numbers = [
            "0912345678",  # 10 digits
            "091234567890",  # 12 digits
            "+989123456789",  # with country code
            "08123456789",  # doesn't start with 09
            "abc",  # not even a number
        ]

        for phone in invalid_numbers:
            response = self.client.post(
                self.send_otp_url, {"phone_number": phone}, format="json"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Expected 400 for phone: {phone}",
            )

    #  Verify OTP & Register Tests

    def test_verify_otp_register_success(self):
        """
        Test the full registration flow with a valid OTP.
        Should create a user and return JWT tokens.
        """
        token, code = self._request_otp(self.valid_phone)

        response = self.client.post(
            self.verify_register_url,
            {
                "verification_token": token,
                "otp_code": code,
                "password": "securepass123",
                "email": "test@example.com",
                "full_name": "Test User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["phone_number"], self.valid_phone)

        # Verify user was created in the database
        user = User.objects.get(phone_number=self.valid_phone)
        self.assertTrue(user.is_phone_verified)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.full_name, "Test User")

    def test_verify_otp_wrong_code_returns_400(self):
        """
        Test that verification with a wrong OTP code fails.
        """
        token, code = self._request_otp(self.valid_phone)

        response = self.client.post(
            self.verify_register_url,
            {
                "verification_token": token,
                "otp_code": "000000",  # Wrong code
                "password": "securepass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_no_token_returns_400(self):
        """
        Test that verification without a valid token fails.
        """
        response = self.client.post(
            self.verify_register_url,
            {
                "verification_token": "invalid_token_here",
                "otp_code": "000000",
                "password": "securepass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_password_too_short_returns_400(self):
        """
        Test that a short password is rejected.
        """
        token, code = self._request_otp(self.valid_phone)

        response = self.client.post(
            self.verify_register_url,
            {
                "verification_token": token,
                "otp_code": code,
                "password": "123",  # Too short (min 6 chars)
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_creates_verified_phone_user(self):
        """
        Test that a user created via registration has is_phone_verified=True.
        """
        token, code = self._request_otp(self.valid_phone)

        self.client.post(
            self.verify_register_url,
            {
                "verification_token": token,
                "otp_code": code,
                "password": "securepass123",
            },
            format="json",
        )

        user = User.objects.get(phone_number=self.valid_phone)
        self.assertTrue(user.is_phone_verified)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class LoginAPITests(APITestCase):
    """
    Test suite for login endpoints.

    Covers:
    1. Password-based login
    2. OTP-based login (send-login-otp + verify-login-otp)
    """

    def setUp(self):
        """Create a registered user and set up URLs."""
        self.login_url = reverse("accounts-v1:login")
        self.send_login_otp_url = reverse("accounts-v1:send-login-otp")
        self.verify_login_otp_url = reverse("accounts-v1:verify-login-otp")

        # Create a test user
        self.phone_number = "09123456789"
        self.password = "securepass123"
        self.user = User.objects.create_user(
            phone_number=self.phone_number,
            password=self.password,
            full_name="Test User",
            is_phone_verified=True,
        )

    #  Password Login Tests

    def test_login_with_password_success(self):
        """
        Test login with correct phone number and password.
        Should return 200 OK with JWT tokens.
        """
        response = self.client.post(
            self.login_url,
            {
                "phone_number": self.phone_number,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["phone_number"], self.phone_number)
        self.assertEqual(response.data["user"]["full_name"], "Test User")

    def test_login_with_wrong_password_returns_401(self):
        """
        Test login with wrong password fails.
        """
        response = self.client.post(
            self.login_url,
            {
                "phone_number": self.phone_number,
                "password": "wrongpassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_phone_returns_401(self):
        """
        Test login with a phone number that is not registered.
        """
        response = self.client.post(
            self.login_url,
            {
                "phone_number": "09999999999",
                "password": "somepass",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_without_password_returns_400(self):
        """
        Test login without providing password fails.
        """
        response = self.client.post(
            self.login_url,
            {
                "phone_number": self.phone_number,
                # password missing
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #  OTP Login Tests

    def test_send_login_otp_success(self):
        """
        Test that requesting login OTP for a registered user succeeds.
        """
        response = self.client.post(
            self.send_login_otp_url, {"phone_number": self.phone_number}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("verification_token", response.data)

    def test_send_login_otp_unregistered_phone_returns_400(self):
        """
        Test that requesting login OTP for unregistered number fails.
        """
        response = self.client.post(
            self.send_login_otp_url, {"phone_number": "09999999999"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_login_otp_success(self):
        """
        Test full OTP login flow: request → verify → get tokens.
        """
        # Step 1: Request login OTP
        response = self.client.post(
            self.send_login_otp_url, {"phone_number": self.phone_number}, format="json"
        )
        token = response.data["verification_token"]

        # Get the OTP code from the latest verification
        import pyotp

        verification = PhoneVerification.objects.filter(
            phone_number=self.phone_number, verified=False
        ).latest("created_at")
        totp = pyotp.TOTP(verification.secret, interval=120)
        code = totp.now()

        # Step 2: Verify OTP
        response = self.client.post(
            self.verify_login_otp_url,
            {
                "verification_token": token,
                "otp_code": code,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["phone_number"], self.phone_number)

    def test_verify_login_otp_wrong_code_returns_400(self):
        """
        Test that wrong OTP code for login fails.
        """
        response = self.client.post(
            self.send_login_otp_url, {"phone_number": self.phone_number}, format="json"
        )
        token = response.data["verification_token"]

        response = self.client.post(
            self.verify_login_otp_url,
            {
                "verification_token": token,
                "otp_code": "000000",  # Wrong
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailVerificationAPITests(APITestCase):
    """
    Test suite for email verification endpoints.
    Requires authentication (JWT token).
    """

    def setUp(self):
        """Create a user, log in, and set up URLs."""
        self.send_email_url = reverse("accounts-v1:send-email-verification")
        self.verify_email_url = reverse("accounts-v1:verify-email")

        # Create and authenticate user
        self.user = User.objects.create_user(
            phone_number="09123456789", password="testpass123", is_phone_verified=True
        )
        self.client.force_authenticate(user=self.user)

    def test_send_email_verification_success(self):
        """
        Test sending verification code to email.
        Should return 200 OK.
        """
        response = self.client.post(
            self.send_email_url, {"email": "test@example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_send_email_verification_without_auth_returns_401(self):
        """
        Test that unauthenticated users cannot send email verification.
        """
        # Remove authentication
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.send_email_url, {"email": "test@example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_email_success(self):
        """
        Test full email verification flow.
        """
        from apps.accounts.models import EmailVerification

        # Generate verification code
        verification, code = EmailVerification.generate(
            email="verify@example.com", user=self.user
        )

        response = self.client.post(
            self.verify_email_url,
            {
                "email": "verify@example.com",
                "code": code,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

        # Check user's email is verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        self.assertEqual(self.user.email, "verify@example.com")

    def test_verify_email_wrong_code_returns_400(self):
        """
        Test that wrong verification code fails.
        """
        response = self.client.post(
            self.verify_email_url,
            {
                "email": "test@example.com",
                "code": "000000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetAPITests(APITestCase):
    """
    Test suite for password reset endpoints.
    Public endpoints (no authentication required).
    """

    def setUp(self):
        """Create a user and set up URLs."""
        self.request_url = reverse("accounts-v1:password-reset-request")
        self.confirm_url = reverse("accounts-v1:password-reset-confirm")

        self.phone_number = "09123456789"
        self.user = User.objects.create_user(
            phone_number=self.phone_number,
            password="oldpassword123",
            is_phone_verified=True,
        )

    def test_password_reset_request_success(self):
        """
        Test requesting a password reset code.
        Should return 200 with verification_token.
        """
        response = self.client.post(
            self.request_url, {"phone_number": self.phone_number}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("verification_token", response.data)

    def test_password_reset_request_unregistered_phone_returns_400(self):
        """
        Test requesting reset for unregistered number fails.
        """
        response = self.client.post(
            self.request_url, {"phone_number": "09999999999"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_full_flow(self):
        """
        Test the complete password reset flow.
        Request → Verify → New Password → Login with new password
        """
        import pyotp

        # Step 1: Request reset
        response = self.client.post(
            self.request_url, {"phone_number": self.phone_number}, format="json"
        )
        token = response.data["verification_token"]

        # Get the OTP code
        verification = PhoneVerification.objects.filter(
            phone_number=self.phone_number, verified=False
        ).latest("created_at")
        totp = pyotp.TOTP(verification.secret, interval=120)
        code = totp.now()

        # Step 2: Confirm with new password
        new_password = "newsecurepass456"
        response = self.client.post(
            self.confirm_url,
            {
                "verification_token": token,
                "otp_code": code,
                "new_password": new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

        # Step 3: Verify new password works
        login_response = self.client.post(
            reverse("accounts-v1:login"),
            {
                "phone_number": self.phone_number,
                "password": new_password,
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_wrong_code_returns_400(self):
        """
        Test reset confirmation with wrong code fails.
        """
        response = self.client.post(
            self.request_url, {"phone_number": self.phone_number}, format="json"
        )
        token = response.data["verification_token"]

        response = self.client.post(
            self.confirm_url,
            {
                "verification_token": token,
                "otp_code": "000000",
                "new_password": "newpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RateLimitingTests(APITestCase):
    """
    Test suite for OTP rate limiting.

    Ensures that users cannot request OTP codes more than once
    within the cooldown period (2 minutes).
    """

    def setUp(self):
        """Set up test data."""
        self.send_otp_url = reverse("accounts-v1:send-otp")
        self.valid_phone = "09123456789"

    def test_send_otp_rate_limiting_returns_429(self):
        """
        Test that second OTP request within 2 minutes is rejected.
        """
        # First request should succeed
        response1 = self.client.post(
            self.send_otp_url, {"phone_number": self.valid_phone}, format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Second request immediately after should fail with 429
        response2 = self.client.post(
            self.send_otp_url, {"phone_number": self.valid_phone}, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("detail", response2.data)
        self.assertIn("seconds", response2.data["detail"])

    def test_login_invalid_phone_format_returns_400(self):
        """
        Test that login with invalid phone format is rejected.
        """
        login_url = reverse("accounts-v1:login")

        invalid_phones = [
            "0912345678",  # 10 digits
            "091234567890",  # 12 digits
            "08123456789",  # doesn't start with 09
        ]

        for phone in invalid_phones:
            response = self.client.post(
                login_url,
                {"phone_number": phone, "password": "testpass123"},
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Expected 400 for phone: {phone}",
            )
