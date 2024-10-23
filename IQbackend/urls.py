"""
URL configuration for IQbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from .views import google_signin
from main_application import  views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('payments.urls')),
    path('', include('authentication.urls')),
    path('', include('users.urls')),
    path('', include('architectural_plans.urls')),
    path('', include('chat.urls')),
    path('', include('sales_crm.urls')),
    path('', include('chatbot.urls')),
    path('', include('cost_estimation.urls')),
    path('', include('zoning.urls')),
    path('', include('permits.urls')),
    path('', include('main_application.urls')),
    # path('accounts/', include('allauth.urls')),
    # path('api/google-signin/', views.google_signin, name='google_signin'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
