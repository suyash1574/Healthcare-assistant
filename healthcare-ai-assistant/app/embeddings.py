import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.config import DATA_DIR, VECTOR_STORE_DIR, COLLECTION_NAME, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from app.logger import logger


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def ingest_documents():
    """Load .txt and .pdf docs from /data, chunk them, embed with HuggingFace, store in ChromaDB via LangChain."""
    documents = []
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
            documents.extend(docs)
            logger.info(f"Loaded TXT: {filename}")
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
            documents.extend(docs)
            logger.info(f"Loaded PDF: {filename} ({len(docs)} pages)")

    if not documents:
        raise ValueError(f"No documents found in {DATA_DIR}")

    logger.info(f"Total documents loaded: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Total chunks created: {len(chunks)}")

    embeddings = get_embeddings()

    # Delete existing collection and recreate
    if os.path.exists(VECTOR_STORE_DIR):
        import shutil
        shutil.rmtree(VECTOR_STORE_DIR, ignore_errors=True)
        logger.info("Cleared existing vector store")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_STORE_DIR
    )
    logger.info(f"Stored {len(chunks)} chunks in ChromaDB via LangChain")

    return {"message": "Documents ingested successfully", "chunks": len(chunks)}
