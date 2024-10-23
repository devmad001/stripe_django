import requests
from shapely.geometry import shape
from .common_functions import shapely_to_arcgis

def queryFeatures(url, geometry):
    """
    Query the road API to get the nearest road.

    Parameters:
        url (string): Base Url for the API endpoint.
        geometry(shapely polygon): The polygon of the parcel

    Returns:
        geometry of road (shapely linestring): The road closest to the polygon(assume it is on the frontage side).
        distance (integer): The distance at which the road is found
        
    Description:
        The function loops over fixed distances of step of 5 feet to find a road within that distance.
        The loop is important because the roads are not at a constant distance from the polygon everytime
        We cannot also give a bigger value because we risk getting roads which are far away, hence complicating our task
    """
    try:
        #for i in range(10, 60, 10):
        geometry_poly = shapely_to_arcgis(geometry)

        params = {
            'timeRelation' : 'esriTimeRelationOverlaps',
            'geometry' : geometry_poly,
            'geometryType' : 'esriGeometryPolygon',
            'inSR' : 4326,
            'spatialRel' : 'esriSpatialRelIntersects',
            'distance' : 100,
            'units' : 'esriSRUnit_Foot',
            'outFields' : '*',
            'returnGeometry' : 'true',
            'returnTrueCurves' : 'false',
            'outSR' : 4326,
            'returnIdsOnly' : 'false',
            'returnCountOnly' : 'false',
            'returnZ' : 'false',
            'returnM' : 'false',
            'returnDistinctValues' : 'false',
            'resultRecordCount' : 100,
            'returnExtentOnly' : 'false',
            'sqlFormat' : 'none',
            'featureEncoding' : 'esriDefault',
            'f' : 'geojson'
        }

        # Send GET request to the ArcGIS REST API
        response = requests.get(url, params=params)
        #response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            return data
        else:
            print("Error:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

def convert_geojson_to_shapely(geojson):
    features = geojson['features']
    geometries = [shape(feature['geometry']) for feature in features]
    return geometries

def check_intersections(geometries):
    for i in range(len(geometries)):
        for j in range(i + 1, len(geometries)):
            if geometries[i].intersects(geometries[j]):
                #print ('They intersect')
                return True
            
    return False

def removeDuplicates(features):
    # Load the GeoJSON file
    geojson_data = features

    # Specify the attribute to check for duplicates
    attribute = 'BASENAME'

    # Use a set to track unique attribute values
    unique_values = set()
    unique_features = []

    # Iterate through features and add only unique ones
    for feature in geojson_data['features']:
        attr_value = feature['properties'][attribute]
        if attr_value not in unique_values:
            unique_features.append(feature)
            unique_values.add(attr_value)

    # Replace the original features with the unique features
    geojson_data['features'] = unique_features

    return geojson_data

def isCorner(original_polygon):
    """
    Returns if a lot is corner or not.

    Parameters:
        original_polygon (shapely.geometry.Polygon): The Shapely polygon for lot.

    Returns:
        Corner or not (boolean): Returns True or False based on if the lot is corner or not.
    """
    # Get the features from the API call
    url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer/8/query?where="
    features = queryFeatures(url, original_polygon)

    if len(features['features']) > 1:
        features_new = removeDuplicates(features)
        geometries = convert_geojson_to_shapely(features_new)
        if check_intersections(geometries):
            return True
        else:
            return False
    else:
        return False