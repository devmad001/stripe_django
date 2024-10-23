from django.urls import path
from . import views

urlpatterns = [
    path('demo_populateZoningSection/', views.demo_populateZoningSection, name="demo_populateZoningSection"), #GET
    path('get_far_api/', views.get_far_api, name='get_far_api'),
    path('get_front_set_back_api/', views.get_front_set_back_api, name='get_front_set_back_api'),
    path('get_lot_coverage_api/', views.get_lot_coverage_api, name='get_lot_coverage_api'),
    path('get_rear_set_back_api/', views.get_rear_set_back_api, name='get_rear_set_back_api'),
    path('get_side_set_back_api/', views.get_side_set_back_api, name='get_side_set_back_api'),
    path('get_building_height_api/', views.get_building_height_api, name='get_building_height_api'),
    path('get_frontage_api/', views.get_frontage_api, name='get_frontage_api'),
    path('get_parking_cap_api/', views.get_parking_cap_api, name='get_parking_cap_api'),
    path('get_structure_type_api/', views.get_structure_type_api, name='get_structure_type_api'),
    path('zoning/', views.GetZoningView.as_view(), name='get_zoning'),
]