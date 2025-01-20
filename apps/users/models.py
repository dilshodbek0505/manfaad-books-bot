from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.users.managers import CustomUserManager


class LanguageType(models.TextChoices):
    UZ = 'uz', 'uz'
    RU = 'ru', 'ru'
    EN = 'en', 'en'


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128, verbose_name=_("First name"))
    last_name = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("Last name"))
    username = models.CharField(max_length=128, unique=True, blank=True, null=True, verbose_name=_("Username"))
    phone = models.CharField(max_length=16, blank=True, null=True, verbose_name=_("Phone number"))
    language = models.CharField(max_length=128, choices=LanguageType.choices, default='en', verbose_name=_("User language"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Is active ?"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Is staff ?"))
    is_superuser = models.BooleanField(default=False, verbose_name=_("Is superuser ?"))
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"    
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
