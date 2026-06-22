from django.contrib import admin
from .models import Ticket, Comment

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_by', 'status', 'priority', 'category', 'sentiment', 'ai_processed', 'created_at']
    list_filter = ['status', 'priority', 'category', 'sentiment', 'escalation_required']
    search_fields = ['title', 'description']
    readonly_fields = ['ai_summary', 'ai_solution', 'ai_processed']

admin.site.register(Comment)
