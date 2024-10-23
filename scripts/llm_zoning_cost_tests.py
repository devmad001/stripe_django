from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser
import urllib.parse
import requests
import json
import pymongo
from fuzzywuzzy import fuzz
import pandas as pd
import pickle
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

mongodb_path =  os.getenv('MONGODB_URL')

dbclient = pymongo.MongoClient(mongodb_path)
iqlandDB = dbclient["IQLAND"]
vectors_collection = iqlandDB["Zoning_vectors"]
zoning_collection = iqlandDB["Zoning"]

#deployed cities:
DEPLOYED_CITIES = ['Tulsa']
llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)

# System prompt
system_initial_prompt = """
                You are a real estate expert able to understand user queries and extract the address from their prompt.

                Your task will be to extract the address, the type of request from the user as well as the concept of interest.

                In simple words, you need to reformulate the request in JSON format with three keys:
                - "address"
                - "request_type"
                - "concepts_of_interest"

                You need to identify the request_type, which must only be one of the following at all cost:
                {request_types}
                
                Always enclose the JSON code between [BEGIN] and [END] tags.
                
                A few examples:
                {example_user_prompts}

                It is important that your answers are accurate and that you strictly respect the required format. Take a deep breath, you can do it :) 
                """

request_types = """
                - "lot_subdivision", when the user wants to calculate a maximized parcel subdivision for a plot of land.
                - "zoning", when the user wants to get information about what is authorized on a parcel as per the regulation and land development code requirements.
                - "plan_recommendation", when the user wants suggestions of plans that could qualify for their parcel. 
                - "profitability", when the user wants to get advice on how to optimize profit out of a construction project on a given parcel.
                - "cost_estimation", when the query is about estimating the cost of a potential construction project.
                - "plan_compliance", when the user wants to upload a plan and pre-determine its legal compliance.
                - "other", any other type of request.
                ]
                """

example_user_prompts = """
                        Example input 1: "What is the lot coverage and the side yard setback for 2101 Verbena St Nw Atlanta, GA 30314 ?"

                        Example output 1: 
                        {{
                                "address": "2101 Verbena St Nw Atlanta, GA 30314",
                                "request_type": "zoning",
                                "concepts_of_interest": ["lot coverage", "side yard setback"]
                        }}

                        Example input 2: "I have a 25000 sq ft parcel, I'd like to estimate the cost of my project if it was a bronze quality level please help."
                        
                        Note: In case request_type is cost_estimation. We need to collect "building_area" and "building_quality". If missing, value is 'NA'.

                        Example output 2: 
                        {{
                                "address": "NA",
                                "request_type": "cost_estimation",
                                "concepts_of_interest": "cost",
                                "building_area": 25000,
                                "building_quality": "bronze"
                        }}

                        """

