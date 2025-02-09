from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import os
import shutil
from pathlib import Path

# Define paths
CHROMA_PATH = "chroma"
DATA_PATH = "data"

# Initialize lists to hold documents
md_documents = []

def main():
    generate_data_store()

def generate_data_store():
    print("Start processing...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    chunks = split_text(documents)
    print("Text chunks generated")
    save_to_chroma(chunks)

def load_documents():
    data_folder = Path(DATA_PATH)
    for file_path in data_folder.iterdir():
        if file_path.suffix == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
            md_documents.extend(loader.load())
            print(f"Loaded file: {file_path.name}")

    return md_documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear existing database
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Use Hugging Face embeddings (Free & Local)
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create and save embeddings to ChromaDB
    db = Chroma.from_documents(
        chunks, embedding_model, persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} text chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
