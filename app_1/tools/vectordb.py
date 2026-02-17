

import json, requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool, create_retriever_tool
from langchain_core.documents import Document
from langchain_core.messages import ToolMessage

from app.tools import STEP_PATH

from dotenv import load_dotenv
load_dotenv()

from utils.colored_logger import get_logger
logger = get_logger("Tools >> VectorDB")



def retriver(vector_store):

    @tool
    def retrive_tool(query: str, count: int = 30, tool_call_id: str = None):
        """
        A Tool used to retrive the content from the vector db based on the user
        query.
        
        :param query: Data to be extracted.
        :type query: str
        :param count: No. of source data to be extracted
        :type count: int
        :param tool_call_id: Id of the Tool Call
        :type tool_call_id: str
        """
        if count > 30:
            count = 30

        retrive_tool.name = "retrive_tool"
        logger.debug(f"Retrieving for the query: {query}")
        docs = vector_store.similarity_search(query, k=count)
        return_data = [doc.page_content for doc in docs]
        logger.debug(f"Retrieved data is {len(return_data)}")

        # return {
        #     "messages": [
        #         ToolMessage(
        #             content=str(return_data), 
        #             tool_call_id=tool_call_id,
        #             tool_name="retrive_tool"
        #         )
        #     ]
        # }
        return f"Retrieved data is {return_data}"

    return retrive_tool



def store(vector_store):
    @tool
    def store_tool(content: str, title: str):
        """
        A tool to store the content to the VectorDB using the given title.
        
        :param content: Content to be stored in the VectorDB
        :type content: str
        :param title: Title of the content
        :type title: str
        """
        store_tool.name = "store_tool"
        logger.debug(f"Storing the content for title: {title}")
        documents = []
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". "]
        )
        content_chunks = text_splitter.split_text(content)
        for i, chunk in enumerate(content_chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "title": title,
                        "chunk_id": i
                    }
                )
            )
        
        if len(documents) > 0:
            vector_store.add_documents(documents)

        file_name = f"{STEP_PATH}/save_docs/{title}"
        with open(file=file_name, mode="w+") as file:
            file.write(content)

        return f"Added {title} to the VectorDB"


    return store_tool
