
from app.phase_5.session_03 import graph as g, State

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from langchain_ollama.embeddings import OllamaEmbeddings

# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from utils.file_management import load_yaml

from app import ColoredLogger
logger = ColoredLogger(name="STEP-001")

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest", base_url="http://localhost:11434")
vector_store = Chroma(
    collection_name="test",
    embedding_function=embeddings,
    persist_directory="./new_chroma_db"
)

# in_state: State = {
#     "messages": [HumanMessage(content="hi")],
#     "convo_end": False
# }
# graph.invoke(in_state, config=config)

path = "app/docs/user_stories.yaml"
user_stories_list = load_yaml(file_name=path)["user_stories"]
categories_dict = {}
for story in user_stories_list:
    if not user_stories_list[story]["category"] in categories_dict:
        categories_dict[user_stories_list[story]["category"]] = []

    categories_dict[user_stories_list[story]["category"]].append(story)
# print(list(categories_dict.keys()))
# print(categories_dict)

categories = [
    'Core Functionality', 'Access Control', 'AI Features', 'Export Functionality', 
    'Offline Functionality', 'Data Integrity', 'Error Handling', 'Security'
]


category_index = 7


fn_data = load_yaml("app/docs/func_nonfunc.yaml")
# print(len(fn_data["functional_requirements"]), len(fn_data["non_functional_requirements"]))




graph = g.IdeaExpansion(
    vector_store=vector_store, 
    user_stories_ids=categories_dict[categories[category_index]]
).compile()
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
        "convo_end": False,

        "us_ids": categories_dict[categories[category_index]],
        "us_category": categories[category_index],

        "total_frs": len(fn_data["functional_requirements"])+1,
        "total_nfrs": len(fn_data["non_functional_requirements"])+1
    }
    # graph.invoke(input=in_state, config=config)


    for mode, chunks, meta in graph.stream(input=in_state, config=config, subgraphs=True, stream_mode=["values"]):
        
        if "resp_type" in meta and meta["resp_type"] == "options":
            continue
        
        # logger.info(f"The mode is {mode}")
        # logger.error(f"The chunks are {chunks}")

        # logger.warning(f"AI: {meta["messages"][-1].content}")

    # logger.error(meta)


# {"product_name": "SmartMed Scheduler", "domain": "HealthTech", "description": "An AI-powered platform that automatically schedules patient appointments, sends reminders, and optimizes doctor availability based on historical patterns and patient preferences."}
# {"product_name":"FinSight Ledger","domain":"FinTech","description":"An AI-driven personal finance platform that categorizes transactions, forecasts cash flow, and provides real-time spending insights and savings recommendations."}




