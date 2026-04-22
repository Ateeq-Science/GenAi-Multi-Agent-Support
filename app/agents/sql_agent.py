from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.tools.sql_tools import build_customer_context_from_query
from app.utils.config import settings
from app.utils.prompts import SQL_SUMMARY_PROMPT


def run_sql_agent(query: str) -> str:
    structured_data = build_customer_context_from_query(query)
    llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model, temperature=0)
    prompt = ChatPromptTemplate.from_template(SQL_SUMMARY_PROMPT)
    chain = prompt | llm
    result = chain.invoke({"query": query, "data": structured_data})
    return result.content.strip()
