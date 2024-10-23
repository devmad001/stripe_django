# urls.py
from django.urls import path, include
# from .views import register_client
from main_application import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Commercial version Routes
    path('dashboard/', views.dashboard, name='dashboard'), #GET
    
    path('municipality_dashboard/', views.municipality_dashboard, name="municipality_dashboard"), #GET


    ###### DASHBOARD DEMO API ENDPOINTS #####

    path('demo_populateDashBoard/', views.demo_populateDashBoard, name="demo_populateDashBoard"), #POST
    path('demo_populatePropertyInfoSection/', views.demo_populatePropertyInfoSection, name="demo_populatePropertyInfoSection"), #GET
    path('demo_change_buildQuality/',views.demo_change_buildQuality,name="demo_change_buildQuality"), #POST
    path('demo_change_ArchitecturalPlan/',views.demo_change_ArchitecturalPlan,name="demo_change_ArchitecturalPlan"), #POST
    path('demo_getSession/', views.demo_getSession, name="demo_getSession"), #GET

    # Other URL patterns...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
