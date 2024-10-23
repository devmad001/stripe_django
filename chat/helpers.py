import json
from chat.models import Chat, Message
from django.db import transaction
from IQbackend.helpers import validateAddress
from django.shortcuts import get_object_or_404

def store_conversation(user_message, bot_response):
    # Load existing chat history if available
    try:
        with open('ml_models/data/chat_history.json', 'r') as file:
            chat_history = json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        chat_history = []

    # Append the new message to the chat history
    chat_history.append(bot_response)

    # Write the updated chat history back to the file
    with open('ml_models/data/chat_history.json', 'w') as file:
        json.dump(chat_history, file)
# static data with json file storage for testing end

def generate_bot_response(user_message):
    # Sample data for bot response
    bot_response = {
        "id": 1,
        "message": [
            {
                "id": 1,
                "user_chat": user_message,
                "bot_chat": {
                    "sources": [
                        {
                            "id": 1,
                            "text": "FAR for R5 parcel",
                            "favicon": "https://images.softwaresuggest.com/latest_screenshots/1616241910950newphotos.png",
                            "title": "source"
                        },
                        {
                            "id": 2,
                            "text": "Structural requirement for a 3 story home",
                            "favicon": "https://images.softwaresuggest.com/latest_screenshots/1616241910950newphotos.png",
                            "title": "source"
                        },
                        {
                            "id": 3,
                            "text": "Lot coverage for R5 parcel",
                            "favicon": "https://images.softwaresuggest.com/latest_screenshots/1616241910950newphotos.png",
                            "title": "source"
                        },
                        {
                            "id": 4,
                            "text": "Plumbing regulations for 2400 square foot home.",
                            "favicon": "https://images.softwaresuggest.com/latest_screenshots/1616241910950newphotos.png",
                            "title": "source"
                        }
                    ],
                    "answer": "For 123 Main Street, the property allows for a construction footprint of up to 2,400 square feet. This size accommodates a spacious 4 bedroom, 3 bathroom layout, ideal for residential development aiming at both comfort and functionality. Considering the current market rates for materials, labor, and other construction-related expenses in the area, the projected cost to bring this plan to fruition is estimated at approximately $425,000. This estimate is derived from a detailed analysis of local building costs, ensuring a realistic budget overview. Additionally, this development plan aligns with the local zoning regulations, providing a straightforward path through the permitting process. Utilizing this information effectively can help in optimizing your project's financial planning and architectural design, ensuring a balance between aesthetic appeal and cost-efficiency.",
                    "follow_up": [
                        {
                            "id": 1,
                            "question": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines.",
                            "answer": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines."
                        },
                        {
                            "id": 2,
                            "question": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines.",
                            "answer": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines."
                        },
                        {
                            "id": 3,
                            "question": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines.",
                            "answer": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines."
                        },
                        {
                            "id": 4,
                            "question": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines.",
                            "answer": "Explore zoning regulations and constraints for 123 Main Street to align your development with local guidelines."
                        }
                    ]
                }
            }
        ]
    }
    
    return bot_response

def saveChatHistory(user, chat_title, text, sent_by, chat_id= None, chat_address = None, sources = [], plans = [], map = None, remaining_plans_query = None):
    new_chat = False
    if not chat_title:
        chat_title = 'New Chat'
    with transaction.atomic():
        if not chat_id:
            chat = Chat.objects.create(user=user, title=chat_title, address='NA')
            new_chat = True
        else:
            chat = get_object_or_404(Chat, id=chat_id, user=user)
        if chat_address:
            try:
                chat_address = validateAddress(chat_address)['full_address']
            except Exception as e:
                chat_address = None
            if chat_address:
                chat.title = chat_address
            chat.address = chat_address
            chat.save()

        message = Message.objects.create(chat=chat, text=text, sent_by=sent_by, sources=sources, map=map, remaining_plans_query=remaining_plans_query)
        if len(plans):
            message.architectural_plans.set(plans)
            message.save()
    return {
        'message': 'Message saved successfully!',
        'data': {'chat_id': chat.id, 'message_id': message.id, 'new_chat': new_chat},
    }

def checkChatExistence(user, chat_address):
    chat = Chat.objects.filter(user=user, address=chat_address).first()
    if chat:
        return {
            'chat_exists': True,
            'chat_id': chat.id
        }
    else:
        return {
            'chat_exists': False,
            'chat_id': None
        }
    
def getAddress(user, chat_id):
    chat = Chat.objects.filter(user=user, id=chat_id).first()
    if chat.address == 'NA' or chat.address == None:
        return 'NA'
    else:
        return chat.address
    
def checkChatAddressExistence(user, chat_address, chat_id):
    chat = None
    
    if chat_id:
        chat = Chat.objects.filter(user=user, id=chat_id).first()
    
    if not chat and chat_address and chat_address != 'NA':
        chat = Chat.objects.filter(user=user, address=chat_address).first()
    
    if chat:
        if chat.address == 'NA':
            return {
                'chat_exists': True,
                'chat_id': chat.id
            }
        elif chat.address == chat_address:
            return {
                'chat_exists': True,
                'chat_id': chat.id
            }
        else:
            confirmChat = Chat.objects.filter(user=user, address=chat_address).first()
            if confirmChat:
                return {
                    'chat_exists': True,
                    'chat_id': confirmChat.id
                }
            else:
                return {
                    'chat_exists': False,
                    'chat_id': None
                }
    else:
        return {
            'chat_exists': False,
            'chat_id': None
        }
