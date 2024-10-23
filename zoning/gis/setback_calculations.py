import requests
import numpy as np
from fuzzywuzzy import fuzz
from geographiclib.geodesic import Geodesic
from shapely.ops import unary_union, linemerge
from shapely.geometry import Polygon, LineString, MultiLineString
from .common_functions import shapely_to_arcgis, reprojectParcel

def is_almost_parallel(line1, line2, tolerance=50.0):
    def direction_vector(line):
        # Get the direction vector of the line (end point - start point)
        x, y = line.coords[0], line.coords[-1]
        return np.array([y[0] - x[0], y[1] - x[1]])

    # Get direction vectors for both lines
    v1 = direction_vector(line1)
    v2 = direction_vector(line2)

    # Normalize the direction vectors
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)

    # Compute the dot product
    dot_product = np.dot(v1, v2)

    # Calculate the angle between the vectors
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))

    # Convert the angle to degrees
    angle_degrees = np.degrees(angle)

    # Check if the angle is close to 0 or 180 degrees within the given tolerance
    return np.isclose(angle_degrees, 0, atol=tolerance) or np.isclose(angle_degrees, 180, atol=tolerance)

def identifyRear(frontage, other_sides):
    rears = []
    sides = []
    for i in range(len(other_sides)):
        cur_line = other_sides[i]
        
        if (is_almost_parallel(frontage, cur_line, tolerance=40.0)):
            rears.append(cur_line)
        else:
            sides.append(cur_line)
            
    multi_line_string = MultiLineString(rears)
    dissolved_rear = linemerge(multi_line_string)
    
    return dissolved_rear, sides
    
def calculateAreas(original_polygon, setback_polygon):
    org_area = (original_polygon.area) * 10.764
    sb_area = (setback_polygon.area) * 10.764
    
    open_area_poly = original_polygon.difference(setback_polygon)
    open_area = (open_area_poly.area) * 10.764
    
    return org_area, sb_area, open_area

# Function to calculate the setbacks and return the new polygon with setback
def calculateSetbacks(parcel, setback_front, setback_rear, setback_side, frontage, rear, other_sides):
    """
    Convert a Shapely polygon to an ArcGIS-compatible data structure.

    Parameters:
        parcel (shapely.geometry.Polygon): The Shapely polygon for setbacks.
        setback_front, setback_side, setback_rear (float): values of setbacks in feet
        frontages, other_sides(list of shapely linestring): list, each of which have the frontage and sides separated

    Returns:
        polygon (shapely polygon): Polygon geometry after the setback rules have been applied.
        side lengths (list): Length of each side(ft) after setback is applied - format of list = [front_length, rear_length, [list with lengths of sides]]
    """
    setback_front = setback_front * 0.3048
    setback_side = setback_side * 0.3048
    setback_rear = setback_rear * 0.3048
    
    frontage_buffered = frontage.buffer(setback_front)
    rear_buffered = rear.buffer(setback_rear)
    other_sides_buffered = [line.buffer(setback_side) for line in other_sides]
    
    buffered_sides = []
    buffered_sides.extend([frontage_buffered])
    buffered_sides.extend(other_sides_buffered)
    buffered_sides.extend([rear_buffered])
    
    buffered_polygon = parcel.difference(unary_union(buffered_sides))
    
    # Calculate the new lengths of the front, rear and sides after setback rules are applied
    front_len = (frontage.length - 2*setback_side)/0.3048
    front_len_org = (frontage.length)/0.3048
    rear_len = (rear.length - 2*setback_side)/0.3048
    rear_len_org = (rear.length)/0.3048
    # Since there are 2 sides, lengths of both sides are stored in a list
    side_lens = []
    side_lens_org = []
    for s in other_sides:
        side_lens.append((s.length - setback_front - setback_rear)/0.3048)
        side_lens_org.append((s.length)/0.3048)
    
    # See the documentation at the start of this function to understand the returned values
    return buffered_polygon, [front_len, rear_len, side_lens], [front_len_org, rear_len_org, side_lens_org]

