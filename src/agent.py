from typing import Any
from .config import settings
from .context import add_event, render_events
from .llm import call_agent_llm
from .retrieval import retrieve_relevant_tables, format_schema_context
from .sql_validator import clean_sql, validate_readonly_sql
from .db import execute_readonly_sql


def _latest_retrieved_tables(events: list[dict[str, Any]]) -> list[dict]:
    for event in reversed(events):
        if event["type"] == "retrieve_relevant_tables_result":
            return event["data"]["tables"]
    return []


def _allowed_tables_from_events(events: list[dict[str, Any]]) -> set[str]:
    rows = _latest_retrieved_tables(events)
    return {row["table_name"] for row in rows}


def run_agent(user_question: str) -> dict:
    events: list[dict[str, Any]] = []

    add_event(events, "user_request", user_question)
  
    for step in range(settings.max_agent_steps):
        context_prompt = render_events(events)

        try:
            action = call_agent_llm(context_prompt)
            print(action)
        except Exception as exc:
          
            add_event(
                events,
                "error",
                {
                    "source": "llm_json_parse",
                    "message": str(exc),
                },
            )
            continue

        intent = action.get("intent")
        add_event(events, intent or "unknown_intent", action)
        
        if intent == "retrieve_relevant_tables":
            query = action.get("query") or user_question
            top_k = int(action.get("top_k") or settings.schema_top_k)

            try:
                tables = retrieve_relevant_tables(query=query, top_k=top_k)
                schema_context = format_schema_context(tables)

                add_event(
                    events,
                    "retrieve_relevant_tables_result",
                    {
                        "query": query,
                        "tables": tables,
                        "schema_context": schema_context,
                    },
                )

            except Exception as exc:
                add_event(
                    events,
                    "error",
                    {
                        "source": "retrieve_relevant_tables",
                        "message": str(exc),
                    },
                )

        elif intent == "execute_sql":
            raw_sql = action.get("sql", "")
            sql = clean_sql(raw_sql)

            try:
                allowed_tables = _allowed_tables_from_events(events)
                validate_readonly_sql(sql, allowed_tables=allowed_tables)

                rows = execute_readonly_sql(sql)

                add_event(
                    events,
                    "execute_sql_result",
                    {
                        "sql": sql,
                        "rows": rows,
                    },
                )

            except Exception as exc:
                add_event(
                    events,
                    "error",
                    {
                        "source": "execute_sql",
                        "sql": sql,
                        "message": str(exc),
                    },
                )

        elif intent == "request_clarification":
            return {
                "status": "needs_clarification",
                "message": action.get("question", "Can you clarify your question?"),
                "events": events,
            }

        elif intent == "final_answer":
            return {
                "status": "done",
                "answer": action.get("answer", ""),
                "events": events,
            }

        else:
            add_event(
                events,
                "error",
                {
                    "source": "agent",
                    "message": f"Unknown intent: {intent}",
                    "action": action,
                },
            )

    return {
        "status": "max_steps_reached",
        "answer": "The agent reached the maximum number of steps before producing a final answer.",
        "events": events,
    }