import os
from src.utils.prompt_utils import build_prompt, construct_messages_list
from langchain_openai import OpenAIEmbeddings
import logging

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_embedding(chunk):
    try:
        logging.info(f"Embedding chunk: {chunk[:50]}...")
        return embedding.embed_query(chunk)
    except Exception as e:
        logging.error(f"Error embedding chunk: {e}")
        raise RuntimeError(f"Embedding failed: {str(e)}")


def construct_llm_payload(question, context_chunks, chat_history):
    prompt = build_prompt(question, context_chunks)
    messages = construct_messages_list(chat_history, prompt)
    
    headers = {
        'content-type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"            
    }
    
    data = {
        'model': 'gpt-4',
        'messages': messages,
        'temperature': 1, 
        'max_tokens': 1000,
        'stream': True
    }
    return headers, data
