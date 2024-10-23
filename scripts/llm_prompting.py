from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate 
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
                        Example input 1: 'What is the lot coverage and the side yard setback for 2101 Verbena St Nw Atlanta, GA 30314 ?

                        Example output 1: 
                        {{
                                "address": "2101 Verbena St Nw Atlanta, GA 30314",
                                "request_type": "zoning",
                                "concepts_of_interest": ["lot coverage", "side yard setback"]
                        }}

                        Example input 2: "I have a parcel, I'd like to estimate the cost of my project please help.
                        
                        Example output 2: 
                        {{
                                "address": "NA",
                                "request_type": "cost_estimation",
                                "concepts_of_interest": "cost"
                        }}

                        """

llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125",temperature=0)

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
    llmchain = LLMChain(llm=llm, prompt=prompt_template)

    # Run LLM chain based on the entries
    results = llmchain.run({"input":input,"request_types": request_types, "example_user_prompts":example_user_prompts})

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

def generate_json_response(input):
    '''
    Function to generate the JSON response.

    input: input (string), contains the user request.
    output: json_response (dict), translation of the user prompt to json.  
    '''
    response = extract_substring(get_user_request(input,llm))
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



# Replace by query DB function!
# including entity matching + DB query!
def query_db(json_response):
    '''
    retrieves information from DB based on user prompt.

    input: 
            json_response (dict) representing user prompt in structured format.

    output:
            query results as a dict or list of dict
    
    '''

    return {
            "FAR" : { 
                    "name": "FAR",
                    "value": 0.4, 
                    "unit":"ratio",
                    "source":"https://library.municode.com/ga/atlanta/codes/code_of_ordinances?nodeId=PTIIICOORANDECO_PT16ZO_CH6SIMIREDIRE_S16-06.008MIYARE"},
            "setbacks" : {
                            "front_setback" : {
                                            "name": "Front setback",
                                            "value": 35,
                                            "unit":"feet",
                                            "source":"https://library.municode.com/ga/atlanta/codes/code_of_ordinances?nodeId=PTIIICOORANDECO_PT16ZO_CH6SIMIREDIRE_S16-06.008MIYARE"
                                            },
                            "side_setback" : {
                                            "name": "Side setback",
                                            "value": 7, 
                                            "unit":"feet",
                                            "source":"https://library.municode.com/ga/atlanta/codes/code_of_ordinances?nodeId=PTIIICOORANDECO_PT16ZO_CH6SIMIREDIRE_S16-06.008MIYARE"
                                            },
                            "rear_setback" : {
                                            "name":"Rear setback",
                                            "value": 15,
                                            "unit":"feet",
                                            "source":"https://library.municode.com/ga/atlanta/codes/code_of_ordinances?nodeId=PTIIICOORANDECO_PT16ZO_CH6SIMIREDIRE_S16-06.008MIYARE"
                                            }
                        }
            }

#deployed cities:
DEPLOYED_CITIES = ['Atlanta', 'Tulsa']

#use your function instead! #replace is_address_valid by your verification function.
def is_address_valid(address):
    '''
    check if address is valid.

    input:
            address (string)

    output:
            boolean (True if deployed)
    '''
    return True

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
    llmchain = LLMChain(llm=llm, prompt=prompt_template)
    # Run LLM chain based on the entries
    llm_response = llmchain.run({"input":final_response['user_prompt'],"results": final_response['results'],"address":final_response["address"]}) 
    print('============================')
    print(llm_response, 'llm_response here')
    print('===========================')
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

            # fetch relevant results from DB:
            json_response['results'] = query_db(json_response)

            print(json_response['results'])

            # generate final response
            llm_response = final_response(json_response)

    return llm_response


if __name__ == "__main__":
    # Example usage
    # user_input = "Give me FAR and setbacks for 24 Orez Street,30356 Atlanta."
    user_input = "Can you please recommend plans for the 24 Orez Street,30356 Atlanta."
    json_response = generate_json_response(user_input)
    print(json.dumps(json_response, indent=4))
    llm_response = process_user_prompt_json(json_response)

    print(llm_response)