from typing import List, Dict, Any, Optional, TypedDict

from typing import TypedDict, Annotated, List, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage



from pathlib import Path
STEP_PATH = str(Path(__file__).parent.resolve())

from enum import Enum

class ResponseType(Enum):
    MESSAGE = "message"
    STATUS = "status"
    DOCUMENT = "document"
    APPROVAL = "approval"
    ANSWER_SUGGESTION = "options"
    ERROR = "error"
    NONE = "none"


class DocumentDetails(TypedDict):
    document_name: str
    document_type: str

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    resp_type: str
    resp_data: DocumentDetails
    convo_end: bool
    
    # Conversation tracking
    conversation_phase: str
    start_convo_index: int
    

