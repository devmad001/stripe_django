from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('resend-verify-email-otp/', views.ResendEmailVerificationOTPView.as_view(), name="resend_verify_email_otp"),
    path('resend-login-otp/', views.ResendLoginOTPView.as_view(), name="resend_login_otp"),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile-info/', views.ProfileInfoView.as_view(), name='profile_info'),
    path('session/', views.TestSessionView.as_view(), name='test_session'),
    path('email/', views.TestEmailView.as_view(), name='test_email'),
    path('get-csrf-token/', views.GetCsrfTokenView.as_view(), name='get_csrf_token')
]