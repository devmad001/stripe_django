from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from IQbackend.mixins.auth import LoginRequiredMixin
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin

from chat.models import Chat, Message

class GetChatAddressView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            chat_id = kwargs.get('chat_id')
            chat = get_object_or_404(Chat, id=chat_id, user=request.user)

            data = {
                'chat_id': chat.id,
                'title': chat.title,
                'address': chat.address
            }

            return JsonResponse({'message': 'Chat fetched successfully!', 'data': data}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
class GetChatView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            chat_id = kwargs.get('chat_id')
            chat = get_object_or_404(Chat, id=chat_id, user=request.user)
            messages = Message.objects.filter(chat=chat).order_by('created_at')
    
            data = {
                'chat_id': chat.id,
                'title': chat.title,
                'address': chat.address,
                'messages': [{
                    'id': message.id,
                    'text': message.text,
                    'sources': message.sources,
                    'sent_by': message.sent_by,
                    'updated_at': message.updated_at,
                    'map': message.map,
                    'plans': list(message.architectural_plans.values()),
                    'remaining_plans_query': message.remaining_plans_query
                } for message in messages]
            }

            return JsonResponse(
                {'message': 'Chat fetched successfully!', 'data': data}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=400
            )

class GetAllChatsView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            chats = Chat.objects.filter(user=request.user).order_by('-updated_at')
            data = [{'chat_id': chat.id, 'chat_title': chat.title, 'chat_address': chat.address, 'updated_at': chat.updated_at} for chat in chats]
            return JsonResponse(
                {'message': 'Chats fetched successfully!', 'data': data}, 
                status=200
            )
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=400
            )