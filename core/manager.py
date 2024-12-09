
from django.contrib.auth.models import BaseUserManager



def input_check(*value):
    if not value:
        raise ValueError(f'The {value} field must be set')
    
class CustomUserManager(BaseUserManager):
    def create_user(self, full_name, email, password=None, confirm_password=None,**extra_fields):
        input_check(full_name, email)
        email = self.normalize_email(email)
        user = self.model(full_name=full_name, email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, email, password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(full_name=full_name, email=email, password=password, **extra_fields)