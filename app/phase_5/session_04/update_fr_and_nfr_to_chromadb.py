

file_name = "func_nonfunc.yaml"
file_path = "app/docs/func_nonfunc.yaml"

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


def md_style_list(data: list) -> str:
    return_str = ""
    for i in data:
        return_str += i
        return_str += "\n"

def comma_saperated_list(data: list) -> str:
    return ", ".join(data)

def return_md_format(id: str, data: dict) -> str:
    doc_style = """# {fr_id}
{description}
### Priority: {priority}
### Related User Stories: {user_stories}
## Acceptance Criteria:
{acceptance_criteria}
## Edge Cases
{edge_cases}
## Dependencies
{dependencies}
## Related Goals:
{derived_from}
"""
    return doc_style.format(
        fr_id = id,
        description = data["description"],
        priority = data["priority"],
        user_stories = comma_saperated_list(data["related_usecase"]),
        acceptance_criteria = md_style_list(data["acceptance_criteria"]),
        edge_cases = md_style_list(data["edge_cases"]),
        dependencies = comma_saperated_list(data["dependencies"]),
        derived_from = comma_saperated_list(data["derived_from"])
    )



dict_data = {
  "description": "The system shall allow a trip owner to create a trip with a unique name, start/end dates, optional description, and optional version tag (user-supplied or default \"v1\"). The trip creation must be atomic and persist all trip metadata in the data store.",
  "priority": "High",
  "related_usecase": [
    "USER_STORY-0001"
  ],
  "acceptance_criteria": [
    "The trip appears in the owner’s trip list immediately after creation.",
    "Duplicate trip names for the same user are rejected with a clear error.",
    "The created trip’s version tag is stored and displayed in the UI."
  ],
  "edge_cases": [
    "Attempting to create a trip with a past end date – should fail validation.",
    "Creating a trip while offline – should queue and sync upon reconnect."
  ],
  "dependencies": [],
  "derived_from": [
    "GOAL-001"
  ]
}
print(return_md_format("FR-0001", dict_data))


# file_data = load_yaml(file_path)

# data_list_append = [
#     Document(
#         page_content=return_md_format(fr_content),
#         metadata={
#             "title": file_name,
#             "data": fr_id
#         }
#     )
#     for fr_id, fr_content in file_data["functional_requirements"]
# ]

# final_list = data_list_append
# logger.debug(f"Final List is {final_list}")
# vector_store.add_documents(final_list)