def queryFeatures(url, geometry, street):
    """
    Query the road API to get the nearest road.

    Parameters:
        url (string): Base Url for the API endpoint.
        geometry(shapely polygon): The polygon of the parcel
        street (str): It is the street extracted from the address

    Returns:
        geometry of road (shapely linestring): The road closest to the polygon(assume it is on the frontage side).
        distance (integer): The distance at which the road is found
        
    Description:
        The function loops over fixed distances of step of 5 feet to find a road within that distance.
        The loop is important because the roads are not at a constant distance from the polygon everytime
        We cannot also give a bigger value because we risk getting roads which are far away, hence complicating our task
    """
    try:
        for i in range(10, 80, 10):
            data = ''
            geometry_poly = shapely_to_arcgis(geometry)

            params = {
                'timeRelation' : 'esriTimeRelationOverlaps',
                'geometry' : geometry_poly,
                'geometryType' : 'esriGeometryPolygon',
                'inSR' : 4326,
                'spatialRel' : 'esriSpatialRelIntersects',
                'distance' : i,
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

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                if len(data['features']) == 0:
                    continue
                
                else:
                    ind = ''
                    # Check if the name of returned street is that of the input one, uses fuzzy matching to match the names
                    for j, feat in enumerate(data['features']):
                        if fuzz.ratio(feat['properties']['NAME'].lower(), street.lower()) < 85:
                            continue
                        else:
                            # If the match is higher than 85, this means we found the street
                            ind = j
                            break
                            
                        
                    if ind != '':
                        data['features'] = [data['features'][ind]]
                        return data, i
            else:
                print("Error:", response.status_code)
                return None
    except Exception as e:
        print("Error:", e)
        return None
    
def getSetbackPolygon(address, poly, setback_front, setback_rear, setback_side):
    """
    Calculate the setbacks of the polygon.

    Parameters:
        address (str): The address of the input polygon in text. It should be complete address
        parcel (coordinates in a list): The Shapely polygon for setbacks.
        setback_front, setback_side, setback_rear (float): values of setbacks in feet

    Returns:
        polygon (shapely polygon): Polygon geometry after the setback rules have been applied and in epsg:4326.
        side lengths (list): Length of each side(ft) after setback is applied - format of list = [front_length, rear_length, [list with lengths of sides]]
    """
    # Extract street from the address. It is considered that address is int his format
    # <house num> <street>, Tulsa, OK, USA e.g. 8226 E 34TH ST, Tulsa, OK, USA ('E 34TH ST' is the street name in this)
    street = ' '.join(address.split(',')[0].split(' ')[1:])
    
    # Convert the polygon to shapely object
    original_polygon = Polygon(poly)
    
    # Get the features from the API call
    url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer/8/query?where="
    # features, max_distance = queryFeatures(url, original_polygon, street) # It also returns the max_distance which we use later
    queryFeaturesData = queryFeatures(url, original_polygon, street) # It also returns the max_distance which we use later
    if not queryFeaturesData:
        return None
    features, max_distance = queryFeaturesData
    # Extract the coordinates from the retuned geojson
    road = LineString(features['features'][0]['geometry']['coordinates'])
    # Reproject the parcel
    polygon_prj = reprojectParcel(original_polygon, ['EPSG:4326', 'EPSG:6350'])
    # Reproject the roads
    road_prj = reprojectParcel(road, ['EPSG:4326', 'EPSG:6350'])
    
    # Separate the polygon into separate sides and store in a list along with the midpoint and a bool value
    polygon_sides = [[LineString([polygon_prj.exterior.coords[i], polygon_prj.exterior.coords[i + 1]]),
                  LineString([polygon_prj.exterior.coords[i], polygon_prj.exterior.coords[i + 1]]).centroid,
                  False]  # Default value indicating midpoint not within distance
                 for i in range(len(polygon_prj.exterior.coords) - 1)]
    
    # Specify a max distance to check if midpoint is within this distance of the road (to identify frontage side)
    # Max distance is taken as the one returned by the query function, this way we have a proper value, instead of estimate
    # We add 5 to the max_distance because the frontage is sometimes made of more than one segments are they are sometime
    # a bit far away and are missed. To avoid this, we add 5 feet so they are included in the frontage identification
    max_distance = (max_distance + 15) * 0.3048

    # Loop over the sides to check which side is nearest to the road and then update the bool value to 'True'
    for i in range(len(polygon_sides)):
        if polygon_sides[i][1].distance(road_prj) <= max_distance:
            polygon_sides[i][2] = True
            
    # Now separate the sides into two list, one to carry frontages and the other to sides
    frontage = []
    other_sides = []
    for side, midpoint, is_within_distance in polygon_sides:
        if is_within_distance:
            frontage.append(side)
        else:
            other_sides.append(side)
    
    # Merge the frontage segments into one line
    multi_line_front = MultiLineString(frontage)
    frontage_side = linemerge(multi_line_front)

    # Identify the rear segment
    rear_side, sides = identifyRear(frontage_side, other_sides)

    multi_line_sides = MultiLineString(sides)
    
    sides_multi = linemerge(multi_line_sides)
    sides_lines = list(sides_multi.geoms)

    poly_sides = []
    for line in sides_lines:
        poly_sides.append(line)
        
    # Define the setback values and then calculate the setbacks
    setback_polygon, setback_lens, org_lens = calculateSetbacks(polygon_prj, setback_front, setback_rear, setback_side, frontage_side, rear_side, poly_sides)

    # Reproject the parcel back to 4326
    final_polygon = reprojectParcel(setback_polygon, ['EPSG:6350', 'EPSG:4326'])
    
    # Calculate the areas
    org_a, sb_a, open_a = calculateAreas(polygon_prj, setback_polygon)
    
    return final_polygon, setback_lens, [org_a, sb_a, open_a], org_lens