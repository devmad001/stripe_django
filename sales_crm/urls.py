from django.urls import path
from . import views

urlpatterns = [
    path('waitlist/', views.WaitlistUserView.as_view(), name='waitlist'),
    path('municipality-contact-info/', views.MContactInfoView.as_view(), name='mcontactinfo'),
]