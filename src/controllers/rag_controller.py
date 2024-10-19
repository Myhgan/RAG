from . import api_blueprint
import os
from flask import request, jsonify, Response, stream_with_context
import requests
import sseclient
import json
from src.services import openai_service, vector_db_service
from src.services.chunk_pdf_service import chunk_pdf

PINECONE_INDEX_NAME = 'index237'

@api_blueprint.route('/embedding-pdf', methods=['POST'])
def embed_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400
        
    file = request.files['pdf_file']
    file_path = rf"E:\RAG\file\{file.filename}"

    with open(file_path, 'wb') as f:
        f.write(file.read())
    
    response_message = chunk_pdf(file_path, PINECONE_INDEX_NAME)
    os.remove(file_path)
    return jsonify({"message": response_message})

@api_blueprint.route('/handle-query', methods=['POST'])
def handle_query():
    question = request.json['question']
    chat_history = request.json['chatHistory']

    context_chunks = vector_db_service.get_most_similar_chunks_for_query(question, PINECONE_INDEX_NAME)
    headers, data = openai_service.construct_llm_payload(question, context_chunks, chat_history)
    def generate():
        url = 'https://api.openai.com/v1/chat/completions'
        response = requests.post(url, headers=headers, json=data, stream=True) 
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data != '[DONE]':
                try:
                    text = json.loads(event.data)['choices'][0]['delta']['content']
                    yield(text)
                except:
                    yield('')

    return Response(stream_with_context(generate()))