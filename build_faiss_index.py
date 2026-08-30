"""
Step 1 of RAG: Load PDFs → Chunk text → Create embeddings → Save FAISS index
"""
# Imports
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader # loads PDF files
from langchain_text_splitters import RecursiveCharacterTextSplitter # breaks docs into chunks
from langchain_openai import OpenAIEmbeddings # converts chunks into numerical vectors
from langchain_community.vectorstores import FAISS # FAISS stores vectors for similarity search

load_dotenv()

# --- Config ---
PDF_FOLDER = "rag_files" # Where the RAG documents are stored
FAISS_INDEX_PATH = "faiss_index" # Where to save the vector database
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # API Key
EMBEDDING_MODEL = "text-embedding-ada-002" # Embedding Model

# --- Step 1: Load PDFs ---
print("Loading PDFs...")
# Loop reads every PDF in rag_files, each PDF is loaded page by page
# Those pages are added to the documents list
documents = []

for filename in os.listdir(PDF_FOLDER):
    if filename.endswith(".pdf"):
        filepath = os.path.join(PDF_FOLDER, filename)
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        documents.extend(docs)
        print(f"Loaded: {filename} ({len(docs)} pages)")
# Confirm the script found and loaded the docs
print(f"Total pages loaded: {len(documents)}")

# --- Step 2: Split into chunks ---
print("\nSplitting into chunks...")
# After loading the PDFs, they are split into smaller text chunks
# RAG works with chunks because the model needs only most relevant pieces of documentation
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, # characters per chunk (500 characters = ~125 tokens = 80-100 words)
    chunk_overlap=50, # overlap between chunks to preserve context
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(chunks)}")

# Optional: Print all chunks so we can see what happened
# Helps confirm if docs are being split correctly and chunks make sense
for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(f"Source: {chunk.metadata['source']}, Page: {chunk.metadata['page']}")
    print(chunk.page_content)

# --- Step 3: Create embeddings and build FAISS index ---
print("\nCreating embeddings and building FAISS index...")
# Embedding converts each text chunk into a numerical vector representing its meaning
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    openai_api_key=OPENAI_API_KEY
)
# Embeds all chunks and stores them into a FAISS vector db
# FAISS allows Ollie to search for chunks most similar to user's questions
vectorstore = FAISS.from_documents(chunks, embeddings)

# --- Step 4: Save FAISS index ---
# Saves FAISS index to folder
vectorstore.save_local(FAISS_INDEX_PATH)

print(f"\nDone! FAISS index saved to: '{FAISS_INDEX_PATH}/'")