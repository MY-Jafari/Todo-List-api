"""
Notification utilities for sending OTP and verification codes.

Provides a unified interface for sending codes via SMS and Email.
Supports development mode (logging/returning codes) and production
mode (integration with real SMS/Email providers).
"""

from django.conf import settings

# from django.utils.translation import gettext_lazy as _


def send_phone_verification_code(phone_number, code):
    """
    Send a verification code to the specified phone number.

    In development (DEBUG=True): Prints the code to the console.
    In production: Integrates with an SMS provider (e.g., Kavenegar, Twilio).

    Args:
        phone_number (str): The recipient's phone number.
        code (str): The 6-digit TOTP code to send.

    Returns:
        dict: Response data containing the code in development mode.
        None: In production mode (code is sent via SMS).
    """
    if settings.DEBUG:
        # Development mode: Log and return the code for testing
        print(f"\n{'='*50}")
        print(f"[DEV] SMS to: {phone_number}")
        print(f"[DEV] Verification code: {code}")
        print("[DEV] Code expires in: 120 seconds")
        print(f"{'='*50}\n")
        return {"code": code, "phone_number": phone_number}
    else:
        # Production mode: Integrate with real SMS provider here
        # Example with Kavenegar:
        # from kavenegar import KavenegarAPI
        # api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        # api.sms_send({'receptor': phone_number, 'message': f'Your code: {code}'})
        pass


def send_email_verification_code(email, code):
    """
    Send a verification code to the specified email address.

    Uses django-mail-templated for HTML email templates.
    In development (DEBUG=True): Prints the code to the console.
    In production: Sends a real email using configured email backend.

    Args:
        email (str): The recipient's email address.
        code (str): The 6-digit verification code to send.

    Returns:
        dict: Response data containing the code in development mode.
        None: In production mode (email is sent).
    """
    if settings.DEBUG:
        # Development mode: Log and return the code for testing
        print(f"\n{'='*50}")
        print(f"[DEV] Email to: {email}")
        print(f"[DEV] Verification code: {code}")
        print("[DEV] Code expires in: 10 minutes")
        print(f"{'='*50}\n")
        return {"code": code, "email": email}
    else:
        # Production mode: Send real HTML email using django-mail-templated
        from mail_templated import send_mail

        send_mail(
            template_name="accounts/emails/verification_code.tpl",
            context={"code": code, "email": email},
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )


def send_password_reset_code(phone_number=None, email=None, code=None):
    """
    Send a password reset code via phone or email.

    Prioritizes phone if both are provided.

    Args:
        phone_number (str, optional): The recipient's phone number.
        email (str, optional): The recipient's email address.
        code (str): The reset code to send.

    Returns:
        dict or None: Response data in dev mode, None in production.
    """
    if phone_number:
        return send_phone_verification_code(phone_number, code)
    elif email:
        return send_email_verification_code(email, code)
    return None
