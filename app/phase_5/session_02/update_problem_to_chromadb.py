

file_name = "problem.yaml"
file_path = "app/docs/problem.yaml"

from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_management import load_yaml
from langchain_core.documents import Document
from langchain_ollama.embeddings import OllamaEmbeddings

from langchain_chroma import Chroma

from app import ColoredLogger
logger = ColoredLogger(name="STEP-001")

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest", base_url="http://localhost:11434")
vector_store = Chroma(
    collection_name="test",
    embedding_function=embeddings,
    persist_directory="./new_chroma_db"
)



file_data = load_yaml(file_path)
data_list = [
    Document(
        page_content=f"Problem Statement: {file_data["problem_statement"]}",
        metadata={
            "title": file_name,
            "data": "problem"
        }
    ),
    Document(
        page_content=f"Solution: {file_data["solutions"]}",
        metadata={
            "title": file_name,
            "data": "solution"
        }
    ),
    Document(
        page_content=f"Stakeholders: {file_data["stakeholders"]}",
        metadata={
            "title": file_name,
            "data": "stakeholders"
        }
    )
]

data_list_append = [
    Document(
        page_content=str(goal),
        metadata={
            "title": file_name,
            "data": goal["goal_id"]
        }
    )
    for goal in file_data["goals"]
]

final_list = data_list+data_list_append
logger.debug(f"Final List is {final_list}")
vector_store.add_documents(final_list)


