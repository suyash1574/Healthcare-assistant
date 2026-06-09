from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY, LLM_MODEL
from app.prompting import SYSTEM_PROMPT
from app.logger import logger

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])


def get_llm_response(context: str, question: str, history: list = None) -> str:
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set")
        return "Error: GROQ_API_KEY not configured in .env file."

    try:
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0.3,
            max_tokens=1024
        )

        chain = prompt_template | llm

        response = chain.invoke({
            "context": context,
            "question": question
        })

        answer = response.content
        logger.info("LLM response generated successfully via LangChain")
        return answer

    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        return f"Error generating response. Please try again."


def compute_confidence(sources: list) -> str:
    """Simple confidence scoring based on number of retrieved chunks."""
    n = len(sources)
    if n >= 3:
        return "high"
    elif n == 2:
        return "medium"
    elif n == 1:
        return "low"
    return "none"
