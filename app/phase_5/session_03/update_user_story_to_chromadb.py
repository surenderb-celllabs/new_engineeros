

file_name = "user_stories.yaml"
file_path = "app/docs/user_stories.yaml"

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

data_list_append = [
    Document(
        page_content=str(user_story),
        metadata={
            "title": file_name,
            "data": user_story["user_story_id"]
        }
    )
    for user_story in file_data["user_stories"]
]

final_list = data_list_append
logger.debug(f"Final List is {final_list}")
vector_store.add_documents(final_list)


