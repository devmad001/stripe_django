import json
import stripe
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from authentication.models import UserRole
from django.http.response import HttpResponse
from payments.models import Subscription, Customer
from authentication.users import UserRoleCommercial
from IQbackend.mixins.auth import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin
from payments.helpers import handle_subscription_trial_will_end, handle_subscription_created, handle_invoice_payment_succeeded, handle_subscription_updated, convert_timestamp_to_aware_datetime
        
class CreateSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            data = json.loads(request.body)
            price_id = data.get('price_id')

            user_role = UserRole.objects.filter(user=request.user, role=UserRoleCommercial.TYPE).first()
            customer = user_role.customer.first()
            can_get_trial = False
            if not customer:
                can_get_trial = True
                stripe_customer = stripe.Customer.create(email=request.user.username)
                customer = Customer.objects.create(user_role=user_role, stripe_customer_id=stripe_customer.id)
                customer.save()
            
            current_subscription = customer.subscriptions.order_by('-created_at').first()

            if current_subscription and current_subscription.status in ['trialing', 'active']:
                return JsonResponse({
                    'type': 'None',
                    'clientSecret': 'None',
                    'subscriptionId': 'None',
                    'has_active_subscription': True,
                    'message': 'You already have an active subscription',
                })
            
            customer_id = customer.stripe_customer_id

            price_detail = stripe.Price.retrieve(price_id)
            discount_id = settings.STRIPE_YEARLY_DISCOUNT_ID if price_detail.recurring.interval == "year" else None

            # Create a dictionary for subscription parameters
            subscription_params = {
                'customer': customer_id,
                'items': [{
                    'price': price_id,
                }],
                'payment_behavior': 'default_incomplete',
                'payment_settings': {'save_default_payment_method': 'on_subscription'},
                'expand': ['latest_invoice.payment_intent', 'pending_setup_intent']
            }

            if can_get_trial:
                subscription_params['trial_period_days'] = 7

            # Check if the customer has already taken a yearly discount
            if discount_id is not None:
                has_taken_yearly_discount = False
                
                # customer.subscriptions.filter(
                #     interval='year',
                #     first_discount_taken=True
                # ).exists()

                if has_taken_yearly_discount:
                    discount_id = None

            # Add discount if discount_id is not None
            if discount_id is not None:
                coupon = stripe.Coupon.retrieve(discount_id)
                if coupon.valid:
                    subscription_params['discounts'] = [{"coupon": discount_id}]

            # Create the subscription with the conditional parameters
            subscription = stripe.Subscription.create(**subscription_params)
            if subscription.pending_setup_intent is not None:
                return JsonResponse({'type':'setup', 'clientSecret':subscription.pending_setup_intent.client_secret, 'subscriptionId': subscription.id})
            else:
                return JsonResponse({'type':'payment', 'clientSecret':subscription.latest_invoice.payment_intent.client_secret, 'subscriptionId': subscription.id})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)

