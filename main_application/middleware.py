from django.utils import timezone
from django.http import JsonResponse

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                # Check if last activity was within the last 30 seconds
                if timezone.now() - last_activity > timezone.timedelta(seconds=30):
                    # If no activity within last 30 seconds, logout user
                    del request.session['last_activity']
                    del request.session['client_id']
                    del request.session['token']
                    request.session.modified = True  # Ensure changes are saved
                    return JsonResponse({'error': 'Inactive session. You have been logged out.'}, status=401)
            else:
                # Set last activity time if not set
                request.session['last_activity'] = timezone.now()
                request.session.modified = True  # Ensure changes are saved

        response = self.get_response(request)
        
        return response
