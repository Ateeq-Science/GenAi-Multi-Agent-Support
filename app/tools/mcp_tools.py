from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.tools.rag_tools import retrieve_policy_context
from app.tools.sql_tools import build_customer_context_from_query, extract_customer_name, get_customer_by_name, get_tickets_by_customer

app = FastAPI(title="GenAI Support MCP-style Tool Server")


class SearchRequest(BaseModel):
    query: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/customer/{name}")
def customer_lookup(name: str) -> dict:
    customer = get_customer_by_name(name)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    tickets = get_tickets_by_customer(int(customer["customer_id"]))
    return {"customer": customer, "tickets": tickets}


@app.post("/structured/search")
def structured_search(req: SearchRequest) -> dict:
    return {"result": build_customer_context_from_query(req.query)}


@app.post("/policy/search")
def policy_search(req: SearchRequest) -> dict:
    context, sources = retrieve_policy_context(req.query)
    return {"context": context, "sources": sources}