class CancelSubscription(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            subscription_id = data.get('subscription_id')
            if (subscription_id != 'iqland-internal-user'):
                stripe.Subscription.delete(subscription_id)
            return JsonResponse({'message': 'Subscription deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e), 'message': 'Error occurred while deleting subscription'}, status=400)

class UpdatePaymentMethod(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            payment_method_id = data.get('payment_method_id')
            user_role = UserRole.objects.filter(user=request.user, role=UserRoleCommercial.TYPE).first()
            customer = user_role.customer.first()
            customer_id = customer.stripe_customer_id
            # Attach the new payment method to the customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )

            # Update the customer's default invoice payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )

            subscription_id = None
            current_subscription = customer.subscriptions.order_by('-created_at').first()

            if current_subscription and current_subscription.status in ['trialing', 'active']:
                subscription_id = current_subscription.stripe_subscription_id

            # Update the subscription with the new payment method
            stripe.Subscription.modify(
                subscription_id,
                default_payment_method=payment_method_id,
            )

            return JsonResponse({'message': 'Payment method updated successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e), 'message': 'Error occurred while updating payment method'}, status=400)
class GetSubscriptionDetails(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            subscription_id = data.get('subscription_id')
            if (subscription_id == 'iqland-internal-user'):
                return JsonResponse({'subscription': {
                    'collection_method': 'charge_automatically', 
                    'currency': 'USD', 
                    'current_period_start': '', 
                    'current_period_end': '', 
                    'trial_start': '', 
                    'trial_end': '', 
                    'amount': '0.00', 
                    'discount_percentage': 0,
                    'status': 'active',
                    'plan_interval': 'Infinite',
                    'plan_name': 'Internal Use'
                    }})
            else:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe_subscription = stripe.Subscription.retrieve(subscription_id)
                total_amount = 0
                discount_percentage = 0
                for item in stripe_subscription.get('items'):
                    total_amount += item.price.unit_amount
                if stripe_subscription.get('discount'):
                    discount_percentage = stripe_subscription.get('discount')['coupon']['percent_off'] or 0
                return JsonResponse({'subscription': {
                    'collection_method': stripe_subscription.collection_method, 
                    'currency': stripe_subscription.currency, 
                    'current_period_start': convert_timestamp_to_aware_datetime(stripe_subscription.current_period_start) if stripe_subscription.current_period_start else '', 
                    'current_period_end': convert_timestamp_to_aware_datetime(stripe_subscription.current_period_end) if stripe_subscription.current_period_end else '', 
                    'trial_start': convert_timestamp_to_aware_datetime(stripe_subscription.trial_start) if stripe_subscription.trial_start else '', 
                    'trial_end': convert_timestamp_to_aware_datetime(stripe_subscription.trial_end) if stripe_subscription.trial_end else '', 
                    'amount': f'{total_amount / 100:.2f}', 
                    'discount_percentage': discount_percentage,
                    'status': stripe_subscription.status,
                    'plan_interval': stripe_subscription['plan']['interval'],
                    'plan_name': 'Residential'
                    }})

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)

class CheckActiveSubscription(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            user_role = UserRole.objects.filter(user=request.user, role=UserRoleCommercial.TYPE).first()
            if user_role.user.username.endswith('@iqland.ai'):
                return JsonResponse({
                    'has_active_subscription': True,
                    'message': 'You already have an active subscription',
                    'subscription_id': 'iqland-internal-user'
                })
            customer = user_role.customer.first()
            if not customer:
                return JsonResponse({
                    'has_active_subscription': False,
                    'message': 'You don\'t have an active subscription'
                })
            current_subscription = customer.subscriptions.order_by('-created_at').first()

            if current_subscription and current_subscription.status in ['trialing', 'active']:
                return JsonResponse({
                    'has_active_subscription': True,
                    'message': 'You already have an active subscription',
                    'subscription_id': current_subscription.stripe_subscription_id
                })
            else:
                return JsonResponse({
                    'has_active_subscription': False,
                    'message': 'You don\'t have an active subscription'
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        stripe.api_key = settings.STRIPE_SECRET_KEY
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        if event['type'] == 'customer.subscription.trial_will_end':
            handle_subscription_trial_will_end(event)
        elif event['type'] == 'customer.subscription.created':
            handle_subscription_created(event)
        elif event['type'] == 'invoice.payment_succeeded':
            handle_invoice_payment_succeeded(event)
        elif event['type'] in ['customer.subscription.updated', 'customer.subscription.deleted']:
            handle_subscription_updated(event)
            
        return HttpResponse(status=200)
    
class GetDiscountPercentage(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            data = json.loads(request.body)
            interval = data.get('interval')
            user_role = UserRole.objects.filter(user=request.user, role=UserRoleCommercial.TYPE).first()
            customer = user_role.customer.first()
            discount_id = settings.STRIPE_YEARLY_DISCOUNT_ID if interval == "year" else None
            if customer:
                if discount_id is not None:
                    has_taken_yearly_discount = False
                    
                    # customer.subscriptions.filter(
                    #     interval='year',
                    #     first_discount_taken=True
                    # ).exists()

                    if has_taken_yearly_discount:
                        discount_id = None
            else:
                discount_id = None
            if discount_id is not None:
                return JsonResponse({
                    'apply_discount': True,
                })
            else:
                return JsonResponse({
                    'apply_discount': False,
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class SubscriptionPackagesView(View):
    def get(self, request, *args, **kwargs):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            products = stripe.Product.list(active=True)
            data = []
            for product in products.data:
                if product.metadata.get('enterprise') == 'true':
                    continue
                prices = stripe.Price.list(product=product.id, active=True)
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'features': product.marketing_features,
                    'prices': [
                        {
                            'id': price.id,
                            'currency': price.currency,
                            'interval': price.recurring.interval,
                            'discount_percentage': "20%" if price.recurring.interval == "year" else "0%",
                            'unit_amount': price.unit_amount / 100 if price.unit_amount else None
                        } for price in prices.data if price.active
                    ],
                }
                data.append(product_data)
            return JsonResponse({'products': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
class TestSubscriptionAccess(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse({'message': 'You are subscribed that\'s why you are getting this message.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)