from langchain_community.document_loaders import PyPDFLoader
from src.services.vector_db_service import embed_chunks_and_upload_to_pinecone

def chunk_pdf(file_path, index_name):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    texts = [page.page_content for page in pages]

    # Gọi Pinecone service để lưu trữ
    embed_chunks_and_upload_to_pinecone(texts, index_name)
    
    return f"{len(pages)} pages embedded and uploaded to Pinecone index '{index_name}'."
