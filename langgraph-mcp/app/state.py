from langgraph.graph import MessagesState


class AgentState(MessagesState):
    query: str
    role: str
