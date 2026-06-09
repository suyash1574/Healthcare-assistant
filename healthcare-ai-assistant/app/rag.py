from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import VECTOR_STORE_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K_RESULTS, SIMILARITY_THRESHOLD
from app.logger import logger


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=VECTOR_STORE_DIR
    )


def retrieve_context(question: str):
    """
    Retrieve relevant document chunks for a question using LangChain Chroma retriever.
    Returns (contexts, sources) where sources include document name and chunk preview.
    """
    try:
        vectorstore = get_vectorstore()
    except Exception as e:
        logger.error(f"Failed to load vectorstore: {e}")
        return [], []

    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": TOP_K_RESULTS,
            "score_threshold": SIMILARITY_THRESHOLD
        }
    )

    try:
        docs = retriever.invoke(question)
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        return [], []

    if not docs:
        logger.warning("No relevant documents found above similarity threshold")
        return [], []

    contexts = []
    sources = []
    seen_sources = set()

    for doc in docs:
        contexts.append(doc.page_content)
        source_name = doc.metadata.get("source", "unknown")
        chunk_preview = doc.page_content[:120].replace("\n", " ").strip() + "..."

        if source_name not in seen_sources:
            seen_sources.add(source_name)

        sources.append({
            "document": source_name,
            "chunk": chunk_preview
        })
        logger.info(f"Retrieved chunk from '{source_name}': {chunk_preview[:60]}...")

    logger.info(f"Retrieved {len(contexts)} chunks from {len(seen_sources)} source(s)")
    return contexts, sources
