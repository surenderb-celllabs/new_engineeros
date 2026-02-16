
from app.phase_5.session_03 import graph as g, State

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from langchain_ollama.embeddings import OllamaEmbeddings

# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

from app import ColoredLogger
logger = ColoredLogger(name="STEP-001")

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest", base_url="http://localhost:11434")
vector_store = Chroma(
    collection_name="test",
    embedding_function=embeddings,
    persist_directory="./new_chroma_db"
)
graph = g.IdeaExpansion(vector_store=vector_store).compile()
checkpointer = InMemorySaver()

pointer = InMemorySaver()


config = {
    "recursion_limit": 50,
    "configurable": {"thread_id": "1"}
}

while True:
    input_msg = input("User: ")
    in_state: State = {
        "messages": [HumanMessage(content=input_msg)],
        "convo_end": False
    }
    # graph.invoke(input=in_state, config=config)


    for mode, chunks, meta in graph.stream(input=in_state, config=config, subgraphs=True, stream_mode=["values"]):
        
        if "resp_type" in meta and meta["resp_type"] == "options":
            continue
        
        # logger.info(f"The mode is {mode}")
        # logger.error(f"The chunks are {chunks}")

        logger.warning(f"AI: {meta["messages"][-1].content}")

    # logger.error(meta)


# {"product_name": "SmartMed Scheduler", "domain": "HealthTech", "description": "An AI-powered platform that automatically schedules patient appointments, sends reminders, and optimizes doctor availability based on historical patterns and patient preferences."}
# {"product_name":"FinSight Ledger","domain":"FinTech","description":"An AI-driven personal finance platform that categorizes transactions, forecasts cash flow, and provides real-time spending insights and savings recommendations."}