def get_user_request(input,llm):
    '''
    Fetches the user request in JSON format.

    Inputs:
            input (string) containing user request.
    Output:
            json format representation of user request    
    '''

    # Prepare System and Human messages for LLMChain
    chat_messages = [
                        ('system',system_initial_prompt),
                        ('human', "{input}")
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    chain =  prompt_template | llm | StrOutputParser()

    # Run LLM chain based on the entries
    results = chain.invoke({"input":input,"request_types": request_types, "example_user_prompts":example_user_prompts})

    return results

def extract_substring(input_string):
    '''
    Function to extract json component only.

    input: input_string (string), with LLM response to user.
    output: substring (string), trimming out the start and end tags.
    '''
    begin_index = input_string.find("[BEGIN]")
    end_index = input_string.find("[END]")

    # Check if both substrings are present
    if begin_index == -1 or end_index == -1 or end_index <= begin_index:
        return input_string  # Return the original string if conditions are not met

    # Extract the substring
    begin_index += len("[BEGIN]")
    substring = input_string[begin_index:end_index]

    return substring

def generate_json_response(input,llm,call):
    '''
    Function to generate the JSON response.

    input: input (string), contains the user request.
    output: json_response (dict), translation of the user prompt to json.  
    '''
    response = extract_substring(call(input,llm))
    try:
        json_response = json.loads(response)
        json_response['user_prompt'] = input

    except json.JSONDecodeError:
        json_response = {
                            "error_message": "Couldn't generate a valid JSON response for that input.",
                            "input": input,
                            "response": response
                        }
    return json_response

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
    query = {"zoning_code": zoning_code, "city": "Tulsa", "state": "Oklahoma"} #FIX!!!

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

    del document['_id']

    return document


def mixedbread_embeddings(payload):
    '''
    API call to the embedding model

    input:
        payload (dict) containing at least 'inputs' as key and a string as value.

    output:
        list of floats as the embedding representation of the input.
    
    '''
    API_URL = "https://api-inference.huggingface.co/models/mixedbread-ai/mxbai-embed-large-v1"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGING_FACE_TOKEN')}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

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

def process_address(address,llm):
    '''
    process_address for ATTOM call

    input:
            address (string) containing the addresss.
    
    output:
            llm_response (string), generated text from LLM.
    
    '''
    system_prompt = """
                            You are a real estate expert, specialized in land development topics.
                            Please reformat the address provided by the user in two parts as per the examples below.

                            Always enclose the JSON code between [BEGIN] and [END] tags.

                            Example input 1: "2998 Miriam Court Decatur GA"
                            Example output 1: 
                            {{
                                    "number_street": "2998 Miriam Court",
                                    "city_state": "Decatur GA"
                            }}

                            Example input 2: "2101 Verbena St Nw Atlanta, GA 30314"
                            Example output 2: 
                            {{
                                    "number_street": "2101 Verbena St Nw",
                                    "city_state": "Atlanta GA",
                                    "zipcode": "30314"
                            }}

                            Example input 3: "8226 E 34th St Tulsa, OK"
                            Example output 3: 
                            {{
                                    "number_street": "8226 E 34th St",
                                    "city_state": "Tulsa OK",
                            }}
                            
                            Always verify that street number, street name, city name, and state acronym (e.g. 'OK') are present. If any of them is missing, return {{"error_message":"missing info"}}

                            It is important that your answers are accurate and that you strictly respect the required format. Take a deep breath, you can do it :) 
                            """
        
    # Prepare System and Human messages for LLMChain
    chat_messages = [
                        ('system',system_prompt),
                        ('human', "{address}")
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    chain = prompt_template | llm | StrOutputParser()
    # Run LLM chain based on the entries
    llm_response = chain.invoke({address}) 

    return llm_response 


def call_attom_API(addrs_part1,addrs_part2):
    """
    Call ATTOM to retrieve property information based on address.

    inputs:
        addrs_part1 (string) with number and street name part of the address.
        addrs_part2 (string) with city and state acronym of the address.
    output:
        attom_resp_json (dict) with full response from attom
    
    """
    addrs_part1_uri = urllib.parse.quote(addrs_part1)
    addrs_part2_uri = urllib.parse.quote(addrs_part2)
    attom_url = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/expandedprofile?address1='+addrs_part1_uri+'&address2='+addrs_part2_uri+'&debug=True'
    headers = {'apikey': os.getenv('ATTOM_API_KEY'),'accept': "application/json", }
    attom_resp = requests.get(attom_url,headers=headers)
    attom_resp_json = attom_resp.json()

    return attom_resp_json

def is_address_valid(address):
    '''
    check if address is valid.

    input:
            address (string)

    output:
            boolean (True if deployed)
    '''
        
    address_dict = generate_json_response(address,llm,process_address)

    if "error_name" not in address_dict:
        return True
    else:
        return False

def extract_all_zoning_codes(collection):
    """
    extract all zoning codes stored in given mongoDB collection.

    input:
        collection (pymongo object) on which to run the query.
    
    output:
        list containing all stored zoning codes.
    """
    pipeline = [
        {"$group": {"_id": "$zoning_code"}}
    ]
    distinct_zoning_codes = collection.aggregate(pipeline)
    return [doc["_id"] for doc in distinct_zoning_codes]


def find_closest_match(target_code, zoning_codes):
    """
    fuzzy search for closest match between a given string and the list of zoning codes stored in mongoDB.

    input:
            target_code (string)
            zoning_codes (list of strings)
    output:
            string containing value of best match 
    """
    best_match = None
    best_score = 0
    
    for code in zoning_codes:
        score = fuzz.ratio(target_code, code)
        if score > best_score:
            best_match = code
            best_score = score
    
    return best_match

def map_zoning_code(target_code,collection):
    '''
    Extract all zoning codes and returns the closest match.

    input:
            target_code (string) containing the value on which to run fuzzy matching.
            collection (pymongo object) containing the list of zoning codes in mongoDB.
    '''
    zoning_codes_in_db = extract_all_zoning_codes(collection)
    return find_closest_match(target_code,zoning_codes_in_db)

def get_zoning_info_from_attom(json_response):
    """
    retrieves zoning information from attom.

    input:
        json_response with "address".
    output:
        json_response with "zoning_code", "city" and "state"
    
    """
    address = json_response['address']
    address_dict = generate_json_response(address,llm,process_address)

    if "error_message" not in address_dict:
        addrs_part1 = address_dict["number_street"]
        addrs_part2 = address_dict["city_state"]

        attom_resp_json = call_attom_API(addrs_part1,addrs_part2)

        # Extract city, state, and zoning code from the data
        city = attom_resp_json['property'][0]['address']['locality']
        state = attom_resp_json['property'][0]['address']['countrySubd']
        zoning_code = attom_resp_json['property'][0]['lot']['siteZoningIdent']

        # Store the extracted values in the result dictionary
        result ={}
        result['city'] = city.capitalize()
        result['state'] = "OK"  #FIX!!!
        result['zoning_code'] = map_zoning_code(zoning_code, vectors_collection) if zoning_code else 'RS-3' #FIX!!!
        if result['zoning_code'] == None:
            result['zoning_code'] = "RS-3"

        return result
    else: #FIX!!!
        result ={} #FIX!!!
        result['city'] = 'Tulsa'#FIX!!!
        result['state'] = 'OK'#FIX!!!
        result['zoning_code'] = 'RS-3' #FIX!!!

        return result#FIX!!!


# check if deployed
def is_deployed(address):
    '''
    check if address is in a deployed city.

    input:
            address (string)

    output:
            boolean (True if deployed)
    '''

    for city in DEPLOYED_CITIES:
        if city.lower() in address.lower():
            return True
    
    return False


def get_additional_info_from_user(json_response,required_info):
    """
    gets additional information from user.

    input: 
        json_response (dict) containing user intent and interaction metadata.
        required_info (list) listing the items to clarify.
    output:
            updated json_response with the missing info.
    """
    system_prompt = """
                            You are a real estate expert, specialized in land development topics.
                            You are trying to help the user on a query:
                               - request type: {type}
                               - concepts of interest: {concept}
                            
                            To help the user, you're missing some information listed below:
                               """+''.join(['- '+info+'\n' for info in required_info])+"""

                            Ask the user to clarify. Take a deep breath, you can do it :) 
                            """
        
    # Prepare System and Human messages for LLMChain
    chat_messages = [
                        ('system',system_prompt),
                        ('human', json_response["user_prompt"])
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    chain = prompt_template | llm | StrOutputParser()
    # Run LLM chain based on the entries
    llm_response = chain.invoke({"type":json_response["request_type"],"concept":json_response["concepts_of_interest"]}) 

    return llm_response 

def getMSANameForCounty(county_name, state_name):
    county_name = county_name.upper().strip()
    state_name = state_name.upper().strip()
    data_path = './ml_models/models/cost_model/mapping_files/' #'./cost_model/mapping_files/'
    county_to_msa_file =  pd.read_csv(data_path+'county_to_msa_mapping.csv')

    # print(county_to_msa_file)
    state_county_cmb = state_name+','+county_name
    print(state_county_cmb)
    msa_name = county_to_msa_file.loc[county_to_msa_file['State_county']==state_county_cmb]['MSA']
    print(msa_name)
    for msa_name,state_county_val in zip(county_to_msa_file['MSA'],	county_to_msa_file['State_county']):
        if(state_county_cmb == state_county_val):
            return msa_name
    return False
    

def predictConstructionCostFromModel(q_state,q_county,q_quality,q_story_count,q_basement_type,q_area):
    dir_name = './mapping_files/'
    q_state = q_state.upper()
    q_county = q_county.upper()
    q_quality = q_quality.upper()
    q_basement_type = q_basement_type.upper()

    if(q_area>5000):
        q_area = 5000
    if(q_area<1000):
        q_area = 1000

    q_city = getMSANameForCounty(q_county, q_state)

    print("--------- q city: ", q_city)

    if(q_city==False):
        return False

    state_city_mapping_file =  pd.read_csv(dir_name+'state_city_mapping.csv')
    state_city_dict = {}
    for state_city_name,state_city_mapping in zip(state_city_mapping_file['State_city'],state_city_mapping_file['Mapping']):
        state_city_dict[state_city_name] = state_city_mapping

    quality_mapping_file =  pd.read_csv(dir_name+'quality_mapping.csv')
    quality_val_dict = {}
    for quality_name,quality_mapping in zip(quality_mapping_file['Quality'],quality_mapping_file['Mapping']):
        quality_val_dict[quality_name] = quality_mapping

    basement_mapping_file =  pd.read_csv(dir_name+'basement_mapping.csv')
    basement_val_dict = {}
    for basement_name,basement_mapping in zip(basement_mapping_file['Basement'],basement_mapping_file['Mapping']):
        basement_val_dict[basement_name] = basement_mapping

    user_input = [q_state,q_city,q_quality,q_story_count,'NO',q_area]
    user_input_merged = [user_input[0]+','+user_input[1],user_input[2],user_input[3],user_input[4],user_input[5]]
    user_input_numeric = [[quality_val_dict[user_input_merged[1]],\
                     user_input_merged[2],basement_val_dict[user_input_merged[3]],user_input_merged[4]]]
    
    model_id = state_city_dict[user_input_merged[0]]
    pred_model = pickle.load(open('./ml_models/models/cost_model/state_wise_models/prediction_model_'+str(model_id)+'.sav', 'rb'))
    per_sq_ft_cost = pred_model.predict(user_input_numeric)
    
    return round(per_sq_ft_cost[0],2)
    

def calculateTotalConstructionCost(sq_ft_cost, area, area_basement,area_garage, basement_type, unfinished_scaling_factor=0.55):
    total_construction_cost = sq_ft_cost * area + area_garage*sq_ft_cost*unfinished_scaling_factor
    basement_type = basement_type.upper()
    if(basement_type=='FINISHED'):
        total_construction_cost += area_basement*sq_ft_cost
    if(basement_type=='UNFINISHED'):
        total_construction_cost += area_basement*sq_ft_cost*unfinished_scaling_factor
    return int(total_construction_cost)

def cost_estimation_inference(json_response):
    """
    computes construction costs for a given parcel
    
    inputs:
        json_response (dict) containing "state","county","building_quality","story count", "building area"

    outputs:
        dictionary with total cost and cost per sqft

    """

    q_state = json_response.get('state','OK')
    q_county = json_response.get('county','TULSA').upper()
    q_quality =  json_response.get('building_quality','bronze').upper() # 'bronze', 'silver', 'gold'
    q_story_count = json_response.get('story_count', 1) # must be number
    q_basement_type = json_response.get('basement_type','no').upper() # unfinished finished
    q_area = json_response.get('building_area', 15000) #must be number 
    area_basement = json_response.get('basement_area', 0) #must be number
    area_garage = json_response.get('garage_area', 0) #must be number

    sq_ft_cost = predictConstructionCostFromModel(q_state,q_county,q_quality,q_story_count,q_basement_type,q_area)
    total_cost = calculateTotalConstructionCost(sq_ft_cost, q_area, area_basement,area_garage, q_basement_type, unfinished_scaling_factor=0.55)

    return {"Total construction cost": total_cost,"Construction cost per square feet":sq_ft_cost}


def final_response(final_response):
    '''
    generates response to user prompt.

    input:
            final_response (dict) containing the 'user_prompt' and 'results' from DB query.
    
    output:
            llm_response (string), generated text from LLM.
    
    '''
    final_system_prompt = """
                            You are a real estate expert, specialized in land development topics.
                            Please respond to the user using this context for {address}:
                            {results}

                            Be strict and accurate to the provided context. If you do not have information about one of the user's question, just say so.
                            """
        
    # Prepare System and Human messages for LLMChain
    chat_messages = [
                        ('system',final_system_prompt),
                        ('human', "{input}")
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    chain = prompt_template | llm | StrOutputParser()
    # Run LLM chain based on the entries
    llm_response = chain.invoke({"input":final_response['user_prompt'],"results": final_response['results'],"address":final_response["address"]}) 

    return llm_response   

def process_user_prompt_json(json_response):
    '''
    This function verifies the conformity of the generated json and orients the LLM to the appropriate path of conversation.

    input:
        json_response (dict) containing generated json. 
            

    output:
            llm_response (string)

    '''
    # if json non valid format.
    if json_response.get('request_type','other') == "other":
        llm_response =  "Sorry, I am exclusively designed to assist you on land development questions. As such, I was unable to process your request. Could you please reformulate the information you are looking for ?"
    else:
        #if no address provided or address invalid
        if json_response['address'] == "NA" or is_address_valid(json_response['address'])==False:
            llm_response = "Sorry, but I was unable to understand your address. Could you please specify it one more time ?"
        # if no
        elif not is_deployed(json_response['address']):
            llm_response = "Sorry, I am not able to process requests for this city yet. Please do not hesitate to contact us to know more about our future deployments."
        else:
            #fetch zoning code city and state
            zoning_info = get_zoning_info_from_attom(json_response)

            for key in zoning_info:
                json_response[key] = zoning_info[key]

            # print(json.dumps(json_response, indent=4))

            if json_response.get('request_type','')=='zoning':

                # fetch relevant results from DB:
                json_response['results'] = query_db(json_response)

                # generate final response
                llm_response = final_response(json_response)

            elif json_response.get('request_type','')=='cost_estimation':
                
                # compute costs
                if json_response.get('building_area','NA') == 'NA' or json_response.get('building_quality','NA') == 'NA':
                    llm_response =  "Please reformulate your question adding the desired building area and building quality"
                else:
                    json_response['results'] = cost_estimation_inference(json_response)

                    # generate final response
                    llm_response = final_response(json_response)


    json_response['llm_response'] = llm_response
    return json_response


if __name__ == "__main__":
    # Example usage
    user_input = "what would be the setbacks at 4145 E 21st St, Tulsa, OK 74114?"
    # user_input = "what would be the setbacks at 3201 N Wild Mountain Rd, Tulsa, OK 74127 ?"
    json_response = generate_json_response(user_input,llm,get_user_request)
    # print(json.dumps(json_response, indent=4))
    llm_response = process_user_prompt_json(json_response)

    print(json.dumps(llm_response, indent=4))
