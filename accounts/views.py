from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm , StaffCreateForm
from .models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to SupportFlow AI, {user.first_name}!')
        return redirect('dashboard:home')
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        return redirect(request.GET.get('next', 'dashboard:home'))
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def create_staff(request):

    if not request.user.is_admin:
        return redirect('dashboard:home')

    form = StaffCreateForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Staff account created successfully."
            )

            return redirect('dashboard:users')

    return render(
        request,
        'accounts/create_staff.html',
        {'form': form}
    )
