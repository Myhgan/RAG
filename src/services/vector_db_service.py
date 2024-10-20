from langchain_community.document_loaders import PyPDFLoader
from src.services.pinecone_service import embed_chunks_and_upload_to_pinecone

def embed_pdf_and_store(file_path, index_name):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()  # Tải và chia nhỏ các trang PDF
    texts = [page.page_content for page in pages]
    
    # Gọi Pinecone service để lưu trữ
    embed_chunks_and_upload_to_pinecone(texts, index_name)
    
    return f"{len(pages)} pages embedded and uploaded to Pinecone index '{index_name}'."
