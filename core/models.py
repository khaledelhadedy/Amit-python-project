from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(_("ID"), primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    confirm_password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name_plural = 'users'
        verbose_name = 'user'

    def __str__(self):
        return self.full_name
    
    
    



