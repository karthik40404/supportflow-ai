from django.db import models
from accounts.models import User
from tickets.models import Ticket

class Assignment(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='assignment')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_given')
    deadline = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.ticket.id} → {self.employee.display_name}"
