from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required.")
        if not email:
            raise ValueError("Email is required.")

        user = self.model(
            username=username, email=self.normalize_email(email), **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_with_profile(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password, **extra_fields)
        try:
            Profile.objects.create(
                user=user,
            )
        except Exception as e:
            user.delete()
            print(f"Error creating profile for user {username}: {e}")
            raise e
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        try:
            Profile.objects.create(
                user=user,
            )
        except Exception as e:
            print(f"Error creating profile for superuser {username}: {e}")
        return user


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_user_email")
        ]

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True
    )
    lastname = models.CharField(_("last name"), max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username if self.user else 'No User'}"
