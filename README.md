# Personalized Learning App for Parallel & Distributed Computing using Python

Welcome to the **Personalized Learning App**! This interactive platform, built with **Streamlit**, is designed to help you master parallel and distributed computing in Python. The app offers three powerful features:

- **Adaptive Quiz Module 🎓**  
- **Chatbot 🤖**  
- **Code Mentor 👨‍💻**

---

## Features

### Adaptive Quiz Module 🎓
- **Dynamic Quiz Generation:**  
  Generate quizzes from various sources (PDF chapters, web links, YouTube videos, or uploaded PDFs).
- **Intelligent Content Processing:**  
  Content is loaded, split into chunks, and embedded. A FAISS vector store is built for similarity searches.
- **Dynamic Prompt Construction:**  
  Merges real-time context with pre-defined templates (for Multiple Choice, True/False, etc.) and calls the OpenAI API (GPT-3.5-Turbo) to generate questions.
- **Adaptive Difficulty:**  
  Quiz difficulty adjusts based on your performance.

**Architecture Overview:**
1. **Content Retrieval & Processing**
   - **Source Selection (`quiz_ui.py`):** User selects quiz source and sets parameters (number of questions, question type, difficulty).
   - **Content Loading:**  
     - **PDF Chapters:** Retrieve PDF path from `chapters.py` using a chapter-to-PDF mapping.  
     - **Other Sources:** Fetch and parse content from web links, YouTube, or uploaded PDFs.
   - **Document Processing & FAISS Indexing (`faiss_utils.py`):** Load content, split into chunks, generate embeddings via HuggingFace, and build a FAISS vector store.
2. **Prompt Construction & API Integration**
   - **Prompt Templates (`prompts.py`):** Pre-defined templates with dynamic instructions based on selected difficulty.
   - **Dynamic Prompt Construction:** Merge real-time context (e.g., chapter/topic, question count) into the selected template.
   - **API Call (`openai_client.py`):** Sends the final prompt to the OpenAI API (using GPT-3.5-Turbo) to generate quiz questions in JSON format.
3. **Quiz Generation & Adaptive UI**
   - **Quiz Logic (`quiz_logic.py`):** Parses API responses to generate a question skeleton, explanations, and hints.
   - **Display & Adaptation (`quiz_ui.py`):** Renders questions and feedback via Streamlit, captures user answers, and adapts difficulty for subsequent rounds.

---

### Chatbot 🤖
- **Conversational Learning:**  
  Engage in a chat to ask questions and receive guidance on parallel and distributed computing topics.
- **Document Preprocessing & Indexing:**  
  Download a PDF book, extract and split the text, compute embeddings with OpenAI's `text-embedding-ada-002`, and build a FAISS index.
- **Chat Processing (`chat_logic.py`):**  
  Embeds user prompts, retrieves similar passages from the FAISS index, and generates responses using GPT-4.
- **Conversation Management:**  
  Users can choose between Normal and Socratic modes. Chat history is archived in a SQLite database for future reference.

**Architecture Overview:**
1. **Document Preprocessing & Index Building**
   - **Build Index (`build_index.py`):** Downloads a PDF, extracts text, splits it, computes embeddings, and builds a FAISS index.
   - **Vector Store Utilities (`vector_store_utils.py`):** Saves and reloads the FAISS index and chunks (using pickle).
2. **User Interaction via Chat UI (`chat_ui.py`):**  
   Allows mode selection, chat management, and displays responses.
3. **Chat Processing (`chat_logic.py`):**  
   Embeds prompts, searches the index for relevant passages, and generates responses using GPT-4.
4. **Database Operations (`db_operations.py`):**  
   Archives conversations and manages chat history.

---

### Code Mentor 👨‍💻
- **Interactive Code Assistance:**  
  Improve your parallel programming skills with tools for code review, conversion, and challenges.
- **Debugger Mode:**  
  Reviews your code for syntax errors, deadlocks, race conditions, and inefficiencies using the Mistral API (mistral-large-latest).
