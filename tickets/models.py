from django.db import models
from accounts.models import User

class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('authentication', 'Authentication'),
        ('billing', 'Billing'),
        ('technical', 'Technical Issue'),
        ('feature_request', 'Feature Request'),
        ('bug_report', 'Bug Report'),
        ('account', 'Account Management'),
        ('performance', 'Performance'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('very_negative', 'Very Negative'),
    ]
    DEPARTMENT_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('devops', 'DevOps'),
        ('billing', 'Billing'),
        ('security', 'Security'),
        ('general', 'General Support'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, blank=True)
    ai_summary = models.TextField(blank=True)
    ai_solution = models.TextField(blank=True)
    suggested_department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    escalation_required = models.BooleanField(default=False)
    ai_processed = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_created')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_assigned')
    deadline = models.DateTimeField(null=True, blank=True)

    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"

    @property
    def priority_badge(self):
        badges = {'low': 'success', 'medium': 'warning', 'high': 'danger', 'critical': 'dark'}
        return badges.get(self.priority, 'secondary')

    @property
    def status_badge(self):
        badges = {'open': 'primary', 'in_progress': 'info', 'pending': 'warning', 'resolved': 'success', 'closed': 'secondary'}
        return badges.get(self.status, 'secondary')

    @property
    def sentiment_badge(self):
        badges = {'positive': 'success', 'neutral': 'secondary', 'negative': 'warning', 'very_negative': 'danger'}
        return badges.get(self.sentiment, 'secondary')


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on #{self.ticket.id}"
