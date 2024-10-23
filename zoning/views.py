import json
import pymongo
from fuzzywuzzy import fuzz
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from langchain_openai import ChatOpenAI
from IQbackend.helpers import processAddress
from IQbackend.mixins.auth import LoginRequiredMixin
from zoning.gis.get_zoning_from_polygon import getZoningCode
from zoning.gis.setback_calculations import getSetbackPolygon
from zoning.gis.get_polygons_from_coords_db import getPolygon
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin
from zoning.gis.common_functions import polygonToCoordinatesList
from main_application.helper import handle_api_error, dict_to_object
from zoning.helpers import processZoningData, processZoningDataResponse, getCityZoningMap, getMaximumBuildableArea, getSideSetback
from zoning.gis.get_parcel_information import getParcelAddressFromId

mongodb_path = settings.MONGODB_URL
llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)

dbclient = pymongo.MongoClient(mongodb_path)
iqlandDB = dbclient["IQLAND"]
vectors_collection = iqlandDB["Zoning_vectors"]
zoning_collection = iqlandDB["Zoning"]

def demo_populateZoningSection(request):
    return JsonResponse({"api_resp": request.session['dash_demo_zoningObj']})

def getFar(zoning_obj):
    return zoning_obj.zoning_far

@handle_api_error
def get_far_api(request):
    get_far = getFar(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"get_far": get_far})

def getFrontSetBack(zoning_obj):
    return zoning_obj.zoning_min_front_setback

@handle_api_error
def get_front_set_back_api(request):
    get_front_set_back = getFrontSetBack(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"getFront_setBack": get_front_set_back})

def getLotCoverage(zoning_obj):
    return zoning_obj.zoning_lot_coverage

@handle_api_error
def get_lot_coverage_api(request):
    get_lot_cov = getLotCoverage(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"get_lot_cov": get_lot_cov})

def getRearSetBack(zoning_obj):
    return zoning_obj.zoning_min_rear_setback

@handle_api_error
def get_rear_set_back_api(request):
    get_rear_set_back = getRearSetBack(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"get_rear_set_back": get_rear_set_back})

def getSideSetBack(zoning_obj):
    return zoning_obj.zoning_min_side_setback

@handle_api_error
def get_side_set_back_api(request):
    get_side_set_back = getSideSetBack(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"get_side_set_back": get_side_set_back})

def getBuildingHeight(zoning_obj):
    return zoning_obj.zoning_building_height

@handle_api_error
def get_building_height_api(request):
    get_building_height = getBuildingHeight(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"building_height": get_building_height})

def getFrontage(zoning_obj):
    return zoning_obj.zoning_min_frontage

@handle_api_error
def get_frontage_api(request):
    get_frontage = getFrontage(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"frontage": get_frontage})

def getParkingCap(zoning_obj):
    return zoning_obj.zoning_parking_capacity

@handle_api_error
def get_parking_cap_api(request):
    get_parking_cap = getParkingCap(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"parking_cap": get_parking_cap})

def getStructureType(zoning_obj):
    return zoning_obj.structure_type

@handle_api_error
def get_structure_type_api(request):
    get_structure_type = getStructureType(dict_to_object(request.session['zoning_obj']))
    return JsonResponse({"structure_type": get_structure_type})

def extract_all_zoning_codes(collection):
    """
    extract all zoning codes stored in given mongoDB collection.

    input:
        collection (pymongo object) on which to run the query.
    
    output:
        list containing all stored zoning codes.
    """
    pipeline = [
        {"$group": {"_id": "$zoning_code"}}
    ]
    distinct_zoning_codes = collection.aggregate(pipeline)
    return [doc["_id"] for doc in distinct_zoning_codes]

def find_closest_match(target_code, zoning_codes):
    """
    fuzzy search for closest match between a given string and the list of zoning codes stored in mongoDB.

    input:
            target_code (string)
            zoning_codes (list of strings)
    output:
            string containing value of best match 
    """
    best_match = None
    best_score = 0
    
    for code in zoning_codes:
        score = fuzz.ratio(target_code, code)
        if score > best_score:
            best_match = code
            best_score = score
    
    return best_match

