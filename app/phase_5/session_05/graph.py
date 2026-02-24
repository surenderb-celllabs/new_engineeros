
from app.phase_5.session_05 import *
from app.phase_5.session_05 import \
    State, node
from app.tools import vectordb, google
from utils.file_management import load_yaml


from langgraph.graph import StateGraph, START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage
from langchain_core.messages import ToolMessage, RemoveMessage

from app import ColoredLogger
logger = ColoredLogger("Graph")

class IdeaExpansion:
    def __init__(self, vector_store: Any):
        self.graph_builder = StateGraph(State)
        self.vector_store = vector_store
        self.agent_tools = [
            # vectordb.retriver(vector_store=self.vector_store),
            node.Tools.user_story()
        ]
        self.doc_agents_tools = [
            vectordb.retriver(vector_store=self.vector_store),
            node.Tools.user_story()
        ]
        self._build()


    def _build(self):
        # Node 1: Conversation for Problem Statement & Solution
        self.graph_builder.add_node("CONVO", node.TechnologyStackConvo(agent_tools=self.agent_tools))
        self.graph_builder.add_node("DOCUMENT", node.TechnologyStackDocument(agent_tools=self.agent_tools))
       
        self.graph_builder.add_node(
            "TOOL_MSG_REMOVER",
            self._remove_tool_messages
        )
        # Start flow
        # self.graph_builder.add_edge(START, "FIRST_CONVO")
        # self.graph_builder.add_edge("FIRST_CONVO", "TOOL_MSG_REMOVER")
        self.graph_builder.add_edge(START, "TOOL_MSG_REMOVER")
        self.graph_builder.add_edge("TOOL_MSG_REMOVER", "CONVO")
        
        # Conditional edge: Check conversation phase and completion
        self.graph_builder.add_conditional_edges(
            "CONVO", 
            self._should_proceed_to_document
        )
        
        self.graph_builder.add_edge("DOCUMENT", END)



    def compile(self):
        checkpointer = InMemorySaver()
        return self.graph_builder.compile(checkpointer=checkpointer)
    

    def _remove_tool_messages(self, state: State) -> State:
        for msg in state["messages"]:
            if isinstance(msg, ToolMessage):
                RemoveMessage(msg.id)

        remove_ids = [
            msg.id
            for msg in state["messages"]
            if isinstance(msg, ToolMessage)
        ]

        return_state = state.copy()
        return_state["messages"] = [
            RemoveMessage(msg_id)
            for msg_id in remove_ids
        ]

        
        logger.debug(return_state)
        return return_state
    
    
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
            return "DOCUMENT"
        
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
            return "tool_node_1"

        # elif state["convo_end"]:
        #     return self._check_if_end(state=state)

        
        # Continue conversation if not complete
        # return self._check_if_end(state=state)
        return END
