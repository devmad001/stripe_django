from django.urls import path
from . import views

urlpatterns = [
    path('get-municipality-response/', views.get_municipality_response, name='get_municipality_response'),
    path('permit-info/<str:permit_number>/', views.permit_info, name='permit_info'),
]