def map_zoning_code(target_code,collection):
    '''
    Extract all zoning codes and returns the closest match.

    input:
            target_code (string) containing the value on which to run fuzzy matching.
            collection (pymongo object) containing the list of zoning codes in mongoDB.
    '''
    zoning_codes_in_db = extract_all_zoning_codes(collection)
    return find_closest_match(target_code,zoning_codes_in_db)

class GetZoningView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
            parcel_id = data.get('parcel_id', None)
            if (parcel_id):
                city = data.get('city', None)
                county = data.get('county', None)
                if (city != None or county != None):
                    result = getParcelAddressFromId(parcel_id, city, county)
                    if result:
                        address = result
                    else:
                        return JsonResponse({'data': {}, 'message': 'To get data from parcel number, you need to give city and county as well.'}, status=404)
            address = processAddress(request, address)
            report_id = data.get('report_id')
            city, state = address['city'], address['full_state']
            original_polygon_with_latlng = {'polygon': [], 'coords': {'lat': 0, 'lng': 0}}
            original_polygon_with_latlng = getPolygon(address['lat'], address['lng'])
            if not original_polygon_with_latlng:
                return JsonResponse({'error': 'Polygon not found', 'message': 'We are unable to find the parcel record in our database.', 'showMessage': True}, status=400)
            zoning_code = getZoningCode(original_polygon_with_latlng['polygon'])
            zoning_document = zoning_collection.find_one({"zoning_code_gis": {"$in": [zoning_code]}, "city": city, "state": state})
            if not zoning_document:
                data = processZoningDataResponse(city, original_polygon_with_latlng, None, '-', None, [], {'zoning_code': zoning_code}, report_id, request.user)
                message = f"We currently only process residential zoning requests. This parcel is classified {data['parcel']['property_type']}" if data['parcel']['property_type'] else 'We currently only process residential zoning requests. This parcel is classified (commercial, industrial, etc.)'
                return JsonResponse({'data': data, 'message': message, 'showMessage': True}, status=200)
            cityZoningMap = getCityZoningMap(city)
            front_setback = zoning_document[cityZoningMap['front_setback']]['value']
            side_setback = getSideSetback(original_polygon_with_latlng['polygon'], city, zoning_document, cityZoningMap)
            rear_setback = zoning_document[cityZoningMap['rear_setback']]['value']
            setbackPolygonData = getSetbackPolygon(address['full_address'], original_polygon_with_latlng['polygon'], front_setback, rear_setback, side_setback)
            zoning = processZoningData(city, cityZoningMap, zoning_document, zoning_code, front_setback, rear_setback, side_setback)
            if not setbackPolygonData:
                data = processZoningDataResponse(city, original_polygon_with_latlng, None, '-', None, [], zoning, report_id, request.user)
                return JsonResponse({
                    'data': data, 'message': f'We are unable to process the given parcel completely.', 'showMessage': True
                }, status=200)
            final_polygon, sides, areas, original_sides = setbackPolygonData
            final_polygon = polygonToCoordinatesList(final_polygon)
            max_buildable_area = getMaximumBuildableArea(city, cityZoningMap, areas, zoning_document)
            open_area = None
            if city == 'Tulsa':
                open_area = zoning_document['minimum_open_space_per_unit']['value']
            elif city == 'Oklahoma City':
                if max_buildable_area['max_coverage_area']:
                    if areas:
                        open_area = areas[0]-max_buildable_area['max_coverage_area']
            data = processZoningDataResponse(city, original_polygon_with_latlng, areas, open_area, sides, final_polygon, zoning, report_id, request.user, max_buildable_area, original_sides)

            return JsonResponse({'data': data, 'message': 'Zoning information fetched successfully', 'showMessage': False}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e), 'message': 'An error occurred while processing your request.', 'showMessage': False}, status=500)