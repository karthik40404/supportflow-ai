from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Ticket, Comment
from .forms import TicketForm, TicketUpdateForm, CommentForm
from ai_engine.gemini import analyze_ticket

@login_required
def create_ticket(request):
    form = TicketForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.created_by = request.user
        ticket.save()
        # Run AI analysis
        try:
            ai_data = analyze_ticket(ticket.title, ticket.description)
            for key, val in ai_data.items():
                setattr(ticket, key, val)
            ticket.ai_processed = True
            ticket.save()
            messages.success(request, '🤖 Ticket created and analyzed by AI successfully!')
        except Exception as e:
            messages.warning(request, f'Ticket created. AI analysis pending: {e}')
        return redirect('tickets:detail', pk=ticket.pk)
    return render(request, 'tickets/create.html', {'form': form})

@login_required
def ticket_list(request):
    user = request.user
    if user.is_customer:
        tickets = Ticket.objects.filter(created_by=user)
    elif user.is_employee:
        tickets = Ticket.objects.filter(assigned_to=user)
    else:
        tickets = Ticket.objects.all()
    
    # Filters
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    search = request.GET.get('q')
    
    if status: tickets = tickets.filter(status=status)
    if priority: tickets = tickets.filter(priority=priority)
    if category: tickets = tickets.filter(category=category)
    if search: tickets = tickets.filter(title__icontains=search) | tickets.filter(description__icontains=search)
    
    return render(request, 'tickets/list.html', {
        'tickets': tickets,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'category_choices': Ticket.CATEGORY_CHOICES,
    })

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    
    # Access control
    if user.is_customer and ticket.created_by != user:
        messages.error(request, 'Access denied.')
        return redirect('tickets:list')
    
    comment_form = CommentForm(request.POST or None)
    update_form = TicketUpdateForm(instance=ticket) if not user.is_customer else None
    
    if request.method == 'POST':
        if 'comment_submit' in request.POST and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.user = user
            if user.is_customer:
                comment.is_internal = False
            comment.save()
            messages.success(request, 'Comment added.')
            return redirect('tickets:detail', pk=pk)
        
        if 'update_submit' in request.POST and update_form:
            update_form = TicketUpdateForm(request.POST, instance=ticket)
            if update_form.is_valid():
                t = update_form.save(commit=False)
                if t.status == 'resolved' and not ticket.resolved_at:
                    t.resolved_at = timezone.now()
                t.save()
                messages.success(request, 'Ticket updated.')
                return redirect('tickets:detail', pk=pk)
    
    comments = ticket.comments.all()
    if user.is_customer:
        comments = comments.filter(is_internal=False)
    
    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'update_form': update_form,
    })

@login_required
def reanalyze_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.is_customer:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        ai_data = analyze_ticket(ticket.title, ticket.description)
        for key, val in ai_data.items():
            setattr(ticket, key, val)
        ticket.ai_processed = True
        ticket.save()
        messages.success(request, '🤖 AI re-analysis complete!')
    except Exception as e:
        messages.error(request, f'AI analysis failed: {e}')
    return redirect('tickets:detail', pk=pk)
