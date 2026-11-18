from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import RegistrationForm, LoginForm, UserProfileUpdateForm
from .decorators import admin_required, employee_required


def register_view(request):
    """
    Handles user account registration with validation and password hashing.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account for '{user.username}' created successfully! You may now sign in."
            )
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please check the form errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handles user login using username or email with password verification.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.display_name}!")

            if next_url:
                return redirect(next_url)
            if user.is_admin_role:
                return redirect('admin_dashboard')
            return redirect('employee_dashboard')
        else:
            messages.error(request, "Invalid credentials. Please verify your username/email and password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@login_required
def logout_view(request):
    """
    Logs out the current authenticated user and clears session data.
    """
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def dashboard_redirect_view(request):
    """
    Directs the authenticated user to their role-specific dashboard.
    """
    if request.user.is_admin_role:
        return redirect('admin_dashboard')
    return redirect('employee_dashboard')


@login_required
@admin_required
def admin_dashboard_view(request):
    """
    Role-Based Dashboard for Administrators.
    Protected so employees cannot access it.
    """
    total_staff = CustomUser.objects.filter(role=CustomUser.Role.EMPLOYEE).count()
    admins_count = CustomUser.objects.filter(role=CustomUser.Role.ADMIN).count()

    context = {
        'total_staff': total_staff,
        'admins_count': admins_count,
        'recent_users': CustomUser.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
@employee_required
def employee_dashboard_view(request):
    """
    Role-Based Dashboard for Employees / Staff.
    Protected so unauthorized users cannot access it.
    """
    context = {
        'employee': request.user,
    }
    return render(request, 'accounts/employee_dashboard.html', context)


@login_required
def profile_view(request):
    """
    Displays the logged-in user's profile.
    Ensures users can only view their own profile.
    """
    return render(request, 'accounts/profile.html', {'user_obj': request.user})


@login_required
def edit_profile_view(request):
    """
    Allows the logged-in user to update their personal details and profile photo.
    Users can only update their own profile.
    """
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Unable to update profile. Please correct the highlighted errors.")
    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})
