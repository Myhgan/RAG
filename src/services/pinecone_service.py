import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_community.document_loaders import PyPDFLoader
from src.services.openai_service import get_embedding
from pinecone import Pinecone as PineconeClient, ServerlessSpec

# Khởi tạo Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = "us-east-1"

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
    
    vector_store = LangchainPinecone.from_existing_index(index_name, embedding)
    results = vector_store.similarity_search(query, k=3)
    return [result.page_content for result in results]


def delete_index(index_name):
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
        print(f"Index '{index_name}' deleted successfully")