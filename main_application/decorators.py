from functools import wraps
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponseForbidden

def session_timeout_required(timeout=30):
    """
    Decorator function to enforce session timeout.
    :param timeout: Timeout duration in seconds (default is 30 seconds).
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Check if the user is logged in and has an active session
            if request.user.is_authenticated:
                last_activity_time = request.session.get('last_activity')
                current_time = timezone.now()

                # Check if the last activity time is available in the session
                if last_activity_time:
                    session_timeout_duration = timedelta(seconds=timeout)

                    # Check if the user has been inactive for more than the timeout duration
                    if current_time - last_activity_time > session_timeout_duration:
                        # Invalidate the session
                        request.session.flush()
                        return HttpResponseForbidden("Session expired due to inactivity")
                else:
                    # Update the last activity time in the session if it's not set
                    request.session['last_activity'] = current_time

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator
