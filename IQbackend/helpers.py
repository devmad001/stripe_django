import us
import requests
from django.conf import settings
from django.http import JsonResponse
from zoning.gis.get_parcel_information import getParcelAddressFromId

def validateAddress(address):
    api_key = settings.GOOGLE_ADDRESS_VALIDATION_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        result = data['results'][0]
        formatted_address = result['formatted_address']
        components = result['address_components']
        return {
            'city': next((comp['long_name'] for comp in components if 'locality' in comp['types']), None),
            'state': next((comp['short_name'] for comp in components if 'administrative_area_level_1' in comp['types']), None),
            'full_state': next((comp['long_name'] for comp in components if 'administrative_area_level_1' in comp['types']), None),
            'county': next((comp['long_name'] for comp in components if 'administrative_area_level_2' in comp['types']), None),
            'street_address': formatted_address.split(', ')[0].strip(),
            'full_address': formatted_address,
            'lng': data['results'][0]['geometry']['location']['lng'],
            'lat': data['results'][0]['geometry']['location']['lat']
        }
    else:
        components = address.split(', ')
        return {
            'city': components[1].strip(),
            'state': components[2].strip(),
            'full_state': us.states.lookup(components[2].strip()).name,
            'street_address': components[0].strip(),
            'full_address': address,
            'county': '',
            'lng': None,
            'lat': None
        }

def getValidatedAddress(request, address):
    if 'validated_addresses' not in request.session:
        request.session['validated_addresses'] = {}

    if address in request.session['validated_addresses']:
        return request.session['validated_addresses'][address]
    else:
        validated_address = validateAddress(address)
        request.session['validated_addresses'][address] = validated_address
        return validated_address

def processAddress(request, address):
    validated_address = getValidatedAddress(request, address)
    
    request.session['original_address'] = address
    request.session['validated_address'] = validated_address
    
    return validated_address
