import json
import pymongo
from .data_types import ZoneInfo
from users.models import Report
from zoning.gis.lot_corner_check import isCorner
from shapely.geometry import Polygon
from zoning.gis.get_polygons_from_coords_db import getPolygon
from zoning.gis.common_functions import polygonToCoordinatesList
from zoning.gis.setback_calculations import getSetbackPolygon
from zoning.gis.get_zoning_from_polygon import getZoningCode
from zoning.gis.get_parcel_information import getParcelInformation
from IQbackend.helpers import processAddress
from django.conf import settings

def demo_getZoningObj(zone_classification,city,state):
    z_url = 'https://library.municode.com/ok/tulsa/codes/code_of_ordinances?nodeId=CD_ORD_TIT42ZOCO_CH5REDI_S5.010DI'
    z_category = 'Single Family Residential'
    z_classification = zone_classification
    z_far = 0.75
    z_lot_coverage = 75
    z_building_height = 35
    z_front_setback = 25
    z_rear_setback = 20
    z_side_setback = 5
    z_lot_size = 6900
    z_frontage = 60
    z_depth = 100
    z_parking_capacity = 2
    z_state = state
    z_city = city
    z_structure_type= 'Detached House'
    z_land_use= 'Land Use'

    zoneObj = ZoneInfo(z_url,z_category,z_classification,z_far,z_lot_coverage,\
                       z_building_height,z_front_setback,z_rear_setback,z_side_setback,\
                       z_lot_size,z_frontage,z_depth,z_parking_capacity,\
                       z_state,z_city,z_structure_type,z_land_use)
    return zoneObj

def getZoningInfoFromLLM(state,city,zone_classification):

    zoning_data = None
    if(city.upper()=='ATLANTA'):
        # pickle.load(open('./cost_model/state_wise_models/prediction_model_'+str(model_id)+'.sav', 'rb'))
        zoning_file = open('./ml_models/data/zoning_files/atlanta_R4.json')
        zoning_data = json.load(zoning_file)

    if(zoning_data == None):
        return False
    
    z_url = zoning_data[0]['minimum_frontage']['source']
    z_category = 'Single Family Residential'
    z_classification = zoning_data[0]['zoning_code']
    z_far = zoning_data[0]['maximum_floor_area_ratio']['value']
    z_lot_coverage = zoning_data[0]['maximum_lot_coverage']['value']
    z_building_height = 35
    z_front_setback = zoning_data[0]['minimum_front_setback']['value']
    z_rear_setback = zoning_data[0]['minimum_rear_setback']['value']
    z_side_setback = zoning_data[0]['minimum_side_setback']['value']
    z_lot_size = zoning_data[0]['minimum_lot_size']['value']
    z_frontage = zoning_data[0]['minimum_frontage']['value']
    z_depth = 100
    z_parking_capacity = 2
    z_state = zoning_data[0]['minimum_lot_size']['value']
    z_city = zoning_data[0]['minimum_lot_size']['value']
    z_structure_type= 'Duplex'
    z_land_use= 'Land Use'

    zoneObj = ZoneInfo(z_url,z_category,z_classification,z_far,z_lot_coverage,\
                       z_building_height,z_front_setback,z_rear_setback,z_side_setback,\
                       z_lot_size,z_frontage,z_depth,z_parking_capacity,\
                       z_state,z_city,z_structure_type,z_land_use)
    return zoneObj

def getSideSetback(original_polygon, city, zoning_document, cityZoningMap):
    side_setback = 0
    try:
        is_corner = isCorner(Polygon(original_polygon))
        if city == 'Tulsa':
            side_setback = zoning_document[cityZoningMap['side_setback']]['value']
        elif city == 'Oklahoma City':
            if 'value' in zoning_document[cityZoningMap['side_setback']]:
                side_setback = zoning_document[cityZoningMap['side_setback']]['value']
            else:
                if is_corner and 'Corner Side Yards' in zoning_document[cityZoningMap['side_setback']]:
                    side_setback = zoning_document[cityZoningMap['side_setback']]['Corner Side Yards']['value']
                elif not is_corner and 'Interior Side Yards' in zoning_document[cityZoningMap['side_setback']]:
                    side_setback = zoning_document[cityZoningMap['side_setback']]['Interior Side Yards']['value']
        return side_setback
    except Exception as e:
        return 10 # fix this


