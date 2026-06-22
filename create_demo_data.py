import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supportflow.settings')

import django
django.setup()

from accounts.models import User
from tickets.models import Ticket, Comment
from assignments.models import Assignment
from django.utils import timezone
from datetime import timedelta

# Create users
def get_or_create(username, first, last, email, role, dept='', password='pass123'):
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, password=password,
            first_name=first, last_name=last, email=email, role=role, department=dept)
        print(f"Created {role}: {username}")
        return u
    return User.objects.get(username=username)

admin = get_or_create('admin', 'Admin', 'User', 'admin@supportflow.ai', 'admin', password='admin123')
tl = get_or_create('teamlead', 'Sarah', 'Johnson', 'sarah@supportflow.ai', 'team_lead', 'Operations')
emp1 = get_or_create('employee1', 'Rahul', 'Kumar', 'rahul@supportflow.ai', 'employee', 'Backend')
emp2 = get_or_create('employee2', 'Priya', 'Singh', 'priya@supportflow.ai', 'employee', 'Frontend')
emp3 = get_or_create('employee3', 'Arun', 'Nair', 'arun@supportflow.ai', 'employee', 'DevOps')
c1 = get_or_create('customer1', 'Alex', 'Brown', 'alex@example.com', 'customer')
c2 = get_or_create('customer2', 'Maria', 'Garcia', 'maria@example.com', 'customer')
c3 = get_or_create('customer3', 'James', 'Wilson', 'james@example.com', 'customer')

# Create sample tickets
sample_tickets = [
    {
        'title': 'Login fails after password reset',
        'description': 'I reset my password yesterday but still cannot log in. The page shows "Invalid credentials" even with the new password. I have tried on Chrome and Firefox. This is very frustrating and I cannot access my account.',
        'created_by': c1, 'category': 'authentication', 'priority': 'high',
        'status': 'in_progress', 'sentiment': 'negative', 'escalation_required': False,
        'ai_summary': 'Customer unable to login after password reset, experiencing invalid credentials error across multiple browsers.',
        'ai_solution': 'Check authentication token validation and session cache. Verify password hash update was applied correctly in the database.',
        'suggested_department': 'backend', 'ai_processed': True,
    },
    {
        'title': 'Payment charged twice for last month',
        'description': 'Your service is absolutely terrible! I was charged twice on March 15th. I can see two transactions of ₹999 each on my bank statement. This is unacceptable. I want an immediate refund!',
        'created_by': c2, 'category': 'billing', 'priority': 'critical',
        'status': 'open', 'sentiment': 'very_negative', 'escalation_required': True,
        'ai_summary': 'Customer reports duplicate billing charge of ₹999 on March 15th and demands immediate refund.',
        'ai_solution': 'Verify payment gateway logs for duplicate transactions. Issue refund for duplicate charge and send confirmation email.',
        'suggested_department': 'billing', 'ai_processed': True,
    },
    {
        'title': 'Dashboard loading very slowly',
        'description': 'The main dashboard takes about 30-40 seconds to load. This started happening after your last update on March 10th. My internet connection is fine (100 Mbps). Other pages load normally.',
        'created_by': c3, 'category': 'performance', 'priority': 'medium',
        'status': 'open', 'sentiment': 'neutral', 'escalation_required': False,
        'ai_summary': 'Post-update dashboard performance degradation, 30-40 second load times since March 10th update.',
        'ai_solution': 'Profile dashboard queries for N+1 issues. Check CDN and static asset delivery. Review recent deployment changes.',
        'suggested_department': 'frontend', 'ai_processed': True,
    },
    {
        'title': 'Request: Dark mode for mobile app',
        'description': 'I would love to have a dark mode option in the mobile app. It would make it much easier to use at night. I think many users would appreciate this feature. Love the product overall!',
        'created_by': c1, 'category': 'feature_request', 'priority': 'low',
        'status': 'open', 'sentiment': 'positive', 'escalation_required': False,
        'ai_summary': 'Customer requesting dark mode feature for mobile application, positive feedback on product overall.',
        'ai_solution': 'Log as a feature request in the backlog. Acknowledge with estimated timeline and thank customer for positive feedback.',
        'suggested_department': 'frontend', 'ai_processed': True,
    },
    {
        'title': 'API returning 500 error on bulk export',
        'description': 'The API endpoint /api/v2/export/bulk is returning 500 Internal Server Error when trying to export more than 1000 records. Works fine for smaller batches. Error code: ERR_BULK_LIMIT_EXCEEDED',
        'created_by': c2, 'category': 'bug_report', 'priority': 'high',
        'status': 'resolved', 'sentiment': 'neutral', 'escalation_required': False,
        'ai_summary': 'API bulk export endpoint fails with 500 error for datasets over 1000 records.',
        'ai_solution': 'Implement pagination for bulk export, increase memory limit for export workers, add proper error handling.',
        'suggested_department': 'backend', 'ai_processed': True,
    },
    {
        'title': 'Cannot upload profile picture',
        'description': 'Every time I try to upload a profile picture it shows "Upload failed". I have tried PNG and JPG files of different sizes. The largest was 2MB.',
        'created_by': c3, 'category': 'technical', 'priority': 'medium',
        'status': 'in_progress', 'sentiment': 'neutral', 'escalation_required': False,
        'ai_summary': 'Customer unable to upload profile pictures in any format, upload fails consistently.',
        'ai_solution': 'Check file upload size limits and MIME type validation in the upload handler.',
        'suggested_department': 'backend', 'ai_processed': True,
    },
]

for t_data in sample_tickets:
    if not Ticket.objects.filter(title=t_data['title']).exists():
        ticket = Ticket.objects.create(**t_data)
        print(f"Created ticket: #{ticket.id} - {ticket.title[:40]}")

# Create some assignments
t1 = Ticket.objects.filter(status='in_progress').first()
if t1 and not Assignment.objects.filter(ticket=t1).exists():
    Assignment.objects.create(ticket=t1, employee=emp1, assigned_by=tl,
        deadline=timezone.now() + timedelta(days=2), notes="High priority - check auth logs first")
    t1.assigned_to = emp1
    t1.save()

# Add some comments
t2 = Ticket.objects.filter(category='billing').first()
if t2 and not t2.comments.exists():
    Comment.objects.create(ticket=t2, user=tl, message="Escalating to billing team. Checking payment gateway logs.", is_internal=True)
    Comment.objects.create(ticket=t2, user=t2.created_by, message="Please resolve this ASAP! I need my money back.")

print("\n✅ Demo data created successfully!")
print("\nLogin credentials:")
print("  Admin:     admin / admin123")
print("  Team Lead: teamlead / pass123")
print("  Employee:  employee1 / pass123")
print("  Customer:  customer1 / pass123")
