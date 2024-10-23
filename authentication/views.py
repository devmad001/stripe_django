import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views import View
from IQbackend.mixins.auth import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.cache import cache
from django.middleware.csrf import get_token

from authentication.helpers import generate_otp, send_otp
from authentication.models import User, UserRole
from users.models import ProfileSettings
from IQbackend.mixins.auth import LoginRequiredMixin
from IQbackend.connectors import sendgrid_connector
from IQbackend import settings
from authentication.testusers import testUsers, guestUser

@method_decorator(csrf_exempt, name='dispatch')
class ResendEmailVerificationOTPView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({'error': 'Invalid username.'}, status=400)
            sendgrid = sendgrid_connector.SendgridConnector()
            otp = generate_otp()
            cache.set(f"otp_{user.pk}", otp, timeout=600)
            html_content = render_to_string(
                'verification_otp.html', 
                {'name': user.first_name, 'otp': otp}
            )
            sendgrid.send_signup_email_verification_otp(user.username, html_content)
            return JsonResponse({'message': 'New verification code sent successfully! Please check your email for a verification code to complete your registration.'},status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ResendLoginOTPView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({'error': 'Invalid username.'}, status=400)
            sendgrid = sendgrid_connector.SendgridConnector()
            otp = generate_otp()
            cache.set(f"otp_{user.pk}", otp, timeout=600)
            html_content = render_to_string(
                'login_otp.html', 
                {'name': user.first_name, 'otp': otp}
            )
            sendgrid.send_login_otp(user.username, html_content)
            return JsonResponse({'message': 'Verification code sent to your email. Please verify to complete login.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UserRegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            sendgrid = sendgrid_connector.SendgridConnector()
            
            if not first_name or not last_name or not username or not password:
                return JsonResponse(
                    {'error': 'All fields are required.'}, 
                    status=400
                )
            
            if User.objects.filter(username=username).exists():
                return JsonResponse(
                    {'error': 'Username is already registered.'}, 
                    status=400
                )

            if role not in dict(UserRole.USER_ROLES):
                return JsonResponse({'error': 'Invalid role.'}, status=400)
            
            with transaction.atomic():
                user = User.objects.create_user(
                    first_name=first_name, 
                    last_name=last_name, 
                    username=username, 
                    password=password
                )
                user_role = UserRole.objects.create(
                    user=user, 
                    role=role
                )

            otp = generate_otp()
            cache.set(f"otp_{user.pk}", otp, timeout=600)

            html_content = render_to_string(
                'verification_otp.html', 
                {'name': user.first_name, 'otp': otp}
            )
            sendgrid.send_signup_email_verification_otp(user.username, html_content)

            return JsonResponse(
                {'message': 'Account created successfully! Please check your email for a verification code to complete your registration.'},
                status=201
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            otp = data.get('otp')

            if not username or not otp:
                return JsonResponse(
                    {'error': 'Both username and verification code are required.'}, 
                    status=400
                )

            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse(
                    {'error': 'Invalid username.'}, 
                    status=400
                )

            cached_otp = cache.get(f"otp_{user.pk}")
            if cached_otp == otp:
                user.is_verified = True
                user.save()
                cache.delete(f"otp_{user.pk}")
                return JsonResponse(
                    {'message': 'Email verification successful!'}, 
                    status=200
                )
            else:
                return JsonResponse(
                    {'error': 'Invalid verification code.'}, 
                    status=400
                )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse(
                    {'error': 'Both username and password are required.'}, 
                    status=400
                )
            
            user = authenticate(
                request, 
                username=username, 
                password=password
            )

            if settings.DEBUG == 'True':
                if user is not None:
                    if not user.is_verified:
                        return JsonResponse(
                            {'error': 'Your account is not verified. Please verify your email to log in.'}, 
                            status=401
                        )
                    else:
                        if user.username == guestUser:
                            login(request, user)
                            return JsonResponse(
                                {'message': 'Login successful!', 'verifyotp': False}, 
                                status=200
                            )
                        elif user.username.endswith('@iqland.ai') or user.username in testUsers:
                            send_otp(user)
                            return JsonResponse(
                                {'message': 'Verification code sent to your email. Please verify to complete login.', 'verifyotp': True}, 
                                status=200
                            )
                        else:
                            return JsonResponse(
                                {'error': 'You are not authorized to login to test.iqland.ai. If you want to use Iqland create account on iqland.ai.'}, 
                                status=401
                            )

            if user is not None:
                if not user.is_verified:
                    return JsonResponse(
                        {'error': 'Your account is not verified. Please verify your email to log in.'}, 
                        status=401
                    )
                
                send_otp(user)
                return JsonResponse(
                    {'message': 'Verification code sent to your email. Please verify to complete login.', 'verifyotp': True}, 
                    status=200
                )
            
            return JsonResponse(
                {'error': 'Invalid credentials.'}, 
                status=400
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )

@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            otp = data.get('otp')

            if not username or not otp:
                return JsonResponse(
                    {'error': 'Both username and verification code are required.'}, 
                    status=400
                )

            user = User.objects.filter(username=username).first()
            if not user or not user.is_verified:
                return JsonResponse(
                    {'error': 'Invalid username.'}, 
                    status=400
                )

            cached_otp = cache.get(f"otp_{user.pk}")
            if cached_otp == otp:
                login(request, user)
                cache.delete(f"otp_{user.pk}")
                return JsonResponse(
                    {'message': 'Login successful!'}, 
                    status=200
                )
            else:
                return JsonResponse(
                    {'error': 'Invalid verification code.'}, 
                    status=400
                )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        

class UserLogoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'You are not logged in.'}, 
                    status=400
                )
        
            logout(request)

            return JsonResponse(
                {'message': 'Logged out successfully!'}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        
@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            sendgrid = sendgrid_connector.SendgridConnector()

            if not email:
                return JsonResponse(
                    {'error': 'Email is required.'}, 
                    status=400
                )

            user = User.objects.filter(username=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                sendgrid.send_reset_password_link(
                    email, 
                    reset_url
                )

            return JsonResponse(
                {'message': 'If an account with that email exists, a password reset email has been sent.'}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            uidb64 = data.get('uidb64')
            token = data.get('token')
            new_password = data.get('new_password')

            if not new_password:
                return JsonResponse(
                    {'error': 'New password is required.'}, 
                    status=400
                )

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return JsonResponse(
                    {'message': 'Password has been reset successfully!'}, 
                    status=200
                )
            else:
                return JsonResponse(
                    {'error': 'Invalid token or user ID.'}, 
                    status=400
                )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


class ChangePasswordView(LoginRequiredMixin, View):
    def patch(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            new_password = data.get('new_password')

            if not new_password:
                return JsonResponse(
                    {'error': 'New password is required.'}, 
                    status=400
                )

            request.user.set_password(new_password)
            request.user.save()
            
            return JsonResponse(
                {'message': 'Password updated successfully! Please sign in again with your new password.'}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


class ProfileInfoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            profile = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.username,
                'phone': request.user.phone,
            }
            return JsonResponse(
                {'data': profile }, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        
    def patch(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            
            for key, value in data.items():
                if key != 'username' and hasattr(user, key):
                    setattr(user, key, value)

            user.save()

            updated_profile = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.username,
                'phone': user.phone,
            }

            return JsonResponse(
                {
                    'message': 'Profile information updated successfully.',
                    'data' : updated_profile
                }, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )


class TestSessionView(View):
    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'isauthenticated': False}, 
                )

            return JsonResponse(
                {'isauthenticated': True, 'username': request.user.username}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        

@method_decorator(csrf_exempt, name='dispatch')     
class TestEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            sendgrid = sendgrid_connector.SendgridConnector()
            response = sendgrid.send_signup_email_verification_otp(
                email, 
                123456
            )

            return JsonResponse(
                {'message': 'Email sent successfully!'}, 
                status=200
            )

        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )
        
class GetCsrfTokenView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'csrfToken': get_token(request)})
