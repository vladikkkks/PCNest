from django.core.exceptions import PermissionDenied
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_site_admin():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
