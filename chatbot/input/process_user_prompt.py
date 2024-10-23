

import json
from .address_processing import is_address_valid, is_deployed
from chatbot.response.tools import process_cost_estimation, process_zoning, process_allowed_structures, process_parcel_info, process_plan_recommendation, process_optimize_roi
from chatbot.response.textual_response import final_response_other_intent
from chatbot.input.address_processing import get_zoning_info
from chat.helpers import checkChatAddressExistence, saveChatHistory, getAddress
from chat.models import UncoveredAddress

def check_missing_inputs(json_response):
    '''
    This function checks if there are any mising inputs for the given request_type, so that frontend can display form based on that.

    input:
        json_response (dict) containing generated json.

    output:
        missing (dict) containing boolean and list of missing inputs
    '''

    required_keys_map = {
        'zoning': ['address', 'parcel_id', 'city', 'county'],
        'cost_estimation': ['address','parcel_id', 'city', 'county', 'building_area', 'building_quality'],
        'plan_recommendation': ['address','parcel_id', 'city', 'county', 'min_total_area', 'max_total_area', 'stories'],
        'parcel_info': ['address','parcel_id', 'city', 'county'],
        'allowed_structures': ['address', 'parcel_id', 'city', 'county'],
        'other': []
    }

    request_type = json_response.get('request_type', 'other')
    required_keys = required_keys_map.get(request_type, [])

    missing_inputs = [key for key in required_keys if json_response.get(key, 'NA') == 'NA']

    if missing_inputs:
        missing = {
            'missing_inputs': True,
            'list_of_missing_inputs': missing_inputs
        }
    else:
        missing = {
            'missing_inputs': False,
            'list_of_missing_inputs': []
        }
    return missing

def check_address_and_save_history(user, json_response, chat_id):
    plans = json_response.get('plans', [])
    if len(plans):
        plans = [plan['id'] for plan in plans]
    sources = json_response.get('sources', [])
    map = json_response.get('map', None)
    remaining_plans_query = json_response.get('remaining_plans_query', None)
    address = json_response.get('address', None)
    address = None if address == 'NA' else address
    title = (json_response.get('user_prompt', 'New Chat'))[0:25] if address == None or address == 'NA' else address
    # handle other request type which does not have address
    if json_response.get('request_type','other') == "other" and not address and not chat_id:
        chat_history = saveChatHistory(user, title, json_response.get('user_prompt', ''), 'User', None, address)
        saveChatHistory(user, None, json_response.get('llm_response'), 'Bot', chat_history['data']['chat_id'], None, sources, plans, map, remaining_plans_query)
        json_response['chat_id'] = chat_history['data']['chat_id']
        json_response['new_chat'] = chat_history['data']['new_chat']
        return json_response
    # handle remaining request types that have address
    if not chat_id and not address:
        chat_history = saveChatHistory(user, title, json_response.get('user_prompt', ''), 'User', None, address)
        saveChatHistory(user, None, json_response.get('llm_response'), 'Bot', chat_history['data']['chat_id'], None, sources, plans, map, remaining_plans_query)
    else:
        chat = checkChatAddressExistence(user, address, chat_id)
        if (chat['chat_exists']):
            saveChatHistory(user, None, json_response.get('user_prompt', ''), 'User', chat['chat_id'], address)
            chat_history = saveChatHistory(user, None, json_response.get('llm_response'), 'Bot', chat['chat_id'], address, sources, plans, map, remaining_plans_query)
        else:
            chat_history = saveChatHistory(user, address, json_response.get('user_prompt', ''), 'User', None, address)
            saveChatHistory(user, None, json_response.get('llm_response'), 'Bot', chat_history['data']['chat_id'], address, sources, plans, map, remaining_plans_query)
    json_response['chat_id'] = chat_history['data']['chat_id']
    json_response['new_chat'] = chat_history['data']['new_chat']
    return json_response

def process_user_prompt_json(request, json_response, chat_id):
    '''
    This function verifies the conformity of the generated json and orients the LLM to the appropriate path of conversation.

    input:
        json_response (dict) containing generated json. 
            
    output:
            llm_response (string)
    '''

    llm_response = ''

    #if no address provided but chat previously had address
    if json_response.get('address', 'NA') == 'NA' and chat_id:
        json_response['address'] = getAddress(request.user, chat_id)
        
    # if json non valid format.
    if json_response.get('request_type','other') == "other":
        llm_response =  final_response_other_intent(json_response.get('user_prompt', ''))
    else:
        zoning_and_address = get_zoning_info(request, json_response['address'], json_response['parcel_id'], json_response['city'], json_response['county'])
        if json_response['parcel_id'] != "NA" and (json_response['city'] == "NA" or json_response['county'] == "NA"):
            json_response['address'] = "NA"
            llm_response = "Sorry, but I was unable to understand your address. Could you please specify city and county along with parcel number one more time ?"
        # if address is still not there and is not valid
        elif json_response['address'] == "NA" or is_address_valid(request, json_response['address'])==False:
            json_response['address'] = "NA"
            llm_response = "Sorry, but I was unable to understand your address. Could you please specify it one more time ?"
        elif json_response['address'] == "NA" and json_response['parcel_id'] == "NA":
            json_response['address'] = "NA"
            llm_response = "Sorry, but I was unable to understand your address. Could you please specify it one more time ?"
        # if no
        elif not is_deployed(json_response['address']):
            UncoveredAddress.objects.create(
                user=request.user,
                query=json_response.get('user_prompt', ''),
                address=json_response.get('address', '')
            )
            llm_response = "Sorry, I am not able to process requests for this city yet. Please do not hesitate to contact us to know more about our future deployments."
        else:
            #fetch zoning code city and state
            zoning_info = zoning_and_address['zoning']
            json_response['address'] = zoning_and_address['formatted_address']
            
            for key in zoning_info:
                json_response[key] = zoning_info[key]

            if json_response.get('request_type','')=='zoning':
                llm_response = process_zoning(json_response)

            elif json_response.get('request_type','')=='cost_estimation':
                llm_response = process_cost_estimation(json_response)

            elif json_response.get('request_type','')=='plan_recommendation':
                llm_response = process_plan_recommendation(request, json_response, zoning_and_address['original_polygon_with_latlng'])

            elif json_response.get('request_type','')=='allowed_structures':
                llm_response = process_allowed_structures(json_response)

            elif json_response.get('request_type','')=='parcel_info':
                llm_response = process_parcel_info(zoning_and_address['original_polygon_with_latlng'], json_response)
                
            elif json_response.get('request_type','')=='optimize_roi':
                llm_response = process_optimize_roi(request, zoning_and_address['original_polygon_with_latlng'], json_response)

    json_response['llm_response'] = llm_response
    json_response['missing_inputs'] = check_missing_inputs(json_response)
    json_response = check_address_and_save_history(request.user, json_response, chat_id)
    return json_response

