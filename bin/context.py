import json
from typing import Any

def event_to_prompt(event: dict[str, Any]) -> str:
    event_type = event["type"]
    data = event["data"]

    if isinstance(data, str):
        content = data
    else:
        content = json.dumps(data, indent=2, default=str)

    return f"<{event_type}>\n{content}\n</{event_type}>"


def render_events(events: list[dict[str, Any]]) -> str:
    chunks = ["Here is everything that happened so far:\n"]

    for event in events:
        chunks.append(event_to_prompt(event))

    chunks.append("\nWhat is the next step?")

    return "\n\n".join(chunks)


def add_event(events: list[dict[str, Any]], event_type: str, data: Any) -> None:
    events.append(
        {
            "type": event_type,
            "data": data,
        }
    )

