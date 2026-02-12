from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email','is_staff','is_active','is_verified')
    list_filter = ('is_staff','is_active','is_verified')
    ordering = ('email',)
    search_fields = ('email',)
    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2", "is_active", "is_staff")}),
    )
    ROLE_CHOICES = (
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("member", "Member"),
)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")

    


