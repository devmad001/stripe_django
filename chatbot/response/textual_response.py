from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ml_models.models.llm import text_generation

def get_sources_list(data):
    '''
    This function creates a list of sources like {'name': '', 'source': ''} to keep all reference sources in one list
    '''
    sources_list = []
    seen = set()

    def recursive_search(current_obj):
        if not isinstance(current_obj, dict):
            return

        for key, value in current_obj.items():
            if key == 'name' and 'source' in current_obj:
                name = current_obj['name']
                source = current_obj['source']

                # Create a unique identifier for name-source pairs to avoid duplicates
                identifier = f"{name}:{source}"
                if identifier not in seen:
                    sources_list.append({'name': name, 'source': source})
                    seen.add(identifier)

            if isinstance(value, dict):
                recursive_search(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        recursive_search(item)

    for item in data:
        if isinstance(item, dict):
            recursive_search(item)

    return sources_list

def remove_source_links(data):
    '''
    This function removes source links from db response so that when passing to LLM we can save extra tokens
    '''
    def recursive_remove(current_obj):
        if not isinstance(current_obj, dict):
            return

        for key, value in list(current_obj.items()):
            if key == 'source':
                del current_obj[key]
            elif isinstance(value, dict):
                recursive_remove(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        recursive_remove(item)

    for item in data:
        if isinstance(item, dict):
            recursive_remove(item)

def final_response_other_intent(user_message):
    '''
    generates response to user prompt for cases where request type is other.
    input:

    output:
            llm_response (string), generated text from LLM
    '''
    system_prompt = """
                        You are a real estate expert specialized in land development topics. In case the user asks some general knowledge question you can provide help with them as well.
                        Provide concise and accurate answers to the query and if you do not know the answer just say that you do not know about that topic. 
                        Do not provide false information. Use the following markdown format for your response:
                        
                        - [Link text](URL) for hyperlinks
                        - Lists for enumerations:
                        - Use dashes for bullet points
                        - Use numbers for ordered lists

                        ## Tables
                        Use tables for structured data:

                        | Column 1 | Column 2 |
                        |----------|----------|
                        | Data 1   | Data 2   |
                        | Data 3   | Data 4   |

                        Ensure the responses are clear and well-structured.
                    """
    chat_messages = [{"role": 'system', "content": system_prompt}, {"role": 'user', "content": "{input}"}]
    message_variables = {"input":user_message}
    llm_response = text_generation(chat_messages, message_variables) 
    return llm_response

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

                            Use the following markdown formatting in your responses:

                            - **Bold text** for emphasis
                            - *Italic text* for emphasis
                            - Lists for enumerations:
                            - Use dashes for bullet points
                            - Use numbers for ordered lists

                            ## Tables
                            Use tables for structured data:

                            | Column 1 | Column 2 |
                            |----------|----------|
                            | Data 1   | Data 2   |
                            | Data 3   | Data 4   |

                            Note:
                            1. Use tables in the response to display data where appropriate
                            2. Important: Do not add links/urls and images in your response
                            3. If data can be displayed in lists and tables both, then prefer to use table

                            Ensure the responses are clear and well-structured.
                            """
    
    chat_messages = [{"role": 'system', "content": final_system_prompt}, {"role": 'user', "content": "{input}"}]
    message_variables = {"input":final_response['user_prompt'],"results": final_response['results'],"address":final_response["address"]}
    llm_response = text_generation(chat_messages, message_variables) 

    return llm_response   

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

    chat_messages = [{"role": 'system', "content": system_prompt}, {"role": 'user', "content": json_response["user_prompt"]}]
    message_variables = {"type":json_response["request_type"],"concept":json_response["concepts_of_interest"]}
    llm_response = text_generation(chat_messages, message_variables)

    return llm_response 