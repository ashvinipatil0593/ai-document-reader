\# AI Document Reader



A RAG-based document question-answering application that allows users to upload PDF documents and ask questions about their content through a conversational chat interface.



\## Features



\* PDF document upload and text extraction

\* Document chunking with configurable chunk size and overlap

\* Semantic embeddings using `all-MiniLM-L6-v2`

\* FAISS-based vector similarity search

\* Retrieval-Augmented Generation (RAG) for document-based question answering

\* LLM responses using Groq `llama-3.1-8b-instant`

\* Conversational chat history and memory

\* MongoDB-based conversation storage

\* Redis-based login session and password reset handling

\* MCP tools for listing, viewing, and deleting conversations

\* Streamlit-based user interface

\* Retrieved document context can be viewed with each response



\## RAG Workflow



```text

PDF Upload

&#x20;   ↓

Text Extraction

&#x20;   ↓

Text Chunking

&#x20;   ↓

Sentence Embeddings

&#x20;   ↓

FAISS Vector Index

&#x20;   ↓

User Question

&#x20;   ↓

Question Embedding

&#x20;   ↓

FAISS Similarity Search

&#x20;   ↓

Relevant Document Chunks

&#x20;   ↓

Prompt with Retrieved Context

&#x20;   ↓

Groq LLM

&#x20;   ↓

Context-Grounded Answer

```



\## Tech Stack



\* Python

\* Streamlit

\* RAG

\* Sentence Transformers

\* FAISS

\* Groq LLM

\* MongoDB

\* Redis

\* MCP

\* PyPDF

\* LangChain

\* Git/GitHub



\## Project Structure



```text

ai-document-reader/

│

├── app.py

├── agent.py

├── auth.py

├── database.py

├── document\_store.py

├── mcp\_client.py

├── mcp\_server.py

├── prompts.py

├── rag.py

├── redis\_client.py

├── requirements.txt

│

├── services/

│   ├── conversation\_service.py

│   ├── document\_service.py

│   └── rag\_service.py

│

├── utils/

│   ├── embeddings.py

│   ├── llm.py

│   ├── pdf\_loader.py

│   └── vector\_store.py

│

└── tests/

```



\## Installation



\### 1. Clone the repository



```bash

git clone https://github.com/ashvinipatil0593/ai-document-reader.git

cd ai-document-reader

```



\### 2. Create a virtual environment



```bash

python -m venv .venv

```



Activate it on Windows:



```powershell

.venv\\Scripts\\activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file:



```env

GROQ\_API\_KEY=your\_groq\_api\_key

MONGODB\_URI=your\_mongodb\_connection\_string

```



Do not commit the `.env` file to GitHub.



\## Run the Application



```bash

streamlit run app.py

```



The application will open in the browser.



\## How It Works



1\. The user uploads a PDF document.

2\. The application extracts text from the PDF.

3\. The extracted text is divided into overlapping chunks.

4\. Each chunk is converted into an embedding using `all-MiniLM-L6-v2`.

5\. The embeddings are stored in a FAISS index.

6\. When the user asks a question, the question is converted into an embedding.

7\. FAISS retrieves the most relevant document chunks.

8\. The retrieved context and conversation history are passed to the LLM.

9\. Groq generates an answer based on the retrieved document context.

10\. The conversation is stored for continued interaction.



\## Example



```text

User:

What is this document about?



AI Document Reader:

\[Answer generated from the uploaded document]

```



\## Notes



\* The application is designed to answer questions using the uploaded document context.

\* If relevant information is not found in the retrieved document context, the application returns a fallback response.

\* API keys and database credentials should be stored in environment variables.



