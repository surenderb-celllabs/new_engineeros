
from app.phase_5.session_04 import graph as g, State

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




# files = {
#     "func_nonfunc.yaml": "/home/surender/surender/celllabs/new_engineeros/app/phase_5/func_nonfunc.yaml",
#     "problem.yaml": "/home/surender/surender/celllabs/new_engineeros/app/phase_5/problem.yaml",
#     "user_stories.yaml": "/home/surender/surender/celllabs/new_engineeros/app/phase_5/user_stories.yaml"
# }

# for i in list(files.keys()):
#     from langchain_text_splitters import RecursiveCharacterTextSplitter
#     from utils.file_management import load_yaml
#     from langchain_core.documents import Document
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size = 500,
#         chunk_overlap = 50,
#         separators=["\n\n", "\n", "."]
#     )
#     chunks = text_splitter.split_text(str(load_yaml(files[i])))
#     document = []
#     for j, chunks in enumerate(chunks):
#         document.append(Document(
#             page_content=chunks,
#             metadata = {
#                 "title": i,
#                 "chunk_id": j
#             }
#         ))
    
#     if len(document) > 0:
#         vector_store.add_documents(documents=document)
#         print("Added File to the Vector DB")





graph = g.IdeaExpansion(vector_store=vector_store).compile()
checkpointer = InMemorySaver()

pointer = InMemorySaver()


config = {
    "recursion_limit": 50,
    "configurable": {"thread_id": "1"}
}

in_state: State = {
    "messages": [HumanMessage(content="hi")],
    "convo_end": False
}
graph.invoke(in_state, config=config)

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

        # logger.warning(f"AI: {meta["messages"][-1].content}")

    # logger.error(meta)


# # {"product_name": "SmartMed Scheduler", "domain": "HealthTech", "description": "An AI-powered platform that automatically schedules patient appointments, sends reminders, and optimizes doctor availability based on historical patterns and patient preferences."}
# # {"product_name":"FinSight Ledger","domain":"FinTech","description":"An AI-driven personal finance platform that categorizes transactions, forecasts cash flow, and provides real-time spending insights and savings recommendations."}