- **Converter Mode:**  
  Converts your code from one parallel programming paradigm to another (e.g., multiprocessing to threading) with detailed explanations, powered by the Mistral API.
- **Challenges Mode:**  
  Generates dynamic coding challenges using the OpenAI API (GPT-3.5-Turbo) and lets you run your code in a secure Docker sandbox for immediate feedback.

**Architecture Overview:**

1. **Core Modules**
   - **Code Converter Module (`code_convertor.py`)**
     - **Purpose:** Converts parallel programming code from one paradigm to another.
     - **Key Components:**
       - *Mistral API Integration:* Calls Mistral’s chat completion endpoint.
       - *Prompt Construction:* Builds detailed prompts for conversion and explanation.
       - *Retry Logic:* Implements retries for rate limits.
     - **Output:** Returns converted code and an explanation.
   - **Code Review Module (`code_review.py`)**
     - **Purpose:** Reviews code to identify issues and suggest improvements.
     - **Key Components:**
       - *Mistral API Integration:* Uses Mistral’s chat endpoint for analysis.
       - *Prompt Construction:* Forms concise prompts for code review.
       - *Retry Logic:* Handles rate limits similar to the converter.
     - **Output:** Returns review feedback as a string.
   - **Code Challenges Module (`code_challenges.py`)**
     - **Purpose:** Dynamically generates interactive quiz questions and supports code execution.
     - **Key Components:**
       - *OpenAI API Integration:* Uses GPT-3.5-Turbo to generate questions in JSON.
       - *Prompt Construction:* Creates prompts based on challenge types (e.g., `write_code`, `complete_code`, `fix_bug`).
       - *JSON Extraction & Validation:* Ensures responses have the required keys (`type`, `prompt`, `instructions`, `code`, `test_case`).
       - *Docker-based Code Execution:* Executes user code in a Docker sandbox (using `python:3.9-slim`), capturing output and errors.
     - **Output:** Returns a JSON object representing a coding challenge along with execution feedback.
2. **User Interface Module (`code_mentor_ui.py`)**
   - **Purpose:**  
     Provides an interactive Streamlit interface for Code Mentor functionalities.
   - **Key Components:**
     - **Mode Selection:**  
       Users choose between:
       - **Debugger Mode:** Reviews code and provides feedback.
       - **Converter Mode:** Converts code to alternative paradigms with explanations.
       - **Challenges Mode:** Generates dynamic challenges and enables code execution.
     - **User Input Areas:**  
       Dedicated code editors for input; Converter Mode includes a target paradigm dropdown.
     - **Results Display:**  
       Renders output (review feedback, converted code, or challenge details) and maintains session state for seamless interaction.
   - **Docker Requirement:**  
     Docker must be installed and running for executing code challenges in a secure sandbox.

---

## Installation 🔧
### 1. Install Dependencies
```bash
pip install -r requirements.txt


### 2. Set Up Environment Variables
Create a .env file in the project root with:

OPENAI_API_KEY=your_openai_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here

### 3. Install Docker
Ensure Docker is installed and running on your machine (required for Code Challenges mode).

### 4. Run the Application

streamlit run app.py

----
Usage 📚
Adaptive Quiz Module
Content Source Selection:
Select your quiz source (PDF, Web Link, YouTube, Upload PDF) and configure quiz parameters (difficulty, question type, etc.).

Quiz Generation:
Generate adaptive quizzes that adjust based on your performance.

Chatbot Module
Conversational Interface:
Engage in a chat to ask questions or get guidance on parallel and distributed computing topics.

Mode Selection:
Choose between Normal and Socratic modes for varied interaction styles.

Code Mentor Module
Mode Selection:
Choose one of the following modes:

Debugger Mode:
Paste your code to receive a detailed review and actionable suggestions.

Converter Mode:
Input your code, select a target paradigm, and get your code converted along with a brief explanation.

Challenges Mode:
Generate interactive coding challenges, edit the provided code using the built-in editor, and run it in a secure Docker sandbox for immediate feedback.