def getMaximumBuildableArea(city, city_zoning_map, areas, zoning_document):
    max_coverage_area = 0
    if city == 'Tulsa':
        max_coverage_area = areas[0] - zoning_document[city_zoning_map['max_coverage_area'][0]]['value'] if areas else None
    elif city == 'Oklahoma City':
        common_open_space = 0
        if city_zoning_map['max_coverage_area'][1] in zoning_document:
            common_open_space = zoning_document[city_zoning_map['max_coverage_area'][1]]['value']
        max_lot_coverage = 0
        max_lot_coverage_dict = {}
        if city_zoning_map['max_coverage_area'][0] in zoning_document:
            max_lot_coverage_dict = zoning_document[city_zoning_map['max_coverage_area'][0]]
        if common_open_space:
            max_coverage_area = (1 - common_open_space/100) * areas[0] if areas else None
        elif max_lot_coverage_dict:
            if 'value' in max_lot_coverage_dict:
                max_lot_coverage = max_lot_coverage_dict['value']
            else:
                max_lot_coverage = max_lot_coverage_dict['residential_use']['value']
            max_coverage_area = max_lot_coverage/100 * areas[0] if areas else None
    max_buildable_area = min(areas[1], max_coverage_area) if areas else None
    return {'max_coverage_area': max_coverage_area, 'max_buildable_area': max_buildable_area}


def processZoningDataResponse(city, original_polygon_with_latlng, areas, open_area, sides, final_polygon, zoning, report_id = None, user = None, max_buildable_area = {}, original_sides = []):
    depth = '-'
    original_depth = '-'
    if sides:
        if (len(sides[2])):
            depth = min(sides[2][0],sides[2][1])
        else:
            depth = '-'
    if original_sides:
        if (len(original_sides[2])):
            original_depth = min(original_sides[2][0], original_sides[2][1])
        else:
            original_depth = '-'
    data = {
        'city': city,
        'parcel': {
            'longitude': original_polygon_with_latlng['coords']['lng'], 
            'latitude': original_polygon_with_latlng['coords']['lat'],
            'parcel_area': areas[0] if areas else '-',
            'maximum_footprint_area': areas[1] if areas else '-',
            'minimum_setback_area': (areas[0] - areas[1]) if areas else '-',
            'mnimum_open_space_area': open_area,
            # 'maximum_buildable_area_v0': (areas[1] - max(0, open_area - areas[2])) if areas else '-', # buildable = inner_area - max(0, open_area - (outer_area - inner_area))
            'maximum_buildable_area': max_buildable_area.get('max_buildable_area'),
            'maximum_coverage_area': max_buildable_area.get('max_coverage_area'),
            'max_foundation_width': min(sides[0],sides[1]) if sides else '-',
            'max_foundation_depth': depth,
            'lot_width': min(original_sides[0], original_sides[1]) if original_sides else '-',
            'lot_depth': original_depth
            }, 
        'map': {
            'parcel_polygon': original_polygon_with_latlng['polygon'], 
            'setback_polygon': final_polygon
            },
        'zoning': zoning
        }
    parcel = getParcelInformation(original_polygon_with_latlng['coords']['lng'], original_polygon_with_latlng['coords']['lat'])
    data['parcel'].update(parcel)
    if report_id:
        report = Report.objects.get(id=report_id, user=user)
        report.zoning = data
        report.save()
    return data
    
def processZoningData(city, cityZoningMap, zoning_document, zoning_code, front_setback, rear_setback, side_setback):
    residential_data = {}

    if city == 'Tulsa':
        for main_key, main_value in zoning_document[cityZoningMap['residential_data']].items():
            residential_data[main_key] = {
                'permit_type': main_value.get('permit_type')
            }
            
            if main_value.get('minimum_lot_area'):
                residential_data[main_key]['minimum_lot_area'] = f"{main_value['minimum_lot_area']['value']} sqft"
            if main_value.get('minimum_lot_area_per_unit'):
                residential_data[main_key]['minimum_lot_area_per_unit'] = f"{main_value['minimum_lot_area_per_unit']['value']} sqft"
            if main_value.get('minimum_lot_width'):
                residential_data[main_key]['minimum_lot_width'] = f"{main_value['minimum_lot_width']['value']} ft"
            
            if 'building_type' in main_value:
                residential_data[main_key]['building_type'] = {}
                for bld_key, bld_value in main_value['building_type'].items():
                    residential_data[main_key]['building_type'][bld_key] = {
                        k: f"{v['value']} {'sqft' if v['unit'] == 'square feet' else 'ft'}" for k, v in bld_value.items() if 'value' in v and 'unit' in v
                    }
                    residential_data[main_key]['building_type'][bld_key]['permit_type'] = bld_value.get('permit_type')
    
    elif city == 'Oklahoma City':
        residential_data['district_use_regulations'] = {'building_type': {}}
        for main_key, main_value in zoning_document[cityZoningMap['residential_data']].items():
            if main_key == 'values':
                for bld_key, bld_value in main_value.items():
                    residential_data['district_use_regulations']['building_type'][bld_key] = {
                        'permit_type': bld_value['permit_type'] 
                    }
    maximum_building_height = 0
    if 'value' in zoning_document[cityZoningMap['max_building_height']]:
        maximum_building_height = zoning_document[cityZoningMap['max_building_height']]['value']
    elif 'standard' in zoning_document[cityZoningMap['max_building_height']]:
        maximum_building_height = zoning_document[cityZoningMap['max_building_height']]['standard']['value']
    else: 
        maximum_building_height = 35 # fix this
    zoning = {
                'zoning_code': zoning_code,
                'reference': zoning_document[cityZoningMap['reference']]['source'],
                'front_setback': f"{front_setback} ft",
                'side_setback': f"{side_setback} ft",
                'rear_setback': f"{rear_setback} ft",
                'max_building_height': maximum_building_height,
                'structure_types': residential_data
            }
    
    for misc_key in cityZoningMap['misc']:
        misc_value = zoning_document.get(misc_key)
        if misc_value:
            if 'value' in misc_value:
                zoning[misc_key] = f"{misc_value['value']} {misc_value.get('unit', '')}".strip()
            else:
                inner_values = {}
                for key, value in misc_value.items():
                    if not (key == 'name' or key == 'source'):
                        inner_values[key] = f"{value['value']} {value.get('unit', '')}".strip()
                zoning[misc_key] = inner_values
    return zoning

