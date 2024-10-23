import json
import pymongo
from django.conf import settings
from ml_models.models.embeddings import mixedbread_embeddings
from cost_estimation.helpers import predictConstructionCostFromModel, calculateTotalConstructionCost
from chatbot.response.textual_response import final_response, get_sources_list, remove_source_links
from zoning.gis.common_functions import polygonToCoordinatesList
from zoning.gis.setback_calculations import getSetbackPolygon
from zoning.helpers import processZoningData, processZoningDataResponse, getCityZoningMap, getMaximumBuildableArea, getSideSetback
from architectural_plans.helpers import getArchitecturalPlans, getArchitecturalPlansV2
from ml_models.models.llm import text_generation
from zoning.helpers import applyZoningRules
from cost_estimation.helpers import maximizeROI
from cost_estimation.helpers import getPropertyInfo
from architectural_plans.models import ArchitecturalPlan

mongodb_path = settings.MONGODB_URL
dbclient = pymongo.MongoClient(mongodb_path)
iqlandDB = dbclient["IQLAND"]
vectors_collection = iqlandDB["Zoning_vectors"]
zoning_collection = iqlandDB["Zoning"]

# ZONING
def process_zoning(json_response):
    # fetch relevant results from DB:
    json_response['results'] = query_db(json_response)
    json_response['sources'] = get_sources_list(json_response['results'])
    remove_source_links(json_response['results'])

    # generate final response
    llm_response = final_response(json_response)
    return llm_response

def get_nested_subset(zoning_code, city, state, path):
    """
    get nested subset of document in MongoDB given an identified path after vector search.

    input:
            zoning_code (string) for filtering on the relevant document in mongoDB.
            city (string) for filtering on the relevant document in mongoDB.
            state (string) for filtering on the relevant document in mongoDB.
            path (string) identified path to retrieve the document subset in mongoDB.

    output:
            document (dict) result subset of the mongoDB query for the given path.
    
    """
    # Construct the query based on zoning_code, city, and state
    query = {"zoning_code_gis": {"$in": [zoning_code]}, "city": city, "state": state} #FIX!!!!

    # Split the path into its components
    path_components = path.split('.')

    # Initialize the projection dictionary to project only the desired subset
    projection = {}
    nested_projection = projection
    for component in path_components[:-1]:
        nested_projection[component] = {}
        nested_projection = nested_projection[component]
    nested_projection[path_components[-1]] = 1


    # Query the document using the constructed query and projection
    document = zoning_collection.find_one(query, projection)

    if document:
        del document['_id']

    return document

def query_db(json_response):
    '''
    retrieves information from DB based on user prompt.

    input: 
            json_response (dict) representing user prompt in structured format.

    output:
            query results as a dict or list of dict
    
    '''
    results = []
    for concept in json_response['concepts_of_interest']:
        concept_results = {"user intent": concept}
        query = mixedbread_embeddings({"inputs":concept})
        while len(query)<1024:
            import time
            time.sleep(2)
            query = mixedbread_embeddings({"inputs":concept})


        pipeline = [
            {
              "$vectorSearch": {
                "index": "zoning_vectors_index",
                "path": "embeddings",
                'filter': {
                  'zoning_code': {'$eq': json_response['zoning_code']},
                },
                "queryVector": query,
                "numCandidates": 100,
                "limit": 4
              }
              }, {
                  '$project': {
                    "city": 1,
                    "county": 1,
                    "state": 1,
                    "zoning_code": 1,
                    "zoning_name": 1,
                    "path":1,
                    'score': {
                      '$meta': 'vectorSearchScore'
                    }
                  }
            }
          ]

        vector_search = vectors_collection.aggregate(pipeline)

        paths = ["zoning_code","zoning_name"]+[el['path'] for el in vector_search]

        retrieved_info = []
        for path in paths:
            subset = get_nested_subset(json_response['zoning_code'], json_response['city'], json_response['state'], path)
            if len(str(retrieved_info))+len(str(subset))< 3000:
                retrieved_info.append(subset)
        concept_results['official information'] = retrieved_info
        results.append(concept_results)

    return results

