# Chatbot Architecture Overview

## 1. Document Preprocessing & Index Building

### 1.1. build_index.py (Run Once)
- **Download Book (PDF):**
  - Download the book in PDF format through a provided link.
- **Extract Text:**
  - Extract all text from the book.
- **Build Vector Store:**
  - Uses the `build_vector_store` function from `vector_store_utils.py`.

### 1.2. vector_store_utils.py
- **Function: build_vector_store**
  - **Splitting Text:**
    - Splits text into chunks using `chunk_size=500` and `overlap=50`.
  - **Computing Embeddings:**
    - Computes embeddings for each chunk using OpenAI’s `"text-embedding-ada-002"` model.
  - **Building FAISS Index:**
    - Builds a FAISS index for similarity searches.
  - **Saving Data:**
    - Saves the FAISS index and chunks using the `pickle` module in the main project directory for later use.
- **Function: load_vector_store**
  - **Reloading Data:**
    - Reloads the previously stored `faiss_index.pkl` and `chunks.pkl`.
  - **Usage:**
    - Used by `chat_logic.py` to access the vector store.

## 2. User Interaction via Chat UI

### chat_ui.py (Chat Interface)
- **Mode Selection:**
  - Allows the user to select a mode (“Normal” or “Socratic”).
- **Chat Management:**
  - Users can start a new chat or select an existing one.
  - The user’s message is added to the chat history.
- **Display:**
  - Displays the generated answer within the chat interface.

## 3. Chat Processing

### chat_logic.py
- **Embedding the Prompt:**
  - Converts the user’s prompt into an embedding using the `"text-embedding-ada-002"` model.
- **Searching the Index:**
  - Uses the embedding to search the FAISS index for the most similar document chunks.
  - Retrieves the top matching passages.
- **Context Formatting:**
  - Formats the retrieved passages into numbered passages.
- **System Message Creation:**
  - Gets the system message based on the selected mode (Normal or Socratic).
- **Response Generation:**
  - Generates a response using the system message and the GPT-4 model.

## 4. Database Operations

- **Archiving Conversations:**
  - Archives the conversation in a SQLite database via `db_operations.py`.
- **Chat History:**
  - Archived conversations are used to populate the chat history in the sidebar for future reference.
- **Deletion Functionality:**
  - Provides functionalities for deleting old conversations.

 # Code Mentor Architecture Overview

The Code Mentor system supports two main features—code review (debugging) and code conversion—using Mistral’s API.

## 1. Core Modules

### 1.1. code_convertor.py
- **Purpose:**  
  Converts parallel programming code from one paradigm to another (e.g., from multiprocessing to threading) and provides an explanation using Mistral.

### 1.2. code_review.py
- **Purpose:**  
  Reviews provided parallel programming code to identify issues (e.g., syntax errors, potential deadlocks, race conditions) and suggests improvements using Mistral.

## 2. Code Mentor UI

### code_mentor.py
- **Purpose:**  
  Provides an interactive user interface for both code review and code conversion tasks.
- **Features:**  
  - **Debugger Mode:**  
    For code review, where users input code to receive debugging and review feedback.
  - **Converter Mode:**  
    For code conversion, where users input code and select a target paradigm to receive converted code along with an explanation.

