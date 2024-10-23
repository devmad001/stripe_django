from django.urls import path
from . import views

urlpatterns = [
    path('profile-picture/', views.GetProfilePictureView.as_view(), name='profile_picture'),
    path('upload-profile-picture/', views.UploadProfilePictureView.as_view(), name='profile_picture'),
    path('profile-settings/', views.ProfileSettingsView.as_view(), name='profile_settings'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/<uuid:report_id>/', views.GetReportView.as_view(), name='get_report'),
    path('reports/<uuid:report_id>/update-cost/', views.UpdateReportCostView.as_view(), name='update_report'),
    path('reports/<uuid:report_id>/send-email/', views.SendReportEmailView.as_view(), name='send_report_email'),
]