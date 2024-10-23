import requests
from django.conf import settings

def mixedbread_embeddings(payload):
    '''
    API call to the embedding model

    input:
        payload (dict) containing at least 'inputs' as key and a string as value.

    output:
        list of floats as the embedding representation of the input.
    
    '''
    response = {}
    if (settings.USE_MODELS_FALLBACK == 'True'):
        API_URL = "https://api-inference.huggingface.co/models/mixedbread-ai/mxbai-embed-large-v1"
        headers = {"Authorization": f"Bearer {settings.HUGGING_FACE_TOKEN}"}
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    else:
        API_URL = f'{settings.WEBSITE_ML_MODELS_URL}/inference/mxbai-embed'
        headers = {"x-api-key": f"{settings.WEBSITE_ML_MODELS_API_KEY}"}
        response = requests.post(API_URL, headers=headers, json=payload)
        response = (response.json())['embeddings']
        return response