# ALLOWED STRUCTURES
def process_allowed_structures(json_response):
    llm_response = ''
    permit_type_path = {
        'Tulsa': 'residential',
        'Oklahoma City': 'district_use_regulations'
    }
    json_response['results'] = get_nested_subset(json_response['zoning_code'], json_response['city'], json_response['state'], permit_type_path[json_response['city']])
    llm_response = final_response(json_response)
    return llm_response

# PLAN RECOMMENDATION
def process_plan_recommendation(request, json_response, original_polygon):
    llm_response = ''
    if (json_response.get('min_total_area', 'NA') == 'NA' or json_response.get('max_total_area', 'NA') == 'NA' or json_response.get('stories', 'NA') == 'NA'):
        llm_response =  "To help us recommend the best plans, could you please fill out the following information?"
    else:
        architectural_plans = filter_architectural_plans(request, json_response, original_polygon)
        llm_response = f"Here are the recommended architectural plans for {json_response['address']}, based on the conditions provided."
        json_response['plans'] = architectural_plans['plans']
        json_response['remaining_plans_query'] = architectural_plans['query']
    return llm_response

def filter_architectural_plans(request, json_response, original_polygon):
    user_prompt = json_response['user_prompt']
    plan_components = identify_components_from_plans_prompt(user_prompt)
    architectural_style = plan_components.get('architectural_style', None)
    min_depth = plan_components.get('min_depth', 10)
    max_depth = plan_components.get('max_depth', 100)
    min_width = plan_components.get('min_width', 10)
    max_width = plan_components.get('max_width', 100)
    min_total_area = plan_components.get('min_total_area', 10)
    max_total_area = plan_components.get('max_total_area', 10000)
    min_height = plan_components.get('min_height', 10)
    max_height = plan_components.get('max_height', 100)
    stories = plan_components.get('stories', [1, 2, 3])
    cars_capacity = plan_components.get('cars_capacity', [1, 2, 3])
    foundation = plan_components.get('foundation', None)
    exterior_wall_type = plan_components.get('exterior_wall_type', None)
    garage_type = plan_components.get('garage_type', ["Attached", "Detached", "Carport", "Drive Under", "RV Garage", "None"])
    units = plan_components.get('units', ["Single Family", "Duplex", "Multi Family", "Other"])
    bedrooms = plan_components.get('bedrooms', ['1+'])
    bathrooms = plan_components.get('bathrooms', ['1+'])

    # data = getArchitecturalPlans(request, json_response['address'], architectural_style, min_total_area, max_total_area, min_width, max_width, min_height, max_height, min_depth, max_depth, stories, cars_capacity, foundation, exterior_wall_type, garage_type, units, bedrooms, bathrooms, None, None, None, original_polygon, json_response['zoning_code'])
    data = getArchitecturalPlansV2(request, json_response['address'], architectural_style, min_total_area, max_total_area, min_width, max_width, min_height, max_height, min_depth, max_depth, stories, cars_capacity, foundation, exterior_wall_type, garage_type, units, bedrooms, bathrooms, None, None, None, original_polygon, json_response['zoning_code'], 1, 25, True)
    query = {
        'address': json_response['address'], 'architectural_style':architectural_style, 'area_total_min': min_total_area,
        'area_total_max': max_total_area, 'width_min': min_width, 'width_max': max_width, 'height_min': min_height,
        'height_max': max_height, 'depth_min': min_depth, 'depth_max': max_depth, 'stories': stories, 'cars_capacity': cars_capacity,
        'foundation': foundation, 'exterior_wall_type': exterior_wall_type, 'garage_type': garage_type, 'units': units, 'bedrooms': bedrooms, 
        'bathrooms': bathrooms, 'page_number':1, 'per_page': 25, 'total_pages': data['total_pages'], 'total_items': data['total_items']
        }
    return {'query': query, 'plans': data['plans']}

