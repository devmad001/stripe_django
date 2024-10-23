import random
import string
from django.core.cache import cache
from authentication.models import SessionData
from django.template.loader import render_to_string
from IQbackend.connectors import sendgrid_connector


def store_session_data(request, property, zoning, user_choices, query_property, kpi, architectural_plans, selected_architectural_plan, comparables):
    session_id = request.session.session_key
    user = request.user

    session_data = SessionData.objects.create(
        user=user,
        session_id=session_id,
        property=property,
        zoning=zoning,
        user_choices=user_choices,
        query_property=query_property,
        kpi=kpi,
        architectural_plans=architectural_plans,
        selected_architectural_plan=selected_architectural_plan
    )

    request.session['session_data_id'] = str(session_data.id)


def get_session_data(request, field_name):
    session_data_id = request.session.get('session_data_id')
    if not session_data_id:
        return {'error': 'No session data found.', 'status': False}

    try:
        session_data = SessionData.objects.get(id=session_data_id)
        field_value = getattr(session_data, field_name, None)
        return {field_name: field_value, 'status': True}
    except SessionData.DoesNotExist:
        return {'error': 'No session data found.', 'status': False}


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_otp(user):
    otp = generate_otp()
    sendgrid = sendgrid_connector.SendgridConnector()
    cache.set(f"otp_{user.pk}", otp, timeout=600)
    html_content = render_to_string(
        'login_otp.html', 
        {'name': user.first_name, 'otp': otp}
    )
    sendgrid.send_login_otp(user.username, html_content)