from django.db import models
from IQbackend.mixins import base
from authentication.models import UserRole

class Customer(base.UUIDCreatedUpdatedMixin, models.Model):
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name="customer", help_text="")
    stripe_customer_id = models.CharField(max_length=255, help_text="Customer id returned from stripe after it saves subscription details")

class Subscription(base.UUIDCreatedUpdatedMixin, models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=255, help_text="Subscription id returned after subscription created event from stripe")
    status = models.CharField(max_length=255, blank=True, null=True, help_text="Status of subscription like active, renewed etc")
    started_at = models.DateTimeField(blank=True, null=True, help_text="Date when subscription started")
    ended_at = models.DateTimeField(blank=True, null=True, help_text="Date when subscription ended")
    canceled_at = models.DateTimeField(blank=True, null=True, help_text="Date when subscription is cancelled")
    expire_at_period_end = models.BooleanField(default=False, help_text="It indicates that subscription will expire at the end of the billing period after cancellation")
    expire_at = models.DateTimeField(blank=True, null=True, help_text="It indicates at what date subscription will expire")
    interval = models.CharField(max_length=255, default='month', help_text='Recurring interval of subscription like month or year')
    first_discount_taken = models.BooleanField(default=False, help_text='Keep track if the first discount has already been applied or not')

    def __str__(self):
        return f"Subscription - {self.customer.id} - {self.stripe_subscription_id}"