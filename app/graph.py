from __future__ import annotations

from typing import Literal, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.agents.rag_agent import run_rag_agent
from app.agents.sql_agent import run_sql_agent
from app.agents.supervisor_agent import route_query
from app.utils.config import settings
from app.utils.prompts import SYNTHESIS_PROMPT


class AgentState(TypedDict, total=False):
    user_query: str
    route: Literal["SQL", "RAG", "BOTH"]
    sql_result: str
    rag_result: str
    sources: list[dict]
    final_answer: str


def supervisor_node(state: AgentState) -> AgentState:
    return {"route": route_query(state["user_query"])}


def sql_node(state: AgentState) -> AgentState:
    return {"sql_result": run_sql_agent(state["user_query"])}


def rag_node(state: AgentState) -> AgentState:
    rag_result, sources = run_rag_agent(state["user_query"])
    return {"rag_result": rag_result, "sources": sources}


def synthesis_node(state: AgentState) -> AgentState:
    route = state.get("route", "RAG")

    if route == "SQL":
        return {"final_answer": state.get("sql_result", "No structured answer available.")}

    if route == "RAG":
        return {"final_answer": state.get("rag_result", "No policy answer available.")}

    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_template(SYNTHESIS_PROMPT)
    chain = prompt | llm
    result = chain.invoke(
        {
            "query": state["user_query"],
            "sql_result": state.get("sql_result", "No structured result."),
            "rag_result": state.get("rag_result", "No policy result."),
        }
    )
    return {"final_answer": result.content.strip()}


def _route_after_supervisor(state: AgentState) -> str:
    route = state.get("route", "RAG")
    if route == "SQL":
        return "sql"
    if route == "RAG":
        return "rag"
    return "both_start"


def _route_after_sql(state: AgentState) -> str:
    route = state.get("route", "SQL")
    if route == "BOTH":
        return "rag"
    return "synthesis"


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("sql", sql_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("synthesis", synthesis_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {
            "sql": "sql",
            "rag": "rag",
            "both_start": "sql",
        },
    )

    workflow.add_conditional_edges(
        "sql",
        _route_after_sql,
        {
            "rag": "rag",
            "synthesis": "synthesis",
        },
    )

    workflow.add_edge("rag", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile()


def run_query(query: str) -> AgentState:
    app = build_graph()
    return app.invoke({"user_query": query})