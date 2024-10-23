from django.urls import path
from . import views

urlpatterns = [
    path('favorites/', views.ListFavoritePlansView.as_view(), name='get_favorites'),
    path('favorites/new/', views.AddFavoritePlanView.as_view(), name='add_to_favorites'),
    path('favorites/remove/', views.RemoveFavoritePlanView.as_view(), name='remove_from_favorites'),
    path('architectural_plans/', views.GetArchitecturalPlansView.as_view(), name="get_architectural_plans")
]