# src/quiz/faiss_utils.py
# AISS logic, chunking, and embedding code 

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from src.quiz.chapters import get_chapter_path

# Initialize the embeddings once here (avoid doing it repeatedly)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def process_chapter(chapter_name: str, cache=True) -> FAISS:
    """
    Loads the specified PDF, splits it into chunks, and builds a FAISS index.
    Each chunk is assigned a unique 'chunk_id' for reuse-avoidance.
    Optionally, caches the index to a directory for faster subsequent loads.
    """
    pdf_path = get_chapter_path(chapter_name)
    cache_dir = f"vector_cache/{chapter_name}"

    # If cache dir exists, load from local
    if cache and os.path.exists(cache_dir):
        return FAISS.load_local(cache_dir, embeddings, allow_dangerous_deserialization=True)

    # Otherwise, load + split PDF pages
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    # Ensure page_number is in metadata
    for i, page in enumerate(pages):
        page.metadata["page_number"] = page.metadata.get("page", i + 1)

    # Split with text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents(pages)

    # Assign unique chunk IDs
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{chapter_name}_chunk_{i}"

    # Create vector store
    vector_db = FAISS.from_documents(chunks, embeddings)
    if cache:
        vector_db.save_local(cache_dir)
    return vector_db

