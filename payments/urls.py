from django.urls import path
from . import views

urlpatterns = [
    path('checkout/webhook', views.StripeWebhookView.as_view(), name='checkout_webhook'),
    path('subscription/packages/', views.SubscriptionPackagesView.as_view(), name='subscription_packages'),
    path('create/subscription/', views.CreateSubscriptionView.as_view(), name="create_subscription"),
    path('cancel/subscription/', views.CancelSubscription.as_view(), name="cancel_subscription"),
    path('check/active-subscription/', views.CheckActiveSubscription.as_view(), name="check_active_subscription"),
    path('subscription/details/', views.GetSubscriptionDetails.as_view(), name="get_subscription_details"),
    path('check/discount-available/', views.GetDiscountPercentage.as_view(), name='get_discount_percentage'),
    path('test/subscription-access/', views.TestSubscriptionAccess.as_view(), name="test_subscription_access"),
    path('subscription/update-payment-method/', views.UpdatePaymentMethod.as_view(), name="update_payment_method")
]