def getCityZoningMap(city):
    cityZoneMap = {
        'Tulsa': {
            'front_setback': 'minimum_arterial_street_setback',
            'side_setback': 'minimum_interior_side_setback',
            'rear_setback': 'minimum_rear_setback',
            'max_building_height': 'maximum_building_height',
            'reference': 'minimum_arterial_street_setback', # from source key inside this
            'misc': ['minimum_street_frontage', 'minimum_other_street_setback'],
            'residential_data': 'residential',
            'max_coverage_area': ['minimum_open_space_per_unit'],
        },
        'Oklahoma City': {
            'front_setback': 'front_yard',
            'side_setback': 'side_yard',
            'rear_setback': 'rear_yard',
            'max_building_height': 'maximum_height',
            'reference': 'front_yard', #from source key inside it
            'misc': ['minimum_lot_size', 'minimum_lot_width', 'density'],
            'residential_data': 'district_use_regulations',
            'max_coverage_area': ['maximum_lot_coverage', 'common_open_space'],
        }
    }
    return cityZoneMap[city]

def applyZoningRules(request, address, original_polygon_with_latlng = None, zoning_code = None):
    mongodb_path = settings.MONGODB_URL
    dbclient = pymongo.MongoClient(mongodb_path)
    iqlandDB = dbclient["IQLAND"]
    zoning_collection = iqlandDB["Zoning"]
    address = processAddress(request, address)
    city, state = address['city'], address['full_state']
    if not original_polygon_with_latlng:
        original_polygon_with_latlng = {'polygon': [], 'coords': {'lat': 0, 'lng': 0}}
        original_polygon_with_latlng = getPolygon(address['lat'], address['lng'])
        if not original_polygon_with_latlng:
            return None
    if not zoning_code:
        zoning_code = getZoningCode(original_polygon_with_latlng['polygon'])
    zoning_document = zoning_collection.find_one({"zoning_code_gis": {"$in": [zoning_code]}, "city": city, "state": state})
    if not zoning_document:
        return None
    cityZoningMap = getCityZoningMap(city)
    front_setback = zoning_document[cityZoningMap['front_setback']]['value']
    side_setback = getSideSetback(original_polygon_with_latlng['polygon'], city, zoning_document, cityZoningMap)
    rear_setback = zoning_document[cityZoningMap['rear_setback']]['value']
    setbackPolygonData = getSetbackPolygon(address['full_address'], original_polygon_with_latlng['polygon'], front_setback, rear_setback, side_setback)
    if not setbackPolygonData:
        return None
    final_polygon, sides, areas, original_sides = setbackPolygonData
    final_polygon = polygonToCoordinatesList(final_polygon)
    max_buildable_area = getMaximumBuildableArea(city, cityZoningMap, areas, zoning_document)
    depth = 0
    if sides:
        if (len(sides[2])):
            depth = min(sides[2][0],sides[2][1])
        else:
            depth = 0
    width = min(sides[0],sides[1]) if sides else 0
    return {'depth': depth, 'width': width, 'area': max_buildable_area['max_buildable_area'], 'final_polygon': final_polygon, 'original_polygon': original_polygon_with_latlng['polygon']}