def identify_components_from_plans_prompt(text):
    prompt = f"""
            Extract the min depth, max depth, min width, max width, min total area, max total area, architectural style, min height, 
            max height, stories, cars capacity, foundation, exterior wall type, garage type, units, bedrooms, bathrooms from the text.\
            Min depth should be a number only, max depth should be a number only, min width should be a number only, max width should be a number only, 
            min total area should be a number only, max total area should be a number only, min height should be a number only, max height should be a number only,
            stories should be an array of numbers only, cars capacity should be an array of numbers only, bedrooms should be array of strings like '1' or '2' or '3' or '4+' etc, 
            bathrooms should be an array of strings like '1' or '2' or '3' or '4+' etc, architectutal style should be an array of strings, foundation should be an array of strings, exterior wall type should be an array of strings, garage type 
            should be an array of strings, units should be an array of strings. Fill any missing values with None. Formulate response in JSON format with following keys:

            - "min_depth"
            - "max_depth"
            - "min_width"
            - "max_width"
            - "min_total_area"
            - "max_total_area"
            - "architectural_style"
            - "min_height"
            - "max_height"
            - "stories"
            - "cars_capacity"
            - "foundation"
            - "exterior_wall_type"
            - "garage_type"
            - "units"
            - "bedrooms"
            - "bathrooms"

            Text: "{text}"
            """
    
    chat_messages = [{"role": 'system', "content": prompt}, {"role": 'user', "content": "{text}"}]
    message_variables = {"text":text}
    results = text_generation(chat_messages, message_variables)

    try:
        results = json.loads(results)
    except:
        results = {}

    return results

# OPTIMIZE ROI
def process_optimize_roi(request, original_polygon_with_latlng, json_response):
    try:
        zoning_rules = applyZoningRules(request, json_response['address'], original_polygon_with_latlng, json_response['zoning_code'])
        property = getPropertyInfo(json_response['address'], json_response['street_address'], json_response['city'], json_response['state'])
        land_acquisition_cost = 0 if property == None else property['land_acquisition_cost']
        state = json_response.get('state_short','OK')
        county = json_response.get('county','TULSA')
        county = county.upper() if county else county
        county = county.replace('COUNTY', '').strip()
        response = maximizeROI(json_response['street_address'], json_response['city'], county, state, zoning_rules['width'], zoning_rules['depth'], None, zoning_rules['area'], land_acquisition_cost)
        architectural_plans = ArchitecturalPlan.objects.filter(plan_number=response['plan_number'])
        plans_data = list(architectural_plans.values())
        response['plans'] = plans_data
        json_response['results'] = response
        json_response['plans'] = plans_data
        llm_response = final_response(json_response)
        return llm_response
    except Exception as e:
        print(e)
        return f"Could not find the architectural plans that will give the maximum ROI on {json_response['address']}"

# COST ESTIMATION
def process_cost_estimation(json_response):
    llm_response = ''
    if json_response.get('building_area','NA') == 'NA' or json_response.get('building_quality','NA') == 'NA':
        llm_response =  "To help us provide a more accurate cost estimation, could you please fill out the following information?"
    else:
        json_response['results'] = cost_estimation_inference(json_response)
        llm_response = final_response(json_response)
    return llm_response

def identify_components_from_cost_prompt(text):
  '''
  Function gives individual item values used in construction cost computation
 
    Parameters
    ----------
    text : string (user prompt asking for construction cost)
 
    Returns
    -------
    results : dict
        a dictionary containing individual components and their values used in construction cost estimation.
  '''
  prompt = f"""
    Extract the building area, basement area, garage area, story count, build quality, basement quality from the text.\
    Building area should be a number only, basement area be a number only, garage area should be a number and story count\
    shuld be a number. Fill any missing values with None.  Formulate response in JSON format with following keys:

    - "building_area"
    - "basement_area"
    - "garage_area"
    - "story_count"
    - "build_quality"
    - "basement_quality"

    Text: "{text}"
    """
  
  chat_messages = [{"role": 'system', "content": prompt}, {"role": 'user', "content": "{text}"}]
  message_variables = {"text":text}
  results = text_generation(chat_messages, message_variables)

  try:
    results = json.loads(results)
  except:
    results = {}

  return results

