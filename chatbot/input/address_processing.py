import pandas as pd
from IQbackend.helpers import processAddress
from zoning.gis.get_polygons_from_coords_db import getPolygon
from zoning.gis.get_polygon_from_address_db import getPolygon as getPolygonAddress
from zoning.gis.get_zoning_from_polygon import getZoningCode
from zoning.gis.get_parcel_information import getParcelAddressFromId

DEPLOYED_CITIES = ['Tulsa', 'Oklahoma City', 'OKC']

def is_address_valid(request, address):
    '''
    check if address is valid.

    input:
            address (string)

    output:
            boolean (True if deployed)
    '''
    try:
        address = processAddress(request, address)
        return True
    except Exception as e:
        return False
    
# check if deployed
def is_deployed(address):
    '''
    check if address is in a deployed city.

    input:
            address (string)

    output:
            boolean (True if deployed)
    '''

    for city in DEPLOYED_CITIES:
        if city.lower() in address.lower():
            return True
    
    return False

def get_zoning_info(request, address_str, parcel_id, city_, county_):
    """
    retrieves zoning information from attom.

    input:
        address string.
    output:
        json_response with "zoning_code", "city" and "state"
    
    """
    address = {
                'city': 'NA',
                'state': 'NA',
                'county': 'NA',
                'state_short': 'NA',
                'full_state': 'NA',
                'full_address': address_str,
                'street_address': 'NA',
                'lng': None,
                'lat': None
            }
    try:
        if parcel_id != "NA":
            address_ = getParcelAddressFromId(parcel_id, city_, county_)
            if address_:
                address = processAddress(request, address_)
        else: 
            address = processAddress(request, address_str)
    except Exception as e:
        print(f'Error: {str(e)}')
    city, state, state_short, county, street_address = address['city'], address['full_state'], address['state'], address['county'], address['street_address']
    zoning_code = 'R-3' if city == 'Oklahoma City' else 'RS-3'
    original_polygon_with_latlng = {'polygon': [], 'coords': {'lat': 0, 'lng': 0}}
    if (address['lng'] != None and address['lat'] != None):
        original_polygon_with_latlng = getPolygon(address['lat'], address['lng'])
    else:
        original_polygon_with_latlng = getPolygonAddress(address['full_address'])
    if original_polygon_with_latlng:
        zoning_code = getZoningCode(original_polygon_with_latlng['polygon'])
    zoning_info = {
        'city': city,
        'state':  state,
        'state_short': state_short,
        'zoning_code': zoning_code,
        'county': county,
        'street_address': street_address
    }
    return {'zoning': zoning_info, 'formatted_address': address['full_address'], 'original_polygon_with_latlng': original_polygon_with_latlng}
    
def getMSANameForCounty(county_name, state_name):
    county_name = county_name.upper().strip()
    state_name = state_name.upper().strip()
    data_path = 'ml_models/models/cost_model/mapping_files/'
    county_to_msa_file =  pd.read_csv(data_path+'county_to_msa_mapping.csv')
    state_county_cmb = state_name+','+county_name
    for msa_name,state_county_val in zip(county_to_msa_file['MSA'],	county_to_msa_file['State_county']):
        if(state_county_cmb == state_county_val):
            return msa_name
    return False