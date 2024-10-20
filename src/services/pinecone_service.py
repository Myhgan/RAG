import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from src.services.openai_service import get_embedding
from pinecone import Pinecone as PineconeClient, ServerlessSpec
import redis
import json
import time

# Khởi tạo Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = "us-east-1"
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Khởi tạo client
pc = PineconeClient(api_key=PINECONE_API_KEY)
embedding = OpenAIEmbeddings()

def create_pinecone_index(index_name):
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region=PINECONE_ENVIRONMENT
            )
        )

def embed_chunks_and_upload_to_pinecone(chunks, index_name):
    function_name = "embed_chunks_and_upload_to_pinecone"
    
    create_pinecone_index(index_name)
    index = pc.Index(index_name)
    embeddings_with_ids = []
    
    for i, chunk in enumerate(chunks):
        try:
            embedding_vector = get_embedding(chunk)
            embeddings_with_ids.append((str(i), embedding_vector, chunk))
        except Exception as e:
            print(f"Error embedding chunk {i}: {e}", function_name)
    
    # Thực hiện upload các vectors lên Pinecone
    upserts = [(id, vec, {"chunk_text": text}) for id, vec, text in embeddings_with_ids]
    
    print(f"Uploading {len(upserts)} vectors to Pinecone index '{index_name}'...", function_name)
    index.upsert(vectors=upserts)

    print(f"Embedded {len(chunks)} chunks to Pinecone index '{index_name}'", function_name)

def get_most_similar_chunks_for_query(query, index_name):
    if index_name not in pc.list_indexes().names():
        raise ValueError(f"Index {index_name} does not exist")

    # start_time = time.time() 

    # # Kiểm tra cache
    # cache_key = f"query_cache:{query}"
    # cached_result = redis_client.get(cache_key)
    # if cached_result:
    #     end_time = time.time()  # Thời gian kết thúc khi tìm thấy trong cache
    #     elapsed_time_with_cache = end_time - start_time
    #     print(f"Thời gian truy vấn khi sử dụng Redis cache: {elapsed_time_with_cache:.4f} giây")
    #     return json.loads(cached_result)

    print("\nEmbedding query using OpenAI ...")
    question_embedding = get_embedding(query)

    # Sử dụng Pinecone API để thực hiện tìm kiếm
    index = pc.Index(index_name)
    
    # Sử dụng đối số từ khóa cho query
    query_results = index.query(vector=question_embedding, top_k=3, include_metadata=True)

    # Lấy văn bản từ kết quả truy vấn
    context_chunks = [x['metadata']['chunk_text'] for x in query_results['matches']]
    
    # In ra kết quả trả về để kiểm tra
    # print(f"Kết quả tìm kiếm: {context_chunks}")

    # Lưu kết quả vào cache trong 1 giờ
    # redis_client.set(cache_key, json.dumps(context_chunks), ex=3600)
    
    return context_chunks

def delete_index(index_name):
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
        print(f"Index '{index_name}' deleted successfully")