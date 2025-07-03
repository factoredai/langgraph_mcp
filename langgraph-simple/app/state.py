from typing import TypedDict


class InputState(TypedDict):
    query: str


class AgentState(InputState):
    role: str