def cost_estimation_inference(json_response):
    """
    computes construction costs for a given parcel
    
    inputs:
        json_response (dict) containing "state","county","building_quality","story count", "building area"

    outputs:
        dictionary with total cost and cost per sqft

    """
    user_prompt = json_response['user_prompt']
    cost_components = identify_components_from_cost_prompt(user_prompt)
    q_state = json_response.get('state_short','OK')
    q_county = json_response.get('county','TULSA')
    q_county = q_county.upper() if q_county else q_county
    q_county = q_county.replace('COUNTY', '').strip()
    area = json_response.get('building_area')
    if area is None:
       return {"Total construction cost": 0,"Construction cost per square feet":0}

    quality = cost_components.get('build_quality','BRONZE')
    if quality is None:
       quality = 'BRONZE'
    
    story_count = cost_components.get('story_count',1)
    if story_count is None:
       story_count = 1

    garage_area = cost_components.get('garage_area',0)
    if garage_area is None:
       garage_area = 0
    
    basement_area = cost_components.get('basement_area',0)
    if basement_area is None:
       basement_area = 0

    basement_quality = cost_components.get('basement_quality','NO')
    basement_quality = basement_quality.upper() if basement_quality else basement_quality
    if basement_quality is None:
       basement_quality = 'NO'
    
    q_quality =  json_response.get('building_quality','bronze') # 'bronze', 'silver', 'gold'
    q_story_count = json_response.get('story_count', 1) # must be number
    q_basement_type = json_response.get('basement_type','no') # unfinished finished
    q_area = json_response.get('building_area', 15000) #must be number 
    q_area_basement = json_response.get('basement_area', 0) #must be number
    q_area_garage = json_response.get('garage_area', 0) #must be number
    sq_ft_cost = predictConstructionCostFromModel(q_state,q_county,area,quality,story_count,basement_quality)
    total_cost = calculateTotalConstructionCost(q_state,sq_ft_cost,q_area,build_quality=quality,basement_type=basement_quality,area_garage=garage_area,area_basement=basement_area)
    return {"Total construction cost": total_cost,"Construction cost per square feet":sq_ft_cost}

# PARCEL INFO
def process_parcel_info(original_polygon_with_latlng, json_response):
    city, address, state, zoning_code = json_response.get('city'), json_response.get('address'), json_response.get('state'), json_response.get('zoning_code')
    zoning_document = zoning_collection.find_one({"zoning_code_gis": {"$in": [zoning_code]}, "city": city, "state": state})
    if not zoning_document:
        data = processZoningDataResponse(city, original_polygon_with_latlng, None, '-', None, [], {'zoning_code': zoning_code})
        return parcel_info_response(data, json_response)
    cityZoningMap = getCityZoningMap(city)
    front_setback = zoning_document[cityZoningMap['front_setback']]['value']
    side_setback = getSideSetback(original_polygon_with_latlng['polygon'], city, zoning_document, cityZoningMap)
    rear_setback = zoning_document[cityZoningMap['rear_setback']]['value']
    setbackPolygonData = getSetbackPolygon(address, original_polygon_with_latlng['polygon'], front_setback, rear_setback, side_setback)
    zoning = processZoningData(city, cityZoningMap, zoning_document, zoning_code, front_setback, rear_setback, side_setback)
    if not setbackPolygonData:
        data = processZoningDataResponse(city, original_polygon_with_latlng, None, '-', None, [], zoning)
        return parcel_info_response(data, json_response)
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
    data = processZoningDataResponse(city, original_polygon_with_latlng, areas, open_area, sides, final_polygon, zoning, None, None, max_buildable_area, original_sides)
    return parcel_info_response(data, json_response)

def parcel_info_response(data, json_response):
    llm_response = ''
    if data:
      del data['zoning']
    json_response['results'] = data['parcel']
    json_response['map'] = data['map']
    llm_response = final_response(json_response)
    return llm_response