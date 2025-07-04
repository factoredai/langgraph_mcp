import logging
from enum import StrEnum
from typing import Literal, Union
from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState
from langgraph.types import Command, interrupt
from langgraph.prebuilt import ToolNode
from .settings import settings
from .tools import agent_tools
from .prompts import Prompts
from .state import AgentState

logger = logging.getLogger(__name__)


class Nodes(StrEnum):
    INIT = "init"
    ROUTER = "router"
    ASK_HUMAN = "ask_human"
    AGENT = "agent"
    TOOLS = "tools"
    END = "__end__"


class RoleOutput(BaseModel):
    role: Union[str, None] = Field(description="The role the user is applying for")


class Agent:
    def __init__(self):
        self.llm = init_chat_model(settings.OPENAI_MODEL)
        self.graph = self._create_graph()
        self.pg = Prompts

    def _create_graph(self):
        graph = StateGraph(AgentState, input=MessagesState)  # type: ignore
        graph.add_node(Nodes.INIT, self.init)
        graph.add_node(Nodes.ROUTER, self.router)
        graph.add_node(Nodes.ASK_HUMAN, self.ask_human)
        graph.add_node(Nodes.AGENT, self.agent)
        graph.add_node(Nodes.TOOLS, self.tools)
        graph.set_entry_point(Nodes.INIT)
        return graph.compile()

    def init(self, state: AgentState) -> Command[Literal[Nodes.ROUTER]]:
        return Command(
            goto=Nodes.ROUTER,
            update={"query": state["messages"][-1].content},
        )

    def router(
        self, state: AgentState
    ) -> Command[Literal[Nodes.AGENT, Nodes.ASK_HUMAN]]:
        logger.info("-------------- Routing --------------")
        prompt = self.pg.router(state)
        llm = self.llm.with_structured_output(RoleOutput)
        ai_response: RoleOutput = llm.invoke(prompt)  # type: ignore
        if ai_response.role:
            return Command(goto=Nodes.AGENT, update={"role": ai_response.role})
        return Command(goto=Nodes.ASK_HUMAN)

    def ask_human(self, state: AgentState) -> Command[Literal[Nodes.AGENT]]:
        logger.info("-------------- Asking Human --------------")
        human_role = interrupt("Please provide a role you are interested in applying?")
        query = f"{state['query']}, for the role {human_role}"
        return Command(goto=Nodes.AGENT, update={"query": query, "role": human_role})

    def agent(self, state: AgentState) -> Command[Literal[Nodes.TOOLS, Nodes.END]]:
        logger.info("-------------- Calling Agent --------------")
        llm = self.llm.bind_tools(agent_tools)
        prompt = self.pg.agent(state)
        response = llm.invoke(prompt)
        if response.tool_calls:  # type: ignore
            return Command(goto=Nodes.TOOLS, update={"messages": response})
        return Command(goto=Nodes.END, update={"messages": response})

    def tools(self, state: AgentState) -> Command[Literal[Nodes.AGENT]]:
        logger.info("-------------- Calling Tools --------------")
        tool_node = ToolNode(agent_tools)
        response = tool_node.invoke(state)
        return Command(goto=Nodes.AGENT, update=response)
