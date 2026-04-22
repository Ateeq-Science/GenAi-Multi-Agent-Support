from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.utils.config import settings
from app.utils.prompts import SUPERVISOR_PROMPT


def route_query(query: str) -> str:
    llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model, temperature=0)
    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=query),
    ])
    route = response.content.strip().upper()
    if route not in {"SQL", "RAG", "BOTH"}:
        return "RAG"
    return route
