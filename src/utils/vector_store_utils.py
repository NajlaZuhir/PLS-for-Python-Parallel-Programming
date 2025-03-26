import openai
import faiss
import numpy as np
import pickle

def build_vector_store(book_text, chunk_size=500, overlap=50, index_path="faiss_index.pkl", chunks_path="chunks.pkl"):
    """
    Splits the book text into overlapping chunks, computes embeddings for each chunk using OpenAI,
    builds a FAISS index, and saves both the index and the list of chunks to disk.
    """
    # Split text into chunks with overlap
    chunks = []
    start = 0
    while start < len(book_text):
        end = start + chunk_size
        chunk = book_text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    # Compute embeddings for each chunk
    embeddings = []
    for chunk in chunks:
        response = openai.Embedding.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embedding = response["data"][0]["embedding"]
        embeddings.append(embedding)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # Build FAISS index (using L2 distance)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index and chunks to disk
    with open(index_path, "wb") as f:
        pickle.dump(index, f)
    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)
    
    return index, chunks

def load_vector_store(index_path="faiss_index.pkl", chunks_path="chunks.pkl"):
    """
    Loads a previously built FAISS index and the associated text chunks from disk.
    """
    with open(index_path, "rb") as f:
        index = pickle.load(f)
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks
