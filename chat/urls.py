from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.GetAllChatsView.as_view(), name='get_all_chats'),
    path('chats/address/<uuid:chat_id>/', views.GetChatAddressView.as_view(), name="get_chat_address"),
    path('chats/<uuid:chat_id>/', views.GetChatView.as_view(), name='get_chat'),
]