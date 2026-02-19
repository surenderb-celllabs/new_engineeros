
from app.phase_5.session_03 import *
from app.phase_5.session_03 import \
    State, node
from app.tools import vectordb, google
        
from langgraph.graph import StateGraph, START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage


class IdeaExpansion:
    def __init__(self, vector_store: Any):
        self.graph_builder = StateGraph(State)
        self.vector_store = vector_store
        self.agent_tools = [
            vectordb.retriver(vector_store=self.vector_store),
        ]
        self._build()


    def _build(self):
        # Node 1: Conversation for Problem Statement & Solution
        self.graph_builder.add_node(
            "FUNC_NON_FUNC_CONVO", 
            node.SystemRequirement(self.agent_tools)
        )
        
        # Node 2: Generate Goals from Conversation
        self.graph_builder.add_node(
            "FUNC_NON_FUNC_DOC", 
            node.SystemDocument(self.agent_tools)
        )


        self.graph_builder.add_node("tool_node", ToolNode(tools=self.agent_tools))
        self.graph_builder.add_node("tool_node_1", ToolNode(tools=self.agent_tools))
        
        self.graph_builder.add_edge("tool_node", "FUNC_NON_FUNC_CONVO")
        
        # Start flow
        self.graph_builder.add_edge(START, "FUNC_NON_FUNC_CONVO")
        
        # Conditional edge: Check conversation phase and completion
        self.graph_builder.add_conditional_edges(
            "FUNC_NON_FUNC_CONVO", 
            self._should_proceed_to_document
        )
        
        
        # Final edge to END
        self.graph_builder.add_conditional_edges("FUNC_NON_FUNC_DOC", self._should_proceed_to_document_1)
        self.graph_builder.add_edge("tool_node_1", "FUNC_NON_FUNC_DOC")
    

    def compile(self):
        checkpointer = InMemorySaver()
        return self.graph_builder.compile(checkpointer=checkpointer)
    

    def _should_proceed_to_document(self, state: State) -> str:
        """
        Determine if conversation is complete and should proceed to goal generation.
        
        Args:
            state: Current state dictionary
            
        Returns:
            Next node to proceed to
        """

        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tool_node"


        if state.get("convo_end", False):
            return "FUNC_NON_FUNC_DOC"
        
        # Continue conversation if not complete
        return END


    def _should_proceed_to_document_1(self, state: State) -> str:
        """
        Determine if conversation is complete and should proceed to goal generation.
        
        Args:
            state: Current state dictionary
            
        Returns:
            Next node to proceed to
        """

        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tool_node"

        
        # Continue conversation if not complete
        return END
