import requests
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def text_generation(chat_messages, message_variables):
    '''
    API call to the text generation llm model

    input:
        payload (dict) containing 'chat_messages' and 'message_variables' keys.

    output:
        text response from the llm.
    
    '''
    llm_response = ''
    if (settings.USE_MODELS_FALLBACK == 'True'):
        llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0)
        chat_messages_ = [(message["role"], message["content"]) for message in chat_messages]
        prompt_template = ChatPromptTemplate.from_messages(chat_messages_)
        chain = prompt_template | llm | StrOutputParser()
        llm_response = chain.invoke(message_variables)
    else:
        API_URL = f'{settings.WEBSITE_ML_MODELS_URL}/inference/generate-text'
        headers = {"x-api-key": f"{settings.WEBSITE_ML_MODELS_API_KEY}"}
        response = requests.post(API_URL, headers=headers, json={'chat_messages': chat_messages, 'message_variables': message_variables})
        llm_response = (response.json())['llm_response']
    return llm_response