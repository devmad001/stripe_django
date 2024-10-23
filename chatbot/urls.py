from django.urls import path
from . import views

urlpatterns = [
    path('get_response_from_LLM/', views.GetResponseFromLLM.as_view(), name='get_response_from_LLM'),
]