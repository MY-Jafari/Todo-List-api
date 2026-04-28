import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

@pytest.mark.django_db
class TestCustomUser:
    
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass') is True

    def test_create_user_without_username_raises_error(self):
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass'
            )
        assert str(excinfo.value) == "Username is required."

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(
                username='testuser',
                email='',
                password='testpass'
            )
        assert str(excinfo.value) == "Email is required."
    
    def test_create_user_with_profile(self):
        user = User.objects.create_user_with_profile(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        assert user.profile is not None
        assert user.profile.user == user

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass'
        )
        assert superuser.is_superuser is True
        assert superuser.is_staff is True
        assert superuser.profile is not None

    def test_create_user_without_profile_on_error(self):
        user = User.objects.create_user_with_profile(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        assert user.profile is not None
        
