import functools
from kink import inject
from langgraph.graph import END, StateGraph
import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, HumanMessage
from langgraph.prebuilt import ToolNode

@inject
class BaseGraph:
    # Ref 1: https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/multi-agent-collaboration.ipynb
    # Ref 2: https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141
    # * call_tools = tool_node
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    def __init__(self,
                 agents=None, #required
                 tools = None, #required
                 edges = None, # {"from": "agent1", "to": "agent2", "contitional": True} #required
                 entry_point=None, #required
                 ends=None, #required
                 nodes = None, #generated
                 workflow = None, #generated
                 router = None, #generated based on edges
                 recursion_limit=150 #default
    ):
        self._agents = agents
        self._tools = tools
        self._edges = edges
        self._nodes = nodes
        self._workflow = workflow
        self._router = router
        self._entry_point = entry_point
        self._ends = ends
        self._recursion_limit = recursion_limit
        self.init_graph()

    def init_graph(self):
        # We create a workflow that will be used to manage the state of the agents
        if self._workflow is None:
            self._workflow = StateGraph(self.AgentState)
        # We create the nodes for each agent
        if self._nodes is None:
            self._nodes = []
            for agent in self._agents:
                self._nodes.append(self.agent_node(agent))
        # We add the nodes to the workflow
        for node in self._nodes:
            self._workflow.add_node(node.name, node)
        # We set the tool node
        self.tool_node = ToolNode(self._tools)
        self._workflow.add_node("tool_node", self.tool_node)
        # We set the entry point of the workflow
        self._workflow.set_entry_point(self._entry_point)
        # We set the end points of the workflow
        for end in self._ends:
            self._workflow.add_edge(end, END)
        # We set the router
        if self._router is None:
            self._router = self.router
        # Add  edges
        for edge in self._edges:
            if edge["contitional"]:
                self._workflow.add_conditional_edges(
                    edge["from"],
                    self._router,
                    {"continue": edge["to"], "call_tool": "tool_node", "__end__": END},
                )
            else:
                self._workflow.add_edge(edge["from"], edge["to"])
        _call_tool_edges = {}
        for agent in self._agents:
            _call_tool_edges[agent.name] = agent.name
        self._workflow.add_conditional_edges(
            "tool_node",
            # Each agent node updates the 'sender' field
            # the tool calling node does not, meaning
            # this edge will route back to the original agent
            # who invoked the tool
            lambda x: x["sender"],
            _call_tool_edges,
        )
        self._graph = self._workflow.compile()


    # Helper function to create a node for a given agent
    @staticmethod
    def create_agent_node(state, agent):
        result = agent.invoke(state)
        # We convert the agent output into a format that is suitable to append to the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=agent.name)
        return {
            "messages": [result],
            # Since we have a strict workflow, we can
            # track the sender so we know who to pass to next.
            "sender": agent.name,
        }

    def agent_node(self, agent):
        return functools.partial(self.create_agent_node, agent=agent, name = agent.name)

    def router(self,state) -> Literal["call_tool", "__end__", "continue"]:
        # This is the router
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            # The previous agent is invoking a tool
            return "call_tool"
        if "FINAL ANSWER" in last_message.content:
            # Any agent decided the work is done
            return "__end__"
        return "continue"

    def invoke(self, message):
        events = self._graph.stream(
        {
                "messages": [
                    HumanMessage(
                        content=message,
                    )
                ],
            },
            # Maximum number of steps to take in the graph
            {"recursion_limit": self._recursion_limit},
        )
        return events