import stripe
import datetime
from payments.models import Subscription, Customer
from django.utils import timezone
from IQbackend.connectors import sendgrid_connector
from django.template.loader import render_to_string

def convert_timestamp_to_aware_datetime(timestamp, tz=datetime.timezone.utc):
    naive_datetime = datetime.datetime.fromtimestamp(timestamp)
    aware_datetime = timezone.make_aware(naive_datetime, tz)
    return aware_datetime

def handle_subscription_trial_will_end(event):
    stripe_subscription = stripe.Subscription.retrieve(event['data']['object']['id'])
    print(stripe_subscription)
    subscribed_customer = Customer.objects.get(stripe_customer_id=stripe_subscription['customer'])
    sendgrid = sendgrid_connector.SendgridConnector()
    html_content = render_to_string(
                'trial_end.html', 
                {'name': subscribed_customer.user_role.user.first_name, 'trial_end_date': convert_timestamp_to_aware_datetime(stripe_subscription.trial_end)}
            )
    sendgrid.send_trial_end_email(subscribed_customer.user_role.user.username, html_content)

def handle_subscription_created(event):
    stripe_subscription = stripe.Subscription.retrieve(event['data']['object']['id'])
    print(stripe_subscription)
    customer = Customer.objects.get(stripe_customer_id=stripe_subscription.customer)
    interval = stripe_subscription['plan']['interval']

    subscription = Subscription.objects.create(
        customer=customer,
        stripe_subscription_id=stripe_subscription.id,
        status=stripe_subscription.status,
        started_at=convert_timestamp_to_aware_datetime(stripe_subscription.created),
        interval=interval,
        first_discount_taken=True if stripe_subscription.get('discount') else False
    )
    subscription.save()
    return subscription

def handle_invoice_payment_succeeded(event):
    invoice = event['data']['object']
    print(invoice)
    sendgrid = sendgrid_connector.SendgridConnector()
    html_content = render_to_string(
                'payment_succeeded.html', 
                {'amount': f"{invoice['total']/ 100:.2f} usd" , 'payment_date': convert_timestamp_to_aware_datetime(invoice['created']), 'invoice_pdf': invoice['invoice_pdf']}
            )
    if invoice['total']:
        sendgrid.send_purchase_email(invoice['customer_email'], html_content)

def handle_subscription_updated(event):
    stripe_subscription = stripe.Subscription.retrieve(event['data']['object']['id'])

    subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription.id)

    subscription.status = stripe_subscription.status

    if stripe_subscription.canceled_at:
        subscription.canceled_at = convert_timestamp_to_aware_datetime(stripe_subscription.canceled_at)
        subscription.expire_at_period_end = stripe_subscription.cancel_at_period_end
        subscription.expire_at = convert_timestamp_to_aware_datetime(
            stripe_subscription.cancel_at) if stripe_subscription.cancel_at else None

    if stripe_subscription.ended_at:
        subscription.ended_at = convert_timestamp_to_aware_datetime(stripe_subscription.ended_at)

    if stripe_subscription.current_period_start:
        current_period_start = convert_timestamp_to_aware_datetime(stripe_subscription.current_period_start)
        if subscription.started_at < current_period_start:
            subscription.started_at = current_period_start

    subscription.save()

    return subscription