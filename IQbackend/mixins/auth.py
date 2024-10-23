from django.http import JsonResponse
from django.contrib.auth.mixins import AccessMixin


class LoginRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    'error': 'Unauthorized',
                    'message': 'User is not logged in. Please log in to access this resource.',
                    'status_code': 401
                }, 
                status=401
            )
        return super().dispatch(request, *args, **kwargs)