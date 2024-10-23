import json
from django.views import View
from django.http import JsonResponse
from langchain_openai import ChatOpenAI
from IQbackend.mixins.auth import LoginRequiredMixin
from .input.process_user_prompt import process_user_prompt_json
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin
from .input.input_processing import generate_json_response, get_user_request

class GetResponseFromLLM(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user_input = data.get('user_message')
        chat_id = data.get('chat_id', None)

        json_response = generate_json_response(user_input,get_user_request)

        llm_response = process_user_prompt_json(request, json_response, chat_id)
        
        return JsonResponse(llm_response)