import openai
import faiss
import numpy as np
from src.utils.vector_store_utils import load_vector_store
from src.chat.normal_mode import get_system_message as normal_sysmsg, format_context as normal_context
from src.chat.socratic_mode import get_system_message as socratic_sysmsg, format_context as socratic_context
import os

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set your OPENAI_API_KEY in your .env file.")

def embed_text(text):
    """
    Uses the OpenAI embeddings API to get an embedding for the given text.
    """
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]
    return np.array(embedding, dtype=np.float32)

def search_documents(query, index, chunks, top=5):
    """
    Embeds the query and searches the FAISS index for the top most similar document chunks.
    Returns a list of dictionaries with the chunk content.
    """
    query_embedding = embed_text(query)
    # FAISS expects a 2D array (num_queries x dimension)
    query_embedding = np.expand_dims(query_embedding, axis=0)
    distances, indices = index.search(query_embedding, top)
    
    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append({"content": chunks[i]})
    return results

def generate_response(prompt, mode="normal", top=5):
    """
    Given a prompt, this function:
      1. Loads the vector store (FAISS index and text chunks).
      2. Searches for the most relevant passages.
      3. Depending on 'mode', uses either normal or Socratic instructions.
      4. Calls OpenAI’s ChatCompletion API to generate a response.
    """
    # 1. Load the FAISS vector store and associated text chunks.
    index, chunks = load_vector_store()

    # 2. Search for relevant passages.
    search_results = search_documents(prompt, index, chunks, top=top)

    # 3. Format the context string based on the mode.
    if mode.lower() == "socratic":
        context_str = socratic_context(search_results)
        system_message = socratic_sysmsg(context_str)
    else:
        context_str = normal_context(search_results)
        system_message = normal_sysmsg(context_str)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    # 4. Call OpenAI’s ChatCompletion API.
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Change if needed
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )

    return response["choices"][0]["message"]["content"]

# Example usage:
if __name__ == "__main__":
    user_prompt = "Explain the concept of distributed computing as discussed in the book."
    # mode can be "normal" or "socratic"
    answer = generate_response(user_prompt, mode="normal", top=5)
    print("Response:", answer)
