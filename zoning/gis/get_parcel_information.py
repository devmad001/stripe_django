import psycopg2
from IQbackend import settings

def getParcelInformation(x, y):
    """
    Returns the parcel for the polygon. It querries the data in postgres database
    
    Parameters:
        x, y (float): Coordinates of the point in x, y retrieved from geocoding API
        database, user, password, host, port (string): Connection parameters of the DB
    
    Returns:
        list: List of the returned data from the DB - [(geometry,)].
    """
    sql_query = f"SELECT parcel_num, account_type, owner_name1, owner_name2, owner_addr1, owner_addr2, owner_addr3, owner_addr4, owner_addr5 from parcels_gisparcels_new WHERE ST_Contains(parcels_gisparcels_new.geom,  ST_SetSRID(ST_Point({x}, {y}), 4326))"
    
    # DB credentials
    dbname = settings.DB_NAME
    user = settings.DB_USER
    password = settings.DB_PASSWORD
    host = settings.DB_HOST
    port = settings.DB_PORT

    try:
        # Connect to the database
        connection = psycopg2.connect(
            database=dbname,
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
        result = cursor.fetchone()
        data = {}
        if result:
            owner_address_fields = result[4:9]
            non_empty_fields = [field for field in owner_address_fields if field]
            owner_address = " ".join(non_empty_fields) if non_empty_fields else '-'
            data = {
                'parcel_id': result[0] if result[0] else '-',
                'property_type': result[1] if result[1] else '-',
                'owner_name': result[2] if result[2] else '-',
                'owner_address': owner_address
            }

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return data

def getParcelAddressFromId(parcel_id, city, county):
    """
    Returns the parcel address for the parcel id. It querries the data in postgres database
    
    Parameters:
        parcel_id, city, county
    
    Returns:
        Validated address from Google Address Validation
    """
    sql_query = f"SELECT city, parcel_num, prop_addr1, prop_addr2, county_name FROM parcels_gisparcels_new WHERE parcel_num = '{parcel_id}' AND LOWER(city) = LOWER('{city}') AND county_name LIKE '%{county}%'"
    result = None
    # DB credentials
    dbname = settings.DB_NAME
    user = settings.DB_USER
    password = settings.DB_PASSWORD
    host = settings.DB_HOST
    port = settings.DB_PORT

    try:
        # Connect to the database
        connection = psycopg2.connect(
            database=dbname,
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
        result = cursor.fetchone()
        if result:
            result = f'{result[2]} {result[3]} {result[0]} {result[4]}'

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return result