"""
Django admin configuration for the accounts app.

Registers the custom User model and related verification models
so they can be managed through the Django admin panel.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, PhoneVerification, EmailVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for the custom User model.

    Displays all relevant user fields including phone verification
    and email verification status. Allows filtering and searching
    by phone number and email.
    """
    # Fields to display in the user list
    list_display = (
        'phone_number',
        'email',
        'email_verified',
        'full_name',
        'is_active',
        'is_staff',
        'is_phone_verified',
        'date_joined',
    )

    # Filters available in the sidebar
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_phone_verified',
        'email_verified',
    )

    # Searchable fields
    search_fields = (
        'phone_number',
        'email',
        'full_name',
    )

    # Default ordering
    ordering = ('-date_joined',)

    # Fields shown in the user detail/edit form
    fieldsets = (
        (_('Login Information'), {
            'fields': ('phone_number', 'password')
        }),
        (_('Personal Information'), {
            'fields': ('full_name', 'email', 'email_verified')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_phone_verified',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Fields shown when adding a new user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'email',
                'full_name',
                'password1',
                'password2',
                'is_active',
                'is_staff',
            ),
        }),
    )


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    """
    Admin interface for the PhoneVerification model.

    Allows viewing and managing TOTP verification records.
    """
    list_display = ('phone_number', 'verified', 'created_at')
    list_filter = ('verified',)
    search_fields = ('phone_number',)
    ordering = ('-created_at',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """
    Admin interface for the EmailVerification model.

    Allows viewing and managing email verification records.
    """
    list_display = ('email', 'user', 'is_used', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('email', 'user__phone_number')
    ordering = ('-created_at',)
