from django.urls import path
from . import views

urlpatterns = [
    path('get_construction_cost/', views.get_construction_cost, name='get_construction_cost'), # return 2 value, per squre feet, contruction cost
    path('comparable-sales/', views.GetComparableSalesViews.as_view(), name='get_comparable_sales'),
    path('kpis/', views.GetKPIsView.as_view(), name='get_kpis'),
    path('property/', views.GetPropertyInfoView.as_view(), name='get_property')
]