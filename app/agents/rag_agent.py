from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.tools.rag_tools import retrieve_policy_context
from app.utils.config import settings
from app.utils.prompts import RAG_PROMPT


def run_rag_agent(query: str) -> tuple[str, list[dict]]:
    context, sources = retrieve_policy_context(query)
    llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model, temperature=0)
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    chain = prompt | llm
    result = chain.invoke({"query": query, "context": context})
    return result.content.strip(), sources
