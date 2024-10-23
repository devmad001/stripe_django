import psycopg2
from shapely import wkb
from IQbackend import settings

def extract_coordinates(geometry):
    """
        Convert the wkb geometry format into a list of coordinates

        Parameters:
        geometry (wkb string): Polygon returned from the DB in a wkb_geometry format

        Return:
        coords(list): List of coordinates in a proper format
    """
    if geometry.geom_type == 'Polygon':
        return [list(coord) for coord in geometry.exterior.coords]
    elif geometry.geom_type == 'MultiPolygon':
        coords = []
        for polygon in geometry.geoms:
            coords.extend([list(coord) for coord in polygon.exterior.coords])
        return coords
    else:
        raise ValueError("Unsupported geometry type")

def query_database(x, y, database, user, password, host="localhost", port=5432):
    """
    Returns the parcel for the polygon. It querries the data in postgres database
    
    Parameters:
        x, y (float): Coordinates of the point in x, y retrieved from geocoding API
        database, user, password, host, port (string): Connection parameters of the DB
    
    Returns:
        list: List of the returned data from the DB - [(geometry,)].
    """
    sql_query = f"SELECT geom from parcels_gisparcels_new WHERE ST_Contains(parcels_gisparcels_new.geom,  ST_SetSRID(ST_Point({x}, {y}), 4326))"

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

def getPolygon(lat, lng):
    """
        Get the polygon from the address, it uses previous functions

        Parameters:
        lat (float): latitude of the parcel
        lng (float): longitude of the parcel
        
        Return:
        data (object): It includes the coordinates(lat/long) and the coordinates of the polygon
    """

    # DB credentials
    dbname = settings.DB_NAME
    user = settings.DB_USER
    password = settings.DB_PASSWORD
    host = settings.DB_HOST
    port = settings.DB_PORT

    # Query the database
    features = query_database(lng, lat, dbname, user, password, host, port)
    
    # Conver the wkb_geometry to list of coordinates
    if len(features) > 0:
        wkb_bytes = bytes.fromhex(features[0][0])
        output_geometry = wkb.loads(wkb_bytes)
        coordinates = extract_coordinates(output_geometry)
        formatted_coordinates = [[coord[0], coord[1]] for coord in coordinates]
    else:
        return None

    # Create the output dict to return the data in a structured way
    output_dict = {
        'coords': {'lat': lat, 'lng': lng},
        'polygon': formatted_coordinates
    }
    
    return output_dict