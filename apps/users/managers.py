from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, first_name, username, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not first_name:
            raise ValueError("The given fist name must be set")
    
        user = self.model(username=username, first_name=first_name, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, first_name, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(first_name, username, password, **extra_fields)

    def create_superuser(self, first_name, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(first_name, username, password, **extra_fields)
