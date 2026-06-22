from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from tickets.models import Ticket
from accounts.models import User

@login_required
def home(request):
    user = request.user
    ctx = {}
    
    if user.is_customer:
        tickets = Ticket.objects.filter(created_by=user)
        ctx = {
            'total': tickets.count(),
            'open': tickets.filter(status='open').count(),
            'in_progress': tickets.filter(status='in_progress').count(),
            'resolved': tickets.filter(status='resolved').count(),
            'recent_tickets': tickets[:5],
        }
        return render(request, 'dashboard/customer.html', ctx)
    
    elif user.is_employee:
        tickets = Ticket.objects.filter(assigned_to=user)
        today = timezone.now().date()
        ctx = {
            'total': tickets.count(),
            'open': tickets.filter(status='open').count(),
            'in_progress': tickets.filter(status='in_progress').count(),
            'completed': tickets.filter(status='resolved').count(),
            'due_today': tickets.filter(deadline__date=today, status__in=['open','in_progress']).count(),
            'my_tickets': tickets.exclude(status__in=['resolved','closed'])[:8],
        }
        return render(request, 'dashboard/employee.html', ctx)
    
    elif user.is_team_lead or user.is_admin:
        all_tickets = Ticket.objects.all()
        today = timezone.now().date()
        
        # Priority distribution for chart
        priority_data = {
            'low': all_tickets.filter(priority='low').count(),
            'medium': all_tickets.filter(priority='medium').count(),
            'high': all_tickets.filter(priority='high').count(),
            'critical': all_tickets.filter(priority='critical').count(),
        }
        
        # Status distribution
        status_data = {
            'open': all_tickets.filter(status='open').count(),
            'in_progress': all_tickets.filter(status='in_progress').count(),
            'pending': all_tickets.filter(status='pending').count(),
            'resolved': all_tickets.filter(status='resolved').count(),
        }
        
        # Category distribution
        category_counts = list(all_tickets.values('category').annotate(count=Count('id')).order_by('-count')[:6])
        
        # Employee workload
        employees = User.objects.filter(role='employee').annotate(
            task_count=Count('tickets_assigned', filter=Q(tickets_assigned__status__in=['open','in_progress']))
        )[:5]
        
        ctx = {
            'total': all_tickets.count(),
            'open': all_tickets.filter(status='open').count(),
            'high_priority': all_tickets.filter(priority__in=['high','critical']).count(),
            'assigned_today': all_tickets.filter(assignment__created_at__date=today).count(),
            'resolved': all_tickets.filter(status='resolved').count(),
            'escalation': all_tickets.filter(escalation_required=True, status__in=['open','in_progress']).count(),
            'unassigned': all_tickets.filter(assigned_to__isnull=True, status='open').count(),
            'recent_tickets': all_tickets[:10],
            'priority_data': priority_data,
            'status_data': status_data,
            'category_counts': category_counts,
            'employees': employees,
        }
        return render(request, 'dashboard/teamlead.html', ctx)
    
    return redirect('accounts:login')

@login_required
def admin_users(request):
    if not (request.user.is_admin or request.user.is_team_lead):
        return redirect('dashboard:home')
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'users': users})
