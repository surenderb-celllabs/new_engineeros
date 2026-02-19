from langchain_ollama import OllamaEmbeddings, ChatOllama
# from langchain_together import ChatTogether, TogetherEmbeddings
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal



load_dotenv()


class Model:
    def __init__(self):
        pass


    class ChatOllama:
        llama3_1 = ChatOllama(model="llama3.1:8b", base_url="http://183.82.99.107:11434")
        mistral_12b = ChatOllama(model="mistral-nemo:12b", base_url="http://183.82.99.107:11434")
        gpt_oss_20b = ChatOllama(model="gpt-oss:20b", base_url="http://183.82.99.107:11434")

    
    class Gemini:
        gemini3 = ChatGoogleGenerativeAI(model="gemini-3-pro")




    # class ChatTogether:
    #     llama_3_3_70b = ChatTogether(model="meta-llama/Llama-3.3-70B-Instruct-Turbo")
    #     llama_4_scout = ChatTogether(model="meta-llama/Llama-4-Scout-17B-16E-Instruct")


    # class Qwen:
    #     qwen_a22b_instruct = ChatTogether(model="Qwen/Qwen3-235B-A22B-Instruct-2507-tput")
    #     qwen_a3b_thinking = ChatTogether(model="Qwen/Qwen3-Next-80B-A3B-Thinking")


    # class OpenAI:
    #     gpt_oss_20b = ChatTogether(model="OpenAI/gpt-oss-20B")


    class Groq:
        gpt_oss_120b = ChatGroq(model="openai/gpt-oss-120b")
        gpt_oss_20b = ChatGroq(model="openai/gpt-oss-20b")

        llama_scout = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
        llama_31 = ChatGroq(model="llama-3.1-8b-instant")


    class Nvidia:
        gpt_oss_20b = ChatNVIDIA(model="openai/gpt-oss-20b")


    