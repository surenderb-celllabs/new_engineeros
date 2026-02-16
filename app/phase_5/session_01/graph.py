
from app.phase_5.session_01 import *
from app.phase_5.session_01 import \
    State, node
from app.tools import vectordb, google
        
from langgraph.graph import StateGraph, START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
        


class IdeaExpansion:
    def __init__(self, vector_store: Any):
        self.graph_builder = StateGraph(State)
        self.vector_store = vector_store
        self.agent_tools = [
            vectordb.retriver(vector_store=self.vector_store),
            google.search(vector_store=self.vector_store)
        ]
        self._build()


    def _build(self):
        # Node 1: Conversation for Problem Statement & Solution
        self.graph_builder.add_node(
            "PROBLEM_SOLUTION_CONVO", 
            node.ProductRequirement(self.agent_tools)
        )
        
        # Node 2: Generate Goals from Conversation
        self.graph_builder.add_node(
            "PROBLEM_DOCUMENT", 
            node.ProblemDocument(self.agent_tools)
        )
        
        
        # Start flow
        self.graph_builder.add_edge(START, "PROBLEM_SOLUTION_CONVO")
        
        # Conditional edge: Check conversation phase and completion
        self.graph_builder.add_conditional_edges(
            "PROBLEM_SOLUTION_CONVO", 
            self._should_proceed_to_document
        )
        
        
        # Final edge to END
        self.graph_builder.add_edge("PROBLEM_DOCUMENT", END)
    

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
        if state.get("convo_end", False):
            return "PROBLEM_DOCUMENT"
        
        # Continue conversation if not complete
        return END

