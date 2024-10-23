import psycopg2
from zoning.models import GISZoning
from django.contrib.gis.geos import GEOSGeometry

def formatPolygonToWkt(polygon):
    """
    Convert a list of coordinates into a WKT MultiPolygon string.
    
    Parameters:
        polygon (list): List of coordinates, where each coordinate is a list of [longitude, latitude].
    
    Returns:
        str: WKT string for the MultiPolygon.
    """
    # Convert coordinates to WKT format
    wkt_coordinates = ', '.join([f"{coord[0]} {coord[1]}" for coord in polygon])
    wkt_multipolygon = f"MULTIPOLYGON((({wkt_coordinates})))"
    return wkt_multipolygon

def query_database(polygon_wkt, database, user, password, host="localhost", port=5432):
    """
    Returns the zoning information for the polygon. It querries the data in postgres database
    
    Parameters:
        polygon_wkt (wkt_string): Coordinates of the polygon in a wkt strinf format
        database, user, password, host, port (string): Connection parameters of the DB
    
    Returns:
        list: List of the returned data from the DB - [(zoning_code, zoning_description)].
    """
    sql_query = f"SELECT zone_type, zoning_desc FROM zoning_giszoning WHERE ST_Intersects(zoning_giszoning.geom,ST_GeomFromText('{polygon_wkt}', 4326));"

    try:
        # Connect to the database
        connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )

        # Create a cursor object
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(sql_query)

        # Fetch all the results
        rows = cursor.fetchall()

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return rows

def getZoningCode(polygon):
    try:
        polygon_wkt = formatPolygonToWkt(polygon)
        polygon_geom = GEOSGeometry(polygon_wkt, srid=4326)
        zoning_object = GISZoning.objects.filter(geom__intersects=polygon_geom).first()

        if zoning_object:
            return zoning_object.zone_type
        else:
            return None

    except Exception:
        return None

# Set up database connection parameters
# dbname = "iqlandaitestdb"
# user = "root"
# password = "vit9trUpRe9owu6utrlb"
# host = "iqlandaitest.c4xxgddnabze.us-east-1.rds.amazonaws.com"

# Sample polyon, you can get this from the script GetPolygonFromAddress.py and use the resultant polygon as it is from the dict
# polygon = [[-95.95162162121287, 36.14513534755209],
#   [-95.95162107182502, 36.1452693314356],
#   [-95.95162101419497, 36.145283337363004],
#   [-95.95209962406098, 36.14528525986764],
#   [-95.95209966383572, 36.14527180893638],
#   [-95.95209987404088, 36.145199802868696],
#   [-95.95210006316589, 36.14513548680968],
#   [-95.95162162121287, 36.14513534755209]]
# Convert the polygons coordinates to the required format, wkt string
# polygon_wkt = formatPolygonToWkt(polygon)

# Call the function to execute the query
# zoning_info = query_database(polygon_wkt, dbname, user, password, host)
# print (zoning_info)