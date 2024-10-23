import json
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chatbot.prompts import system_initial_prompt, request_types, example_user_prompts
from ml_models.models.llm import text_generation

def generate_json_response(input,call):
    '''
    Function to generate the JSON response.

    input: input (string), contains the user request.
    output: json_response (dict), translation of the user prompt to json.  
    '''
    response = extract_substring(call(input))
    try:
        json_response = json.loads(response)
        json_response['user_prompt'] = input

    except json.JSONDecodeError:
        json_response = {
                            "error_message": "Couldn't generate a valid JSON response for that input.",
                            "input": input,
                            "user_prompt": input,
                            "response": response
                        }
    return json_response

def get_user_request(input):
    '''
    Fetches the user request in JSON format.

    Inputs:
            input (string) containing user request.
    Output:
            json format representation of user request    
    '''
    chat_messages = [{"role": 'system', "content": system_initial_prompt}, {"role": 'user', "content": "{input}"}]
    message_variables = {"input":input,"request_types": request_types, "example_user_prompts":example_user_prompts}
    results = text_generation(chat_messages, message_variables)
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