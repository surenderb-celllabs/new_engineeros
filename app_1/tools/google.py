
import json, requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_core.messages import ToolMessage

from app.tools import STEP_PATH

from dotenv import load_dotenv
load_dotenv()

from utils.colored_logger import get_logger
logger = get_logger("Tests >> Tools")

from langgraph.config import get_stream_writer



def search(vector_store):

    @tool
    def search_tool(query: str, no_of_results: int = 10, tool_call_id: str = None):
        """
        Use this tool to get the contents of the top 10 webistes of the google
        search. This returns the snippets of the websites and the content of the
        websites are stored in the vector db which can be used further·.
        
        :param query: The query that needs to be searched in the google
        :type query: str
        :param no_of_results: The number of websites to be searched max of 10
        :type no_of_results: int 
        :param tool_call_id: Id of the Tool Call
        :type tool_call_id: str
        """
        search_tool.name = "google_search"

        writer = get_stream_writer()

        # if no_of_results > 10:
            # no_of_results = 10

        if no_of_results > 3:
            no_of_results = 1
        elif no_of_results == 0:
            no_of_results = 1

        URL = "https://google.serper.dev/search"

        payload = json.dumps({
            "q": query,
            "location": "Hyderabad, Telangana, India",
            "gl": "in"
        })
        headers = {
            'X-API-KEY': '6fdacbbbb34ca94b77a58f6848e31f7a3cd4a11b',
            'Content-Type': 'application/json'
        }

        writer({"type": "web_search" ,"url": query})

        response = requests.request(method="POST", url=URL, 
                                    headers=headers, data=payload)
        
        urls = response.json()["organic"][:no_of_results]
        # logger.debug(f"The URLs are: \n {urls}")
        
        google_search_result = []
        documents = []
        summary_list = []
        for url in urls:
            logger.debug(f"Getting the content for URL: {url}")
            writer({"type": "web_search" ,"url": url["link"]})
            content = url_content(url["link"])
            data = {}
            if content != "":
                # url["snippet"] = content
                data["url"] = url["link"]
                data["title"] = url["title"]
                data["content"] = content
                # documents.append(
                #     Document(page_content=content, 
                #              metadata={"title": str(url["title"])})
                # )

                from app.common_nodes import documentation
                doc_content = documentation.generate(content=content)
                if doc_content == "":
                    continue
                title, summary = documentation.summary_title_generator(content=content)

                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=800,
                    chunk_overlap=150,
                    separators=["\n\n", "\n", ". "]
                )
                content_chunks = text_splitter.split_text(doc_content)
                for i, chunk in enumerate(content_chunks):
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "title": str(url["title"]),
                                "source_url": str(url["link"]),
                                "chunk_id": i
                            }
                        )
                    )

                new_path = f"{STEP_PATH}/2026-01-07-tool_docs_careflow/{title}"
                with open(new_path, mode="w+") as file:
                    file.write(doc_content)
                
                summary_list.append(summary)

            google_search_result.append(data)
            # logger.debug(f"{content} \n\n")
        if len(documents) != 0:
            vector_store.add_documents(documents)
            logger.warning(f"Added {len(documents)} Documents to the Vector DB")
       
        # return f"Added {len(documents)} Documents with summary of them {summary_list}"
        return f"Search Details for query {query} are added to the VectorDB, you can query from there"       

    def url_content(url: str) -> str:
        try:
            html = requests.get(url=url).text
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()

        except Exception as e:
            logger.error("Failed to get URL: {e}")
            return ""

    return search_tool