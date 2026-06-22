from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'employee', 'assigned_by', 'deadline', 'created_at']
    list_filter = ['employee']
