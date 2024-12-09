from django.contrib import admin
from .models import CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'is_staff', 'is_active', 'created_at']
    search_fields = ['full_name', 'email']


admin.site.register(CustomUser, CustomUserAdmin)