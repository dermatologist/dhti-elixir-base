import functools
import re
from kink import inject
from langgraph.graph import END, StateGraph
import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, HumanMessage

@inject
class BaseGraph:
    # Ref 1: https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/multi-agent-collaboration.ipynb
    # Ref 2: https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141
    # * call_tools = tool_node
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    def __init__(self,
                 agents=[], #required
                 edges = [], # [{"from": "agent1", "to": "agent2", "conditional": True}, {"from": "agent2", "to": "agent1", "conditional": True}] #required
                 entry_point="", #required agent_1
                 ends=[], #required but can be empty
                 end_words=[], #required but can be empty
                 nodes = None, #generated
                 workflow = None, #generated
                 router = None, #generated based on edges
                 name = None, #generated
                 recursion_limit=150 #default
    ):
        self.agents = agents
        self.edges = edges
        self.end_words = end_words
        self.nodes = nodes
        self.workflow = workflow
        self.router = router
        self.entry_point = entry_point
        self.ends = ends
        self.recursion_limit = recursion_limit
        self._name = name

    def init_graph(self):
        # We create a workflow that will be used to manage the state of the agents
        if self.workflow is None:
            self.workflow = StateGraph(self.AgentState)
        # We create the nodes for each agent
        if self.nodes is None:
            self.nodes = []
            for agent in self.agents:
                self.nodes.append(self.agent_node(agent))
        # We add the nodes to the workflow
        for node, agent in zip(self.nodes, self.agents):
            self.workflow.add_node(agent.name, node)
        # We set the entry point of the workflow
        self.workflow.set_entry_point(self.entry_point)
        # We set the end points of the workflow
        for end in self.ends:
            self.workflow.add_edge(end, END)
        # We set the router
        if self.router is None:
            self.router = self._router
        # Add  edges
        for edge in self.edges:
            if edge["conditional"]:
                self.workflow.add_conditional_edges(
                    edge["from"],
                    self.router,
                    {"continue": edge["to"], "__end__": END},
                )
            else:
                self.workflow.add_edge(edge["from"], edge["to"])
        self.graph = self.workflow.compile()

    @property
    def name(self):
        if self._name:
            return self._name
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self._class__.__name__).lower()

    @name.setter
    def name(self, value):
        self._name = value

    # Helper function to create a node for a given agent
    @staticmethod
    def create_agent_node(state, agent):
        try:
            result = agent.invoke(state)
        except ValueError as e:
            _result = agent.invoke({"input": state})
            result = _result["input"]["messages"][0]

        if "output" in _result:
            result = ToolMessage(content=_result["output"], tool_call_id="myTool")
        # We convert the agent output into a format that is suitable to append to the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            try:
                result = AIMessage(**result.dict(exclude={"type", "name"}), name=agent.name)
            except Exception as e:
                result = AIMessage(content=result.content, name=agent.name)
        return {
            "messages": [result],
            # Since we have a strict workflow, we can
            # track the sender so we know who to pass to next.
            "sender": agent.name,
        }

    def agent_node(self, agent):
        return functools.partial(self.create_agent_node, agent=agent)

    def _router(self,state) -> Literal["__end__", "continue"]:
        # This is the router
        messages = state["messages"]
        last_message = messages[-1]
        if any([exit.lower() in last_message.content.lower() for exit in self.end_words]):
            return "__end__"
        return "continue"

    def invoke(self, message):
        events = self.graph.stream(
        {
                "messages": [
                    HumanMessage(
                        content=message,
                    )
                ],
            },
            # Maximum number of steps to take in the graph
            {"recursion_limit": self.recursion_limit},
        )
        return events
