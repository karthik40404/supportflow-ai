from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('team_lead', 'Team Lead'),
        ('admin', 'Admin'),
    ]
    DEPARTMENT_CHOICES = [
    ('backend', 'Backend'),
    ('frontend', 'Frontend'),
    ('devops', 'DevOps'),
    ('qa', 'Quality Assurance'),
    ('support', 'Support'),
    ('operations', 'Operations'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_customer(self): return self.role == 'customer'
    @property
    def is_employee(self): return self.role == 'employee'
    @property
    def is_team_lead(self): return self.role == 'team_lead'
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    @property
    def display_name(self): return self.get_full_name() or self.username
