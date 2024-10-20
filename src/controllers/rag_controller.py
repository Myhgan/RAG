from . import api_blueprint
import os
import requests
import json
from flask import request, jsonify, Response, stream_with_context
import sseclient
from src.services import openai_service, pinecone_service
from src.utils.prompt_utils import chunk_text, format_response
from src.services.vector_db_service import embed_pdf_and_store, scrape_website
from colorama import Fore, Style

PINECONE_INDEX_NAME = 'index237'

@api_blueprint.route('/embed-pdf', methods=['POST'])
def embed_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400
        
    file = request.files['pdf_file']
    temp_dir = "E:\\RAG\\temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, 'wb') as f:
        f.write(file.read())
    
    response_message = embed_pdf_and_store(file_path, PINECONE_INDEX_NAME)
    os.remove(file_path)  # Xóa file tạm sau khi sử dụng
    return jsonify({"message": response_message})


@api_blueprint.route('/handle-query', methods=['POST'])
def handle_query():
    question = request.json['question']
    chat_history = request.json.get('chatHistory', [])

    try:
        context_chunks = pinecone_service.get_most_similar_chunks_for_query(question, PINECONE_INDEX_NAME)
    except Exception as e:
        error_message = f"Error retrieving similar chunks: {str(e)}"
        return jsonify(format_response(success=False, message=error_message))

    # if context_chunks:
    #     print(f"Kết quả khi so sánh vector db ({len(context_chunks)} kết quả):")
    #     for index, chunk in enumerate(context_chunks, start=1):
    #         print(f"{Fore.GREEN}Kết quả {index}: {Style.RESET_ALL}{chunk}")
    # else:
    #     print("Không tìm thấy kết quả nào từ cơ sở dữ liệu.")

    headers, data = openai_service.construct_llm_payload(question, context_chunks, chat_history)

    def generate():
        try:
            url = 'https://api.openai.com/v1/chat/completions'
            response = requests.post(url, headers=headers, json=data, stream=True)
            client = sseclient.SSEClient(response)

            response_text = ""
            for event in client.events():
                if event.data != '[DONE]':
                    try:
                        text = json.loads(event.data)['choices'][0]['delta']['content']
                        response_text += text
                    except Exception as e:
                        continue  # Nếu có lỗi thì tiếp tục chu trình

            # Trả về phản hồi JSON với cấu trúc chuẩn
            yield json.dumps(format_response(data={"message": response_text}, success=True))
        
        except Exception as e:
            error_message = f"Error processing OpenAI API response: {str(e)}"
            yield json.dumps(format_response(success=False, message=error_message))
        
    return Response(stream_with_context(generate()), mimetype='application/json')

@api_blueprint.route('/embed-and-store', methods=['POST'])
def embed_and_store():
    url = request.json['url']
    url_text = scrape_website(url)
    chunks = chunk_text(url_text)
    pinecone_service.embed_chunks_and_upload_to_pinecone(chunks, PINECONE_INDEX_NAME)
    response_json = {
        "message": "Chunks embedded and stored successfully"
    }
    return jsonify(response_json)

@api_blueprint.route('/delete-index', methods=['POST'])
def delete_index():
    pinecone_service.delete_index(PINECONE_INDEX_NAME)
    return jsonify({"message": f"Index {PINECONE_INDEX_NAME} deleted successfully"})
