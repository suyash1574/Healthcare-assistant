from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.config import LLM_PROVIDERS
from app.prompting import SYSTEM_PROMPT
from app.logger import logger

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])


def _create_llm(provider: dict):
    """Create an LLM instance for a given provider config."""
    if provider["name"] == "Groq":
        return ChatGroq(
            api_key=provider["api_key"],
            model=provider["model"],
            temperature=0.3,
            max_tokens=1024
        )
    else:
        # Nvidia NIM and OpenRouter are both OpenAI-compatible
        kwargs = {
            "api_key": provider["api_key"],
            "model": provider["model"],
            "temperature": 0.3,
            "max_tokens": 1024,
        }
        if provider["base_url"]:
            kwargs["base_url"] = provider["base_url"]
        return ChatOpenAI(**kwargs)


def get_llm_response(context: str, question: str, history: list = None) -> str:
    """Try each LLM provider in order until one succeeds."""
    for provider in LLM_PROVIDERS:
        if not provider["api_key"]:
            logger.warning(f"No API key for {provider['name']}, skipping")
            continue

        try:
            llm = _create_llm(provider)
            chain = prompt_template | llm
            response = chain.invoke({
                "context": context,
                "question": question
            })
            answer = response.content
            logger.info(f"LLM response generated via {provider['name']}")
            return answer

        except Exception as e:
            logger.warning(f"{provider['name']} failed: {str(e)}")
            continue

    logger.error("All LLM providers failed")
    return "Error: All LLM providers are currently unavailable. Please try again later."


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
