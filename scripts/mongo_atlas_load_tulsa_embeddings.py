import pymongo
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongodb_path = os.getenv('MONGODB_URL')

dbclient = pymongo.MongoClient(mongodb_path)
iqlandDB = dbclient["IQLAND"]
collection = iqlandDB["Zoning_vectors"]

zoning_path_files = "zoning_files/tulsa/with_embeddings/"

def load_json_file(file_path):
    '''
    loads a json file into a dict based on file path
    '''
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Retrieves all zoning codes json 
documents = []
for file in os.listdir(zoning_path_files):
    data = load_json_file(zoning_path_files+file)
    # documents.append(data)
    # Insert list of documents into MongoDB
    collection.insert_many(data) 
		
print("Data insertion complete.")


