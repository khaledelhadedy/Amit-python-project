
from rest_framework import serializers
from .models import CustomUser
import re
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg
from project.utils import generate_tokens


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'password', 'confirm_password', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'confirm_password': {'write_only': True, 'required': False},
        }

    def validate(self, data):
      
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password:
            password_regex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>])[A-Za-z\d!@#$%^&*(),.?\":{}|<>]{8,20}$"
            if not re.match(password_regex, password):
                raise serializers.ValidationError(
                    _('Password must be 8-20 characters long, contain at least one uppercase letter, one number, and one special character.')
                )
            password_validation.validate_password(password)

            if confirm_password and password != confirm_password:
                raise serializers.ValidationError(_('Passwords do not match'))

        return data


    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Email already exists'))
        return value


    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()
        return instance

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
   
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError(_('Invalid credentials'))
        
        if not user.is_active:
            raise serializers.ValidationError(_('Inactive user'))
        
        data['user'] = user
        return data
    


    






        
