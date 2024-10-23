import json
import pyproj
from shapely.ops import transform

# Function to reproject parcel from epsg:5326 to epsg:6350
def reprojectParcel(parcel, prjs):
    """
    Reprojects a polygon to a projected CRS, in our case from epsg:4326 to epsg:6350.

    Parameters:
        shapely_polygon (shapely.geometry.Polygon): The Shapely polygon to be reprojected.
        prjs (list): The list with the source CRS(at index 0) and target CRS(at index 1)

    Returns:
        shapely_polygon: Reprojected polygon.
    """
    wgs84 = pyproj.CRS(prjs[0])
    prj_6350 = pyproj.CRS(prjs[1])

    project = pyproj.Transformer.from_crs(wgs84, prj_6350, always_xy=True).transform
    prj_parcel = transform(project, parcel)
    
    return prj_parcel

# Function to convert the shapely geometry polygon to arcgis query rest api format 'rings'
def shapely_to_arcgis(shapely_polygon):
    """
    Convert a Shapely polygon to an ArcGIS-compatible data structure.

    Parameters:
        shapely_polygon (shapely.geometry.Polygon): The Shapely polygon to be converted.

    Returns:
        dict: An ArcGIS-compatible representation of the polygon.
    """
    rings = []
    exterior_coords = list(shapely_polygon.exterior.coords)
    rings.append([[coord[0], coord[1]] for coord in exterior_coords])
    for interior in shapely_polygon.interiors:
        interior_coords = list(interior.coords)
        rings.append([[coord[0], coord[1]] for coord in interior_coords])
    return json.dumps({"rings": rings})

def convertPolygonToWkt(polygon):
    points = [f"{point[0]} {point[1]}" for point in polygon]
    polygon_wkt = f"Polygon (({', '.join(points)}))"
    return polygon_wkt

def polygonToCoordinatesList(polygon):
    coordinates = [list(coord) for coord in polygon.exterior.coords]
    return coordinates