from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "owner", "due_date", "created_date")
    list_filter = ("status", "created_date", "due_date")
    search_fields = ("title", "description", "owner__email")
    ordering = ("-created_date",)
