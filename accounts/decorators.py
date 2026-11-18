from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Decorator that checks whether the logged-in user has one of the allowed roles.
    If the user has an unauthorized role, they are redirected to their appropriate
    role dashboard and presented with a warning message.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('login')

            user_role = getattr(request.user, 'role', None)

            # Superusers always have admin access
            if request.user.is_superuser and 'ADMIN' in allowed_roles:
                return view_func(request, *args, **kwargs)

            if user_role not in allowed_roles:
                messages.error(
                    request,
                    f"Access Denied: You do not have permission to access the {', '.join(allowed_roles).title()} dashboard."
                )
                if user_role == 'ADMIN':
                    return redirect('admin_dashboard')
                return redirect('employee_dashboard')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)


def employee_required(view_func):
    return role_required(['EMPLOYEE'])(view_func)
