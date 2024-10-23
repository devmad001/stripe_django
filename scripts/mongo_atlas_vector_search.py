import pymongo
import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongodb_path = os.getenv('MONGODB_URL')

dbclient = pymongo.MongoClient(mongodb_path)
iqlandDB = dbclient["IQLAND"]
collection = iqlandDB["Zoning_vectors"]

API_URL = "https://api-inference.huggingface.co/models/mixedbread-ai/mxbai-embed-large-v1"
headers = {"Authorization": f"Bearer {os.getenv('HUGGING_FACE_TOKEN')}"}

def mixedbread_embeddings(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

query = mixedbread_embeddings({"inputs":"setbacks"})
print(len(query))

pipeline = [
            {
              "$vectorSearch": {
                "index": "zoning_vectors_index",
                "path": "embeddings",
                'filter': {
                  'zoning_code': {'$eq': 'RM-3'},
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

def remove_embeddings(data):
    '''
    removes embeddings from results

    '''
    if isinstance(data, dict):
        for key, value in data.copy().items():
            if key =="embeddings":
                del data['embeddings']
            elif isinstance(value, dict) :
                remove_embeddings(value)

    return data

# run pipeline
result = collection.aggregate(pipeline)

paths = [el['path'] for el in result]

# print results
print(paths)


collection2 = iqlandDB["Zoning"]

def get_nested_subset(zoning_code, city, state, path):
    # Construct the query based on zoning_code, city, and state
    query = {"zoning_code": zoning_code, "city": city, "state": state}

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
    document = collection2.find_one(query, projection)

    del document['_id']

    return document

# Example usage
zoning_code = "RM-3"  
city = "Tulsa"  
state = "Oklahoma"  

results = []
for path in paths:
  subset = get_nested_subset(zoning_code, city, state, path)
  if len(str(results))+len(str(subset))< 3000:
    results.append(subset)

print(len(results))
print(len(str(results)))
  