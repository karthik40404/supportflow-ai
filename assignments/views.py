from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from tickets.models import Ticket
from accounts.models import User
from .models import Assignment
from .forms import AssignmentForm

def team_lead_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and (request.user.is_team_lead or request.user.is_admin)):
            messages.error(request, 'Team Lead access required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@team_lead_required
def assign_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    existing = Assignment.objects.filter(ticket=ticket).first()
    form = AssignmentForm(request.POST or None, instance=existing)
    
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.ticket = ticket
        assignment.assigned_by = request.user
        assignment.save()
        ticket.assigned_to = assignment.employee
        ticket.deadline = assignment.deadline
        if ticket.status == 'open':
            ticket.status = 'in_progress'
        ticket.save()
        messages.success(request, f'Ticket assigned to {assignment.employee.display_name}!')
        return redirect('tickets:detail', pk=ticket_id)
    
    # Employee workload for selection helper
    employees = User.objects.filter(role='employee', is_active=True).annotate(
        active_tasks=Count('tickets_assigned', filter=Q(tickets_assigned__status__in=['open','in_progress']))
    )
    return render(request, 'assignments/assign.html', {'ticket': ticket, 'form': form, 'employees': employees})

@login_required
@team_lead_required
def workload_view(request):
    employees = User.objects.filter(role='employee', is_active=True).annotate(
        total=Count('tickets_assigned'),
        open_tasks=Count('tickets_assigned', filter=Q(tickets_assigned__status='open')),
        in_progress=Count('tickets_assigned', filter=Q(tickets_assigned__status='in_progress')),
        resolved=Count('tickets_assigned', filter=Q(tickets_assigned__status='resolved')),
    )
    return render(request, 'assignments/workload.html', {'employees': employees})
