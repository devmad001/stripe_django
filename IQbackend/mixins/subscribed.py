from django.http import JsonResponse
from authentication.models import UserRole
from django.contrib.auth.mixins import AccessMixin
from authentication.users import UserRoleCommercial

class SubscriptionRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            user_role = UserRole.objects.filter(user=request.user, role=UserRoleCommercial.TYPE).first()
            if user_role.user.username.endswith('@iqland.ai'):
                return super().dispatch(request, *args, **kwargs)
            else:
                customer = user_role.customer.first()
                if not customer:
                    return JsonResponse({
                        'error': 'Not subscribed',
                        'message': 'You don\'t have an active subscription. You can continue using our platform after purchasing a subscription.'
                    }, status=400)
                current_subscription = customer.subscriptions.order_by('-created_at').first()

                if current_subscription and current_subscription.status in ['trialing', 'active']:
                    return super().dispatch(request, *args, **kwargs)
                else:
                    return JsonResponse({
                        'error': 'Not subscribed',
                        'message': 'You don\'t have an active subscription. You can continue using our platform after purchasing a subscription.'
                    }, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Not subscribed', 'message': str(e)}, status=400)