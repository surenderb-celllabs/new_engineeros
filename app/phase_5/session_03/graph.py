
from app.phase_5.session_03 import *
from app.phase_5.session_03 import \
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
    def __init__(self, vector_store: Any, user_stories_ids: List):
        self.user_stories_id = user_stories_ids
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
        self.graph_builder.add_node(
            "FUNC_NON_FUNC_CONVO", 
            node.SystemRequirement(self.agent_tools, user_stories_ids=self.user_stories_id)
        )
        
        # Node 2: Generate Goals from Conversation
        self.graph_builder.add_node(
            "FUNC_NON_FUNC_DOC", 
            node.SystemDocument(self.doc_agents_tools)
        )
        self.graph_builder.add_node(
            "TOOL_MSG_REMOVER",
            self._remove_tool_messages
        )
        self.graph_builder.add_node(
            "FIRST_CONVO",
            self._is_started
        )
        self.graph_builder.add_node(
            "UPDATE_CATEGORY",
            self._update_user_story_category
        )


        self.graph_builder.add_node("tool_node", ToolNode(tools=self.agent_tools))
        self.graph_builder.add_node("tool_node_1", ToolNode(tools=self.doc_agents_tools))
        
        self.graph_builder.add_edge("tool_node", "FUNC_NON_FUNC_CONVO")
        
        # Start flow
        # self.graph_builder.add_edge(START, "FIRST_CONVO")
        # self.graph_builder.add_edge("FIRST_CONVO", "TOOL_MSG_REMOVER")
        self.graph_builder.add_edge(START, "TOOL_MSG_REMOVER")
        self.graph_builder.add_edge("TOOL_MSG_REMOVER", "FUNC_NON_FUNC_CONVO")
        
        # Conditional edge: Check conversation phase and completion
        self.graph_builder.add_conditional_edges(
            "FUNC_NON_FUNC_CONVO", 
            self._should_proceed_to_document
        )
        
        
        # Final edge to END
        self.graph_builder.add_conditional_edges("FUNC_NON_FUNC_DOC", self._should_proceed_to_document_1)
        self.graph_builder.add_edge("tool_node_1", "FUNC_NON_FUNC_DOC")
        self.graph_builder.add_edge("UPDATE_CATEGORY", "TOOL_MSG_REMOVER")
    


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
    
    def _is_started(self, state: State) -> State:
        if "user_story_category_topics" not in state:
            new_state = state.copy()
            new_state["total_frs"] = 0
            new_state["total_nfrs"] = 0

            us_categorized = self._get_user_stories("app/docs/user_stories.yaml")
            new_state["user_story_category_topics"] = us_categorized
            new_state["user_stories_category_list"] = list(us_categorized.keys())
            new_state["user_story_category_total"] = len(new_state["user_story_category_topics"])
            new_state["user_story_category_current"] = 0
            new_state["user_story_category"] = us_categorized[new_state["user_stories_category_list"][new_state["user_story_category_current"]]]

            return new_state
        
        return state
    
    
    def _check_if_end(self, state):
        if (state["user_story_category_current"] + 1) == state["user_story_category_total"]:
            return END
        
        return "UPDATE_CATEGORY"

    def _update_user_story_category(self, state: State) -> State:
        
        return_state = state.copy()
        return_state["user_story_category_current"] = state["user_story_category_current"] + 1
        return_state["user_story_category"] = return_state["user_story_category_topics"][state["user_stories_category_list"][state["user_story_category_current"]]]


        return return_state



    def _get_user_stories(self, path: str):
        user_stories_list = load_yaml(file_name=path)["user_stories"]

        categories_dict = {}

        for story in user_stories_list:
            if not story["category"] in categories_dict:
                categories_dict[story["category"]] = []

            categories_dict[story["category"]].append(story["user_story_id"])

        
        return categories_dict



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
            return "tool_node_1"

        # elif state["convo_end"]:
        #     return self._check_if_end(state=state)

        
        # Continue conversation if not complete
        # return self._check_if_end(state=state)
        return END
