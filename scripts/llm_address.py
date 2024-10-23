from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser
import urllib.parse
import requests
import json
import pymongo
from fuzzywuzzy import fuzz
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)

mongodb_path = os.getenv('MONGODB_URL')

dbclient = pymongo.MongoClient(mongodb_path)
iqlandDB = dbclient["IQLAND"]
vectors_collection = iqlandDB["Zoning_vectors"]


def process_address(address,llm):
    '''
    process_address for ATTOM call

    input:
            address (string) containing the addresss.
    
    output:
            llm_response (string), generated text from LLM.
    
    '''
    final_system_prompt = """
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
                        ('system',final_system_prompt),
                        ('human', "{address}")
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    chain = prompt_template | llm | StrOutputParser()
    # Run LLM chain based on the entries
    llm_response = chain.invoke({address}) 

    return llm_response   

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

def callAttomPropertyAPI(addrs_part1,addrs_part2):
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
    print('Address Part1 : ',addrs_part1_uri,' Address Part2 : ',addrs_part2_uri)
    attom_url = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/expandedprofile?address1='+addrs_part1_uri+'&address2='+addrs_part2_uri+'&debug=True'
    headers = {'apikey': os.getenv('ATTOM_API_KEY'), 'accept': "application/json", }
    attom_resp = requests.get(attom_url,headers=headers)
    attom_resp_json = attom_resp.json()

    return attom_resp_json


def get_zoning_info_from_attom(address):
    """
    retrieves zoning information from attom.

    input:
        address (string)
    output:
        json_response with "zoning_code", "city" and "state"
    
    """
    address_dict = generate_json_response(address,llm,process_address)

    if "error_message" not in address_dict:
        addrs_part1 = address_dict["number_street"]
        addrs_part2 = address_dict["city_state"]

        attom_resp_json = callAttomPropertyAPI(addrs_part1,addrs_part2)

        # Extract city, state, and zoning code from the data
        city = attom_resp_json['property'][0]['address']['locality']
        state = attom_resp_json['property'][0]['address']['countrySubd']
        zoning_code = attom_resp_json['property'][0]['lot']['siteZoningIdent']

        # Store the extracted values in the result dictionary
        result ={}
        result['city'] = city
        result['state'] = state
        result['zoning_code'] = map_zoning_code(zoning_code, vectors_collection) if zoning_code else 'RS-3'

        return result
    else:
        result ={}
        result['city'] = 'Tulsa'
        result['state'] = 'OK'
        result['zoning_code'] = 'RS-3' 

        return result

def extract_all_zoning_codes(collection):
    pipeline = [
        {"$group": {"_id": "$zoning_code"}}
    ]
    distinct_zoning_codes = collection.aggregate(pipeline)
    return [doc["_id"] for doc in distinct_zoning_codes]


def find_closest_match(target_code, zoning_codes):
    best_match = None
    best_score = 0
    
    for code in zoning_codes:
        score = fuzz.ratio(target_code, code)
        if score > best_score:
            best_match = code
            best_score = score
    
    return best_match

def map_zoning_code(target_code,collection):
    zoning_codes_in_db = extract_all_zoning_codes(collection)
    return find_closest_match(target_code,zoning_codes_in_db)


addresses = ["1202 W Gore Blvd, Lawton, OK 73501",
             "1702 NW Bell Ave, Lawton, OK 73507",
             "7044 E 71st Ct, Tulsa, OK 74133",
             "2101 Verbena St Nw Atlanta, GA 30314",
             "8226 E 34th St Tulsa, OK",
             "2998 Miriam Court Decatur GA"
             ]

for add in addresses:
    print(add)
    print(get_zoning_info_from_attom(add))
    print("-----")
    print("------")



