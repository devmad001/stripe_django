# from flask import Flask
# from flask_mail import Mail, Message
from django.http import JsonResponse

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

def dict_to_object(dictionary):
    return DictToObject(dictionary)

def handle_api_error(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except KeyError:
            return JsonResponse({'error': 'Session data not found'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return wrapper

# def send_verification_email(recipient_email, otp_code):
#     app = Flask(__name__)
#     app.config['MAIL_SERVER'] = 'smtp.hostinger.com'
#     app.config['MAIL_PORT'] = 587
#     app.config['MAIL_USE_TLS'] = True
#     app.config['MAIL_USERNAME'] = 'admin@prepowl.info'
#     app.config['MAIL_PASSWORD'] = 'Admin@2024'
#     mail = Mail(app)

#     subject = 'Verify Your Email - IQLand'
#     body = f'Your verification code is: {otp_code}'

#     with app.app_context():
#         msg = Message(subject, sender='admin@prepowl.info', recipients=[recipient_email])
#         msg.body = body

#         try:
#             mail.send(msg)
#             print("Email sent successfully!")
#             return True
#         except Exception as e:
#             print(f"Failed to send email. Error: {str(e)}")
#             return False