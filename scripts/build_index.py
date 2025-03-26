import os
from dotenv import load_dotenv
load_dotenv()

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

import requests
from io import BytesIO
import PyPDF2
from src.utils.vector_store_utils import build_vector_store


pdf_url = "https://enastava.matf.bg.ac.rs/~bojan/Super-racunari/Python%20Parallel%20Programming%20Cookbook%20.pdf"

response = requests.get(pdf_url)
if response.status_code == 200:
    pdf_data = BytesIO(response.content)
    
    reader = PyPDF2.PdfReader(pdf_data)
    full_text = ""
    
    # Optional: limit pages for testing
    # pages_to_read = min(len(reader.pages), 10)  # read 10 pages max
    pages_to_read = len(reader.pages)  # or read all
    
    for i in range(pages_to_read):
        page = reader.pages[i]
        full_text += page.extract_text() or ""

    print("Extracted text from PDF. Now building vector store...")

    # Build the FAISS vector store with your book text
    index, chunks = build_vector_store(full_text, chunk_size=500, overlap=50)
    print("Vector store built successfully!")
else:
    print(f"Failed to download PDF. Status code: {response.status_